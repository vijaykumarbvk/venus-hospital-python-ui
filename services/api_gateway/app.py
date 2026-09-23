"""
Lightweight API Gateway equivalent to Spring Cloud Gateway:
  - Reverse-proxies /api/* requests to the right downstream service
  - Validates JWTs before proxying (except public paths)
  - Applies Redis-backed rate limiting (like RequestRateLimiter)
  - Wraps each downstream call in its own circuit breaker (like Resilience4j)
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import pybreaker
import requests
from flask import Flask, request, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from common.jwt_utils import decode_token
from common.resilience import build_breaker
from common.responses import error

from services.api_gateway.config import Config

import jwt as pyjwt

# One circuit breaker per downstream service, named for observability.
breakers = {
    prefix: build_breaker(name=f"gateway->{prefix}", fail_max=5, reset_timeout=15)
    for prefix in Config.ROUTES
}

HOP_BY_HOP_HEADERS = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade", "content-length", "host",
}


def create_app():
    app = Flask(__name__)

    limiter = Limiter(
        get_remote_address,
        app=app,
        storage_uri=Config.REDIS_URL,
        default_limits=[Config.RATE_LIMIT],
    )

    def _resolve_target(path: str):
        for prefix, base_url in Config.ROUTES.items():
            if path.startswith(prefix):
                return prefix, base_url
        return None, None

    def _is_public(path: str) -> bool:
        return any(path.startswith(p) for p in Config.PUBLIC_PATHS)

    def _authenticate():
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None, error("Missing authorization header", "UNAUTHORIZED", 401)
        token = auth_header[7:]
        try:
            claims = decode_token(token)
        except pyjwt.ExpiredSignatureError:
            return None, error("Token has expired", "TOKEN_EXPIRED", 401)
        except pyjwt.InvalidTokenError:
            return None, error("Invalid token", "INVALID_TOKEN", 401)
        return claims, None

    @app.route(
        "/<path:path>",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    )
    def proxy(path):
        full_path = f"/{path}"
        prefix, base_url = _resolve_target(full_path)
        if not base_url:
            return error("No route matches this path", "NOT_FOUND", 404)

        claims = None
        if not _is_public(full_path):
            claims, err_response = _authenticate()
            if err_response:
                return err_response

        forward_headers = {k: v for k, v in request.headers.items() if k.lower() not in HOP_BY_HOP_HEADERS}
        if claims:
            forward_headers["X-User-Id"] = str(claims.get("userId", ""))
            forward_headers["X-User-Role"] = claims.get("role", "")

        target_url = f"{base_url}{full_path}"
        breaker = breakers[prefix]

        @breaker
        def _call_downstream():
            return requests.request(
                method=request.method,
                url=target_url,
                headers=forward_headers,
                params=request.args,
                data=request.get_data(),
                timeout=5,
            )

        try:
            downstream_response = _call_downstream()
        except pybreaker.CircuitBreakerError:
            return error(
                f"{prefix} is temporarily unavailable, please try again shortly",
                "SERVICE_UNAVAILABLE", 503,
            )
        except requests.RequestException as exc:
            return error(f"Upstream request failed: {exc}", "BAD_GATEWAY", 502)

        excluded = {"content-encoding", "transfer-encoding", "connection"}
        response_headers = [
            (k, v) for k, v in downstream_response.raw.headers.items()
            if k.lower() not in excluded
        ]
        return Response(downstream_response.content, downstream_response.status_code, response_headers)

    @app.get("/actuator/health")
    def health():
        from common.responses import success
        return success({"status": "UP", "service": Config.SERVICE_NAME})

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=Config.SERVICE_PORT, debug=True)
