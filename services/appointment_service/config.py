import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
    JWT_SECRET = os.getenv(
        "JWT_SECRET",
        "venus-hospital-dev-jwt-secret-CHANGE-ME-b64:pQr7ZmX92kLtFj4Nc8Ws",
    )

    DB_HOST = os.getenv("DB_HOST", "mysql")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "admin")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "Cloud123")
    DB_NAME = os.getenv("DB_NAME", "venus_appointment_db")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SERVICE_NAME = "appointment-service"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8080"))

    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:80")
    DOCTOR_SERVICE_URL = os.getenv("DOCTOR_SERVICE_URL", "http://doctor-service:80")
    PATIENT_SERVICE_URL = os.getenv("PATIENT_SERVICE_URL", "http://patient-service:80")

    MAX_APPOINTMENTS_PER_DOCTOR_PER_DAY = int(
        os.getenv("MAX_APPOINTMENTS_PER_DOCTOR_PER_DAY", "20")
    )
    CONFLICT_WINDOW_MINUTES = int(os.getenv("CONFLICT_WINDOW_MINUTES", "30"))

    REDIS_URL = os.getenv(
        "REDIS_URL", "redis://venus-hospital-redis.qgfzwt.0001.use1.cache.amazonaws.com:6379/0"
    )
