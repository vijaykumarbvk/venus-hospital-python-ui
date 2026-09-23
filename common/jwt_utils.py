"""
JWT helper functions + decorators shared by every service.
Equivalent to the Java JwtUtil class + the Gateway's JwtAuthenticationFilter,
collapsed into one reusable module since Flask services are simpler to
secure directly (defense in depth: gateway AND service both validate).
"""
import os
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import request, g

from common.responses import error

JWT_SECRET = os.environ.get("JWT_SECRET", "venus-hospital-dev-jwt-secret-CHANGE-ME-b64:pQr7ZmX92kLtFj4Nc8Ws")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_SECONDS = int(os.environ.get("JWT_EXPIRY_SECONDS", 86400))          # 24h
JWT_REFRESH_EXPIRY_SECONDS = int(os.environ.get("JWT_REFRESH_EXPIRY_SECONDS", 604800))  # 7d


def generate_token(username: str, role: str, user_id: int) -> str:
    payload = {
        "sub": username,
        "role": role,
        "userId": user_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=JWT_EXPIRY_SECONDS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_refresh_token(username: str) -> str:
    payload = {
        "sub": username,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=JWT_REFRESH_EXPIRY_SECONDS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def _extract_token() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


def token_required(fn):
    """Validates the JWT and stashes claims on flask.g.current_user."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _extract_token()
        if not token:
            return error("Missing authorization header", "UNAUTHORIZED", 401)
        try:
            claims = decode_token(token)
        except jwt.ExpiredSignatureError:
            return error("Token has expired", "TOKEN_EXPIRED", 401)
        except jwt.InvalidTokenError:
            return error("Invalid token", "INVALID_TOKEN", 401)

        g.current_user = claims
        return fn(*args, **kwargs)
    return wrapper


def roles_required(*allowed_roles):
    """Stack under @token_required to additionally enforce role membership."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = getattr(g, "current_user", None)
            if not claims or claims.get("role") not in allowed_roles:
                return error("Insufficient permissions", "FORBIDDEN", 403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
