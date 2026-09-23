import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from flask import Flask, request

from common.cache import cached, evict
from common.constants import AppointmentStatus
from common.exceptions import BusinessException, ResourceNotFoundException, register_error_handlers
from common.jwt_utils import token_required
from common.resilience import event_publisher
from common.responses import success

from services.appointment_service.config import Config
from services.appointment_service.models import db, Appointment


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _validate_doctor_availability(doctor_id: int, appointment_time: datetime):
    day_start = appointment_time.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    day_count = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_datetime >= day_start,
        Appointment.appointment_datetime < day_end,
        Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]),
    ).count()

    if day_count >= Config.MAX_APPOINTMENTS_PER_DOCTOR_PER_DAY:
        raise BusinessException("Doctor schedule is full for this day", "SCHEDULE_FULL")

    window = timedelta(minutes=Config.CONFLICT_WINDOW_MINUTES)
    conflict = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_datetime >= appointment_time - window,
        Appointment.appointment_datetime <= appointment_time + window,
        Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]),
    ).first()

    if conflict:
        raise BusinessException("Doctor has a conflicting appointment at this time", "TIME_CONFLICT")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    register_error_handlers(app)

    with app.app_context():
        # Allow the process to start even if DB is briefly unreachable
        # (RDS schema bootstrap, SG propagation, etc.). Probes keep the
        # pod out of service until create_all has succeeded at least once.
        try:
            db.create_all()
        except Exception as exc:
            app.logger.warning("db.create_all() deferred: %s", exc)

    @app.post("/api/appointments")
    @token_required
    def create_appointment():
        data = request.get_json(force=True)
        appointment_time = _parse_datetime(data["appointmentDateTime"])

        if appointment_time <= datetime.now():
            raise BusinessException("Appointment must be in the future", "INVALID_TIME")

        _validate_doctor_availability(data["doctorId"], appointment_time)

        appointment = Appointment(
            patient_id=data["patientId"],
            doctor_id=data["doctorId"],
            appointment_datetime=appointment_time,
            status=AppointmentStatus.SCHEDULED,
            chief_complaint=data.get("chiefComplaint"),
            symptoms=data.get("symptoms"),
            notes=data.get("notes"),
            consultation_type=data.get("consultationType"),
            duration_minutes=data.get("durationMinutes", 30),
            appointment_type=data.get("appointmentType"),
        )
        db.session.add(appointment)
        db.session.commit()

        evict("doctor_appointments", appointment.doctor_id)

        event_publisher.publish("appointment-events", appointment.id, {
            "appointmentId": appointment.id, "patientId": appointment.patient_id,
            "doctorId": appointment.doctor_id,
            "appointmentDateTime": appointment.appointment_datetime.isoformat(),
            "status": appointment.status, "eventType": "APPOINTMENT_CREATED",
        })

        return success(appointment.to_dict(), "Appointment created successfully", 201)

    @app.get("/api/appointments/<int:appointment_id>")
    @token_required
    def get_appointment(appointment_id):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise ResourceNotFoundException("Appointment", "id", appointment_id)
        return success(appointment.to_dict())

    @app.get("/api/appointments/patient/<int:patient_id>")
    @token_required
    def get_patient_appointments(patient_id):
        appointments = Appointment.query.filter_by(patient_id=patient_id).all()
        return success([a.to_dict() for a in appointments])

    @app.get("/api/appointments/doctor/<int:doctor_id>")
    @token_required
    def get_doctor_appointments(doctor_id):
        @cached("doctor_appointments", ttl_seconds=60)
        def _load(d_id):
            appointments = Appointment.query.filter_by(doctor_id=d_id).all()
            return [a.to_dict() for a in appointments]
        return success(_load(doctor_id))

    @app.get("/api/appointments/doctor/<int:doctor_id>/range")
    @token_required
    def get_doctor_appointments_by_range(doctor_id):
        start = _parse_datetime(request.args["start"])
        end = _parse_datetime(request.args["end"])
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_datetime >= start,
            Appointment.appointment_datetime <= end,
        ).all()
        return success([a.to_dict() for a in appointments])

    @app.patch("/api/appointments/<int:appointment_id>/status")
    @token_required
    def update_status(appointment_id):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise ResourceNotFoundException("Appointment", "id", appointment_id)

        new_status = request.args.get("status") or request.get_json(silent=True, force=True).get("status")
        if new_status not in AppointmentStatus.ALL:
            raise BusinessException(f"Invalid status: {new_status}", "INVALID_STATUS")

        old_status = appointment.status
        appointment.status = new_status
        db.session.commit()

        evict("doctor_appointments", appointment.doctor_id)

        event_publisher.publish("appointment-events", appointment.id, {
            "appointmentId": appointment.id, "oldStatus": old_status, "newStatus": new_status,
            "eventType": "APPOINTMENT_STATUS_CHANGED",
        })

        return success(appointment.to_dict(), "Status updated successfully")

    @app.delete("/api/appointments/<int:appointment_id>")
    @token_required
    def cancel_appointment(appointment_id):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise ResourceNotFoundException("Appointment", "id", appointment_id)

        if appointment.status == AppointmentStatus.COMPLETED:
            raise BusinessException("Cannot cancel completed appointment", "INVALID_STATUS")

        reason = request.args.get("reason", "Not specified")
        appointment.status = AppointmentStatus.CANCELLED
        appointment.notes = f"{appointment.notes or ''}\nCancellation Reason: {reason}".strip()
        db.session.commit()

        evict("doctor_appointments", appointment.doctor_id)

        event_publisher.publish("appointment-events", appointment.id, {
            "appointmentId": appointment.id, "reason": reason, "eventType": "APPOINTMENT_CANCELLED",
        })

        return success(None, "Appointment cancelled successfully")

    @app.get("/actuator/health")
    def health():
        return success({"status": "UP", "service": Config.SERVICE_NAME})

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=Config.SERVICE_PORT, debug=True)
