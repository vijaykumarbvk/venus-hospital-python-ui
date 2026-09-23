import sys
from pathlib import Path

# Allow `common` to be imported when this file is run directly.
sys.path.append(str(Path(__file__).resolve().parents[2]))

from flask import Flask, request, g
from werkzeug.security import generate_password_hash, check_password_hash

from common.constants import UserRole
from common.exceptions import BusinessException, ResourceNotFoundException, register_error_handlers
from common.jwt_utils import generate_token, generate_refresh_token, token_required
from common.resilience import event_publisher
from common.responses import success, error

from services.user_service.config import Config
from services.user_service.models import db, User
from services.user_service.schemas import register_schema, login_schema


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

    # ---------------------------------------------------------------- #
    # Auth endpoints (public)
    # ---------------------------------------------------------------- #
    @app.post("/api/users/register")
    def register():
        data = register_schema.load(request.get_json(force=True))

        if User.query.filter_by(username=data["username"]).first():
            raise BusinessException("Username already exists", "USERNAME_EXISTS")
        if User.query.filter_by(email=data["email"]).first():
            raise BusinessException("Email already exists", "EMAIL_EXISTS")

        user = User(
            username=data["username"],
            email=data["email"],
            password_hash=generate_password_hash(data["password"]),
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone_number=data["phone_number"],
            role=data["role"],
            active=True,
        )
        db.session.add(user)
        db.session.commit()

        event_publisher.publish(
            "user-registration-topic", user.id,
            {"userId": user.id, "username": user.username, "role": user.role,
             "eventType": "USER_REGISTERED"},
        )

        return success(user.to_dict(), "User registered successfully", 201)

    @app.post("/api/users/login")
    def login():
        data = login_schema.load(request.get_json(force=True))

        user = User.query.filter_by(username=data["username"]).first()
        if not user or not check_password_hash(user.password_hash, data["password"]):
            raise BusinessException("Invalid credentials", "INVALID_CREDENTIALS")
        if not user.active:
            raise BusinessException("Account is deactivated", "ACCOUNT_INACTIVE")

        token = generate_token(user.username, user.role, user.id)
        refresh_token = generate_refresh_token(user.username)

        return success({
            "token": token,
            "refreshToken": refresh_token,
            "user": user.to_dict(),
        }, "Login successful")

    # ---------------------------------------------------------------- #
    # User lookups (protected)
    # ---------------------------------------------------------------- #
    @app.get("/api/users/<int:user_id>")
    @token_required
    def get_user_by_id(user_id):
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundException("User", "id", user_id)
        return success(user.to_dict())

    @app.get("/api/users/username/<string:username>")
    @token_required
    def get_user_by_username(username):
        user = User.query.filter_by(username=username).first()
        if not user:
            raise ResourceNotFoundException("User", "username", username)
        return success(user.to_dict())

    @app.get("/api/users/role/<string:role>")
    @token_required
    def get_users_by_role(role):
        users = User.query.filter_by(role=role).all()
        return success([u.to_dict() for u in users])

    @app.get("/api/users/active")
    @token_required
    def get_active_users():
        users = User.query.filter_by(active=True).all()
        return success([u.to_dict() for u in users])

    @app.put("/api/users/<int:user_id>")
    @token_required
    def update_user(user_id):
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundException("User", "id", user_id)

        data = request.get_json(force=True)
        user.first_name = data.get("firstName", user.first_name)
        user.last_name = data.get("lastName", user.last_name)
        user.phone_number = data.get("phoneNumber", user.phone_number)
        user.email = data.get("email", user.email)
        db.session.commit()

        return success(user.to_dict(), "User updated successfully")

    @app.delete("/api/users/<int:user_id>")
    @token_required
    def deactivate_user(user_id):
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundException("User", "id", user_id)
        user.active = False
        db.session.commit()
        return success(None, "User deactivated successfully")

    @app.get("/actuator/health")
    def health():
        return success({"status": "UP", "service": Config.SERVICE_NAME})

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=Config.SERVICE_PORT, debug=True)
