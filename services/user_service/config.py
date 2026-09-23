import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
    JWT_SECRET = os.getenv(
        "JWT_SECRET",
        "venus-hospital-dev-jwt-secret-CHANGE-ME-b64:pQr7ZmX92kLtFj4Nc8Ws",
    )
    JWT_EXPIRY_SECONDS = int(os.getenv("JWT_EXPIRY_SECONDS", "86400"))
    JWT_REFRESH_EXPIRY_SECONDS = int(
        os.getenv("JWT_REFRESH_EXPIRY_SECONDS", "604800")
    )

    # Prefer ConfigMap / env; never default to localhost in-cluster.
    DB_HOST = os.getenv("DB_HOST", "mysql")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "admin")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "Cloud123")
    DB_NAME = os.getenv("DB_NAME", "venus_user_db")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SERVICE_NAME = "user-service"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8080"))

    REDIS_URL = os.getenv(
        "REDIS_URL", "redis://venus-hospital-redis.qgfzwt.0001.use1.cache.amazonaws.com:6379/0"
    )
