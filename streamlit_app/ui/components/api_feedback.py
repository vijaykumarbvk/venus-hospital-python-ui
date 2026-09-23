"""Map API client responses to designed UI states."""
from __future__ import annotations

from ui.components.error_state import error_state, offline_state, session_expired, permission_denied


def handle_api_error(resp: dict | None, *, fallback: str = "Request failed") -> bool:
    """
    If resp indicates failure, render the appropriate state and return True
    (caller should stop further rendering). Returns False if resp is ok.
    """
    if not resp:
        offline_state()
        return True
    if resp.get("success"):
        return False

    code = resp.get("error_code")
    msg = resp.get("message") or fallback

    if code == "UNAUTHORIZED":
        session_expired()
        return True
    if code == "FORBIDDEN":
        permission_denied(msg)
        return True
    if code in ("NETWORK", "TIMEOUT"):
        offline_state(msg)
        return True

    error_state(msg)
    return True
