"""Error, permission-denied, session-expiry, and offline states."""
from __future__ import annotations

import hashlib

import streamlit as st

from ui.html import esc
from ui.theme import ui_v2_enabled


def _ref_id(seed: str | None = None) -> str:
    raw = seed or str(st.session_state.get("_venus_last_error", "err"))
    h = hashlib.sha256(raw.encode()).hexdigest()[:7]
    return f"E-{h.upper()}"


def error_state(
    message: str = "Something went wrong",
    *,
    detail: str | None = None,
    reference: str | None = None,
    retry_label: str | None = "Try again",
    on_retry_rerun: bool = True,
) -> None:
    """Human-readable error with optional reference id and retry."""
    ref = reference or _ref_id(message + (detail or ""))
    st.session_state["_venus_last_error"] = f"{message}|{detail or ''}"

    if ui_v2_enabled():
        det = f"<p>{esc(detail)}</p>" if detail else ""
        st.markdown(
            f"""
            <div class="venus-error" role="alert">
              <strong>{esc(message)}</strong>
              {det}
              <p class="tabular-nums">Reference: {esc(ref)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error(message + (f" — {detail}" if detail else "") + f" [{ref}]")

    if retry_label and on_retry_rerun:
        if st.button(retry_label, key=f"retry_{ref}"):
            st.rerun()


def permission_denied(message: str = "You don't have permission to view this.") -> None:
    error_state(
        message,
        detail="If you believe this is a mistake, contact your administrator.",
        retry_label=None,
    )
    st.page_link("pages/1_Dashboard.py", label="Back to Dashboard")


def session_expired(*, next_page: str | None = None) -> None:
    """Designed session-expiry state; preserves intended destination."""
    if next_page:
        st.session_state["_venus_post_login_redirect"] = next_page
    if ui_v2_enabled():
        st.markdown(
            """
            <div class="venus-error" role="alert">
              <strong>Your session has expired</strong>
              <p>Sign in again to continue. Your place will be restored when possible.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.warning("Your session has expired. Please sign in again.")
    st.page_link("Home.py", label="Sign in", icon="🔐")
    st.stop()


def offline_state(message: str = "We can't reach the server right now.") -> None:
    error_state(
        message,
        detail="Check your connection or try again in a moment. If this continues, contact support.",
    )
