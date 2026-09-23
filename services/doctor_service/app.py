import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import pybreaker
import requests
from flask import Flask, request, g

from common.cache import cached, evict
from common.exceptions import BusinessException, ResourceNotFoundException, register_error_handlers
from common.jwt_utils import token_required
from common.resilience import build_breaker, event_publisher
from common.responses import success

from services.doctor_service.config import Config
from services.doctor_service.models import db, Doctor

user_service_breaker = build_breaker("user-service-client", fail_max=5, reset_timeout=30)


@user_service_breaker
def _fetch_user(user_id: int) -> dict | None:
    resp = requests.get(f"{Config.USER_SERVICE_URL}/api/users/{user_id}",
                         headers={"Authorization": request.headers.get("Authorization", "")},
                         timeout=3)
    resp.raise_for_status()
    return resp.json().get("data")


def fetch_user_safe(user_id: int) -> dict | None:
    """Circuit-breaker-protected call to user-service with graceful fallback."""
    try:
        return _fetch_user(user_id)
    except (pybreaker.CircuitBreakerError, requests.RequestException):
        return None  # Fallback: doctor data still returned, just without name/email


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

    @app.post("/api/doctors")
    @token_required
    def create_doctor():
        data = request.get_json(force=True)

        if Doctor.query.filter_by(license_number=data["licenseNumber"]).first():
            raise BusinessException("License number already exists", "LICENSE_EXISTS")

        user = fetch_user_safe(data["userId"])
        if user is None:
            raise ResourceNotFoundException("User", "id", data["userId"])

        doctor = Doctor(
            user_id=data["userId"],
            specialization=data["specialization"],
            license_number=data["licenseNumber"],
            qualification=data.get("qualification"),
            experience_years=data.get("experienceYears"),
            department=data.get("department"),
            bio=data.get("bio"),
            consultation_fee=data.get("consultationFee"),
            available_from=data.get("availableFrom"),
            available_to=data.get("availableTo"),
            working_days=json.dumps(data.get("workingDays", [])),
            room_number=data.get("roomNumber"),
            available_for_telemedicine=data.get("availableForTelemedicine", False),
            max_patients_per_day=data.get("maxPatientsPerDay", 20),
        )
        db.session.add(doctor)
        db.session.commit()

        evict("doctors_by_specialization")
        evict("doctors_by_department")

        event_publisher.publish("doctor-events", doctor.id, {
            "doctorId": doctor.id, "userId": doctor.user_id,
            "specialization": doctor.specialization, "eventType": "DOCTOR_CREATED",
        })

        return success(doctor.to_dict(user), "Doctor profile created successfully", 201)

    @app.get("/api/doctors/<int:doctor_id>")
    @token_required
    def get_doctor(doctor_id):
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ResourceNotFoundException("Doctor", "id", doctor_id)
        user = fetch_user_safe(doctor.user_id)
        return success(doctor.to_dict(user))

    @app.get("/api/doctors/user/<int:user_id>")
    @token_required
    def get_doctor_by_user_id(user_id):
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        if not doctor:
            raise ResourceNotFoundException("Doctor", "userId", user_id)
        user = fetch_user_safe(doctor.user_id)
        return success(doctor.to_dict(user))

    @app.get("/api/doctors/specialization/<string:specialization>")
    @token_required
    def get_doctors_by_specialization(specialization):
        @cached("doctors_by_specialization", ttl_seconds=180)
        def _load(spec):
            doctors = Doctor.query.filter_by(specialization=spec, active=True).all()
            return [d.to_dict(fetch_user_safe(d.user_id)) for d in doctors]
        return success(_load(specialization))

    @app.get("/api/doctors/department/<string:department>")
    @token_required
    def get_doctors_by_department(department):
        @cached("doctors_by_department", ttl_seconds=180)
        def _load(dept):
            doctors = Doctor.query.filter_by(department=dept).all()
            return [d.to_dict(fetch_user_safe(d.user_id)) for d in doctors]
        return success(_load(department))

    @app.get("/api/doctors/telemedicine")
    @token_required
    def get_telemedicine_doctors():
        doctors = Doctor.query.filter_by(available_for_telemedicine=True, active=True).all()
        return success([d.to_dict(fetch_user_safe(d.user_id)) for d in doctors])

    @app.get("/api/doctors/active")
    @token_required
    def get_active_doctors():
        doctors = Doctor.query.filter_by(active=True).all()
        return success([d.to_dict(fetch_user_safe(d.user_id)) for d in doctors])

    @app.put("/api/doctors/<int:doctor_id>")
    @token_required
    def update_doctor(doctor_id):
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ResourceNotFoundException("Doctor", "id", doctor_id)

        data = request.get_json(force=True)
        for field, attr in [
            ("specialization", "specialization"), ("qualification", "qualification"),
            ("experienceYears", "experience_years"), ("department", "department"),
            ("bio", "bio"), ("consultationFee", "consultation_fee"),
            ("availableFrom", "available_from"), ("availableTo", "available_to"),
            ("roomNumber", "room_number"),
            ("availableForTelemedicine", "available_for_telemedicine"),
            ("maxPatientsPerDay", "max_patients_per_day"),
        ]:
            if field in data:
                setattr(doctor, attr, data[field])
        if "workingDays" in data:
            doctor.working_days = json.dumps(data["workingDays"])

        db.session.commit()
        evict("doctors_by_specialization")
        evict("doctors_by_department")

        return success(doctor.to_dict(fetch_user_safe(doctor.user_id)), "Doctor updated successfully")

    @app.delete("/api/doctors/<int:doctor_id>")
    @token_required
    def deactivate_doctor(doctor_id):
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ResourceNotFoundException("Doctor", "id", doctor_id)
        doctor.active = False
        db.session.commit()
        return success(None, "Doctor deactivated successfully")

    @app.get("/actuator/health")
    def health():
        return success({"status": "UP", "service": Config.SERVICE_NAME})

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=Config.SERVICE_PORT, debug=True)
