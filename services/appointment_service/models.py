from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

from common.constants import AppointmentStatus

db = SQLAlchemy()


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, nullable=False, index=True)
    doctor_id = db.Column(db.Integer, nullable=False, index=True)
    appointment_datetime = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default=AppointmentStatus.SCHEDULED)
    chief_complaint = db.Column(db.String(255))
    symptoms = db.Column(db.Text)
    notes = db.Column(db.Text)
    consultation_type = db.Column(db.String(20))
    duration_minutes = db.Column(db.Integer, default=30)
    appointment_type = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self, patient_name: str | None = None, doctor_name: str | None = None) -> dict:
        return {
            "id": self.id,
            "patientId": self.patient_id,
            "patientName": patient_name,
            "doctorId": self.doctor_id,
            "doctorName": doctor_name,
            "appointmentDateTime": self.appointment_datetime.isoformat() if self.appointment_datetime else None,
            "status": self.status,
            "chiefComplaint": self.chief_complaint,
            "symptoms": self.symptoms,
            "notes": self.notes,
            "consultationType": self.consultation_type,
            "durationMinutes": self.duration_minutes,
            "appointmentType": self.appointment_type,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
