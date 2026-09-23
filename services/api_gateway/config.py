import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
    JWT_SECRET = os.getenv(
        "JWT_SECRET",
        "venus-hospital-dev-jwt-secret-CHANGE-ME-b64:pQr7ZmX92kLtFj4Nc8Ws",
    )

    # Downstream service URLs — match k8s Service DNS + port 80
    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:80")
    DOCTOR_SERVICE_URL = os.getenv("DOCTOR_SERVICE_URL", "http://doctor-service:80")
    PATIENT_SERVICE_URL = os.getenv("PATIENT_SERVICE_URL", "http://patient-service:80")
    APPOINTMENT_SERVICE_URL = os.getenv(
        "APPOINTMENT_SERVICE_URL", "http://appointment-service:80"
    )

    ROUTES = {
        "/api/users": USER_SERVICE_URL,
        "/api/appointments": APPOINTMENT_SERVICE_URL,
        "/api/doctors": DOCTOR_SERVICE_URL,
        "/api/patients": PATIENT_SERVICE_URL,
    }

    PUBLIC_PATHS = {
        "/api/users/register",
        "/api/users/login",
        "/actuator/health",
    }

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_URL = os.getenv(
        "REDIS_URL",
        f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    )
    RATE_LIMIT = os.getenv("RATE_LIMIT", "100 per minute")

    SERVICE_NAME = "api-gateway"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8080"))
