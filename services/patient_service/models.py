from datetime import date, datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    height = db.Column(db.Float)   # cm
    weight = db.Column(db.Float)   # kg
    allergies = db.Column(db.Text)
    chronic_diseases = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_relation = db.Column(db.String(50))
    address = db.Column(db.Text)
    city = db.Column(db.String(80))
    state = db.Column(db.String(80))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(80))
    insurance_provider = db.Column(db.String(120))
    insurance_policy_number = db.Column(db.String(80))
    insurance_expiry_date = db.Column(db.Date)
    active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def _age(self) -> int | None:
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def _bmi(self) -> float | None:
        if not self.height or not self.weight:
            return None
        height_m = self.height / 100.0
        return round(self.weight / (height_m ** 2), 2)

    def to_dict(self, user: dict | None = None) -> dict:
        result = {
            "id": self.id,
            "userId": self.user_id,
            "dateOfBirth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "age": self._age(),
            "gender": self.gender,
            "bloodGroup": self.blood_group,
            "height": self.height,
            "weight": self.weight,
            "bmi": self._bmi(),
            "allergies": self.allergies,
            "chronicDiseases": self.chronic_diseases,
            "currentMedications": self.current_medications,
            "emergencyContactName": self.emergency_contact_name,
            "emergencyContactPhone": self.emergency_contact_phone,
            "emergencyContactRelation": self.emergency_contact_relation,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zipCode": self.zip_code,
            "country": self.country,
            "insuranceProvider": self.insurance_provider,
            "insurancePolicyNumber": self.insurance_policy_number,
            "insuranceExpiryDate": self.insurance_expiry_date.isoformat() if self.insurance_expiry_date else None,
            "active": self.active,
            "patientName": None,
            "email": None,
            "phoneNumber": None,
        }
        if user:
            result["patientName"] = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
            result["email"] = user.get("email")
            result["phoneNumber"] = user.get("phoneNumber")
        return result
