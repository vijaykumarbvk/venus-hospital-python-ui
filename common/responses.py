"""
Uniform response envelope for every service, equivalent to the
Java ApiResponse<T> / ErrorDetails classes.
"""
from datetime import datetime, timezone
from typing import Any, Optional
from flask import jsonify


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def success(data: Any = None, message: Optional[str] = None, status_code: int = 200):
    """Build a successful Flask JSON response."""
    payload = {
        "success": True,
        "message": message,
        "data": data,
        "error": None,
    }
    return jsonify(payload), status_code


def error(message: str, error_code: str = "ERROR", status_code: int = 400,
          field_errors: Optional[dict] = None):
    """Build an error Flask JSON response."""
    payload = {
        "success": False,
        "message": message,
        "data": None,
        "error": {
            "errorCode": error_code,
            "errorMessage": message,
            "timestamp": _now_iso(),
            "fieldErrors": field_errors or {},
        },
    }
    return jsonify(payload), status_code
