import json
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    specialization = db.Column(db.String(100), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    qualification = db.Column(db.String(150))
    experience_years = db.Column(db.Integer)
    department = db.Column(db.String(100))
    bio = db.Column(db.Text)
    consultation_fee = db.Column(db.Float)
    available_from = db.Column(db.String(8))   # stored HH:MM:SS for simplicity
    available_to = db.Column(db.String(8))
    working_days = db.Column(db.Text)           # JSON-encoded list
    room_number = db.Column(db.String(20))
    available_for_telemedicine = db.Column(db.Boolean, default=False)
    max_patients_per_day = db.Column(db.Integer, default=20)
    active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self, user: dict | None = None) -> dict:
        result = {
            "id": self.id,
            "userId": self.user_id,
            "specialization": self.specialization,
            "licenseNumber": self.license_number,
            "qualification": self.qualification,
            "experienceYears": self.experience_years,
            "department": self.department,
            "bio": self.bio,
            "consultationFee": self.consultation_fee,
            "availableFrom": self.available_from,
            "availableTo": self.available_to,
            "workingDays": json.loads(self.working_days) if self.working_days else [],
            "roomNumber": self.room_number,
            "availableForTelemedicine": self.available_for_telemedicine,
            "maxPatientsPerDay": self.max_patients_per_day,
            "active": self.active,
            "doctorName": None,
            "email": None,
            "phoneNumber": None,
        }
        if user:
            result["doctorName"] = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
            result["email"] = user.get("email")
            result["phoneNumber"] = user.get("phoneNumber")
        return result
