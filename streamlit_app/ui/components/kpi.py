"""KPI cards — values from real data only."""
from __future__ import annotations

from typing import Any

import streamlit as st

from ui.html import esc
from ui.theme import ui_v2_enabled


def kpi_card(label: str, value: Any, *, hint: str | None = None) -> None:
    display = value if value is not None and value != "" else "Not available"
    if ui_v2_enabled():
        hint_html = f'<div class="venus-kpi__hint">{esc(hint)}</div>' if hint else ""
        st.markdown(
            f"""
            <div class="venus-kpi">
              <div class="venus-kpi__label">{esc(label)}</div>
              <div class="venus-kpi__value tabular-nums">{esc(display)}</div>
              {hint_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.metric(label, display, help=hint)


def kpi_row(items: list[tuple[str, Any]] | list[dict]) -> None:
    """items: list of (label, value) or dicts with label/value/hint."""
    n = max(len(items), 1)
    cols = st.columns(min(n, 4))
    for i, item in enumerate(items):
        with cols[i % len(cols)]:
            if isinstance(item, dict):
                kpi_card(item.get("label", ""), item.get("value"), hint=item.get("hint"))
            else:
                label, value = item
                kpi_card(label, value)
