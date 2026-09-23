"""Designed empty / partial states — no fake data."""
from __future__ import annotations

import streamlit as st

from ui.html import esc
from ui.icons import icon
from ui.theme import ui_v2_enabled


def empty_state(
    title: str,
    *,
    description: str | None = None,
    icon_name: str = "activity",
    action_label: str | None = None,
    action_page: str | None = None,
) -> None:
    if ui_v2_enabled():
        desc = f"<p>{esc(description)}</p>" if description else ""
        st.markdown(
            f"""
            <div class="venus-empty" role="status">
              <div class="venus-empty__icon" aria-hidden="true">{icon(icon_name, size=32)}</div>
              <div class="venus-empty__title">{esc(title)}</div>
              {desc}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info(title + (f" — {description}" if description else ""))

    if action_label and action_page:
        st.page_link(action_page, label=action_label)


def partial_state(message: str = "Some information is not available.") -> None:
    """When API returns a partial payload — show honest notice, not invented fields."""
    if ui_v2_enabled():
        st.markdown(
            f'<p class="venus-partial" role="status">{esc(message)}</p>',
            unsafe_allow_html=True,
        )
    else:
        st.caption(message)
