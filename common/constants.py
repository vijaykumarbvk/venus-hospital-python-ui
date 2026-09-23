"""
Shared enums/constants used across every microservice.
Keeping these in one place avoids drift between services.
"""


class UserRole:
    ADMIN = "ADMIN"
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ASSISTANT_DOCTOR = "ASSISTANT_DOCTOR"
    SURGEON = "SURGEON"

    ALL = [ADMIN, PATIENT, DOCTOR, ASSISTANT_DOCTOR, SURGEON]


class AppointmentStatus:
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"

    ALL = [SCHEDULED, CONFIRMED, IN_PROGRESS, COMPLETED, CANCELLED, NO_SHOW]


class ConsultationType:
    IN_PERSON = "IN_PERSON"
    TELEMEDICINE = "TELEMEDICINE"


class AppointmentType:
    CONSULTATION = "CONSULTATION"
    FOLLOW_UP = "FOLLOW_UP"
    EMERGENCY = "EMERGENCY"
