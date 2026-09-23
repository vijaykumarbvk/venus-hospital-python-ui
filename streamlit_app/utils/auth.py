"""
Session-state based auth helpers.
Phase 7: session-expiry surface + post-login redirect hook.
"""
from __future__ import annotations

import streamlit as st


def is_authenticated() -> bool:
    return bool(st.session_state.get("token")) and bool(st.session_state.get("user"))


def current_user() -> dict | None:
    return st.session_state.get("user")


def login_user(token: str, refresh_token: str, user: dict):
    st.session_state["token"] = token
    st.session_state["refresh_token"] = refresh_token
    st.session_state["user"] = user
    st.session_state.pop("_venus_session_expired", None)


def logout_user():
    for key in ("token", "refresh_token", "user", "_venus_session_expired"):
        st.session_state.pop(key, None)


def require_login():
    # Prefer explicit expiry flag set by api_client on 401
    if st.session_state.get("_venus_session_expired") and not is_authenticated():
        try:
            from ui.components.error_state import session_expired
            # Preserve current page path if available
            session_expired(next_page=None)
        except Exception:
            st.warning("Your session has expired. Please sign in again.")
            st.page_link("Home.py", label="Go to Login", icon="🔐")
            st.stop()
        return

    if not is_authenticated():
        st.warning("Please sign in to continue.")
        st.page_link("Home.py", label="Go to Login", icon="🔐")
        st.stop()


def require_role(*allowed_roles: str):
    require_login()
    user = current_user()
    if not user or user.get("role") not in allowed_roles:
        try:
            from ui.components.error_state import permission_denied
            permission_denied()
        except Exception:
            st.error("You don't have permission to view this page.")
        st.stop()


def consume_post_login_redirect() -> str | None:
    """Return and clear a stored post-login page path, if any."""
    return st.session_state.pop("_venus_post_login_redirect", None)
