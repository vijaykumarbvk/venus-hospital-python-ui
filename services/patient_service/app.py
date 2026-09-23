import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import pybreaker
import requests
from flask import Flask, request

from common.exceptions import BusinessException, ResourceNotFoundException, register_error_handlers
from common.jwt_utils import token_required
from common.resilience import build_breaker, event_publisher
from common.responses import success

from services.patient_service.config import Config
from services.patient_service.models import db, Patient

user_service_breaker = build_breaker("user-service-client", fail_max=5, reset_timeout=30)


@user_service_breaker
def _fetch_user(user_id: int) -> dict | None:
    resp = requests.get(f"{Config.USER_SERVICE_URL}/api/users/{user_id}",
                         headers={"Authorization": request.headers.get("Authorization", "")},
                         timeout=3)
    resp.raise_for_status()
    return resp.json().get("data")


def fetch_user_safe(user_id: int) -> dict | None:
    try:
        return _fetch_user(user_id)
    except (pybreaker.CircuitBreakerError, requests.RequestException):
        return None


def _parse_date(value: str | None):
    return datetime.strptime(value, "%Y-%m-%d").date() if value else None


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

    @app.post("/api/patients")
    @token_required
    def create_patient():
        data = request.get_json(force=True)

        if Patient.query.filter_by(user_id=data["userId"]).first():
            raise BusinessException("Patient profile already exists for this user", "PATIENT_EXISTS")

        user = fetch_user_safe(data["userId"])
        if user is None:
            raise ResourceNotFoundException("User", "id", data["userId"])

        patient = Patient(
            user_id=data["userId"],
            date_of_birth=_parse_date(data.get("dateOfBirth")),
            gender=data.get("gender"),
            blood_group=data.get("bloodGroup"),
            height=data.get("height"),
            weight=data.get("weight"),
            allergies=data.get("allergies"),
            chronic_diseases=data.get("chronicDiseases"),
            current_medications=data.get("currentMedications"),
            emergency_contact_name=data.get("emergencyContactName"),
            emergency_contact_phone=data.get("emergencyContactPhone"),
            emergency_contact_relation=data.get("emergencyContactRelation"),
            address=data.get("address"),
            city=data.get("city"),
            state=data.get("state"),
            zip_code=data.get("zipCode"),
            country=data.get("country"),
            insurance_provider=data.get("insuranceProvider"),
            insurance_policy_number=data.get("insurancePolicyNumber"),
            insurance_expiry_date=_parse_date(data.get("insuranceExpiryDate")),
        )
        db.session.add(patient)
        db.session.commit()

        event_publisher.publish("patient-events", patient.id, {
            "patientId": patient.id, "userId": patient.user_id,
            "bloodGroup": patient.blood_group, "eventType": "PATIENT_CREATED",
        })

        return success(patient.to_dict(user), "Patient profile created successfully", 201)

    @app.get("/api/patients/<int:patient_id>")
    @token_required
    def get_patient(patient_id):
        patient = Patient.query.get(patient_id)
        if not patient:
            raise ResourceNotFoundException("Patient", "id", patient_id)
        return success(patient.to_dict(fetch_user_safe(patient.user_id)))

    @app.get("/api/patients/user/<int:user_id>")
    @token_required
    def get_patient_by_user_id(user_id):
        patient = Patient.query.filter_by(user_id=user_id).first()
        if not patient:
            raise ResourceNotFoundException("Patient", "userId", user_id)
        return success(patient.to_dict(fetch_user_safe(patient.user_id)))

    @app.get("/api/patients/active")
    @token_required
    def get_active_patients():
        patients = Patient.query.filter_by(active=True).all()
        return success([p.to_dict(fetch_user_safe(p.user_id)) for p in patients])

    @app.get("/api/patients/blood-group/<string:blood_group>")
    @token_required
    def get_patients_by_blood_group(blood_group):
        patients = Patient.query.filter_by(blood_group=blood_group).all()
        return success([p.to_dict(fetch_user_safe(p.user_id)) for p in patients])

    @app.put("/api/patients/<int:patient_id>")
    @token_required
    def update_patient(patient_id):
        patient = Patient.query.get(patient_id)
        if not patient:
            raise ResourceNotFoundException("Patient", "id", patient_id)

        data = request.get_json(force=True)
        simple_fields = [
            ("gender", "gender"), ("bloodGroup", "blood_group"), ("height", "height"),
            ("weight", "weight"), ("allergies", "allergies"),
            ("chronicDiseases", "chronic_diseases"), ("currentMedications", "current_medications"),
            ("emergencyContactName", "emergency_contact_name"),
            ("emergencyContactPhone", "emergency_contact_phone"),
            ("emergencyContactRelation", "emergency_contact_relation"),
            ("address", "address"), ("city", "city"), ("state", "state"),
            ("zipCode", "zip_code"), ("country", "country"),
            ("insuranceProvider", "insurance_provider"),
            ("insurancePolicyNumber", "insurance_policy_number"),
        ]
        for field, attr in simple_fields:
            if field in data:
                setattr(patient, attr, data[field])
        if "dateOfBirth" in data:
            patient.date_of_birth = _parse_date(data["dateOfBirth"])
        if "insuranceExpiryDate" in data:
            patient.insurance_expiry_date = _parse_date(data["insuranceExpiryDate"])

        db.session.commit()
        return success(patient.to_dict(fetch_user_safe(patient.user_id)), "Patient updated successfully")

    @app.get("/actuator/health")
    def health():
        return success({"status": "UP", "service": Config.SERVICE_NAME})

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=Config.SERVICE_PORT, debug=True)
