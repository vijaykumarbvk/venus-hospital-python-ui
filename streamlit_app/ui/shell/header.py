"""Contextual header: greeting, date, breadcrumbs placeholder."""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from ui.html import esc
from ui.theme import ui_v2_enabled
from utils import auth


def _greeting(hour: int) -> str:
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"


def render_header(*, page_title: str = "", breadcrumbs: list[str] | None = None) -> None:
    if not ui_v2_enabled():
        return

    user = auth.current_user()
    now = datetime.now()
    greet = _greeting(now.hour)

    if user:
        role = user.get("role", "")
        if role in ("DOCTOR", "SURGEON", "ASSISTANT_DOCTOR"):
            who = f"Dr. {esc(user.get('lastName') or user.get('firstName') or '')}"
        else:
            who = esc(user.get("firstName") or user.get("username") or "")
        line = f"{greet}, {who}"
    else:
        line = greet

    date_str = now.strftime("%A, %d %b %Y")
    crumbs = ""
    if breadcrumbs:
        parts = " / ".join(esc(c) for c in breadcrumbs)
        crumbs = f'<nav class="venus-breadcrumbs" aria-label="Breadcrumb">{parts}</nav>'

    st.markdown(
        f"""
        <div class="venus-header">
          <div class="venus-header__left">
            <p class="venus-header__greeting">{line}</p>
            <p class="venus-header__date">{esc(date_str)}</p>
            {crumbs}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
