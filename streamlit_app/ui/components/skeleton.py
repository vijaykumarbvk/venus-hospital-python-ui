"""Loading skeletons matching final layout shapes."""
from __future__ import annotations

import streamlit as st

from ui.theme import ui_v2_enabled


def skeleton_block(*, height: int = 16, width: str = "100%") -> None:
    if ui_v2_enabled():
        st.markdown(
            f'<div class="venus-skeleton" style="height:{height}px;width:{width};margin-bottom:8px" aria-hidden="true"></div>',
            unsafe_allow_html=True,
        )
    else:
        with st.spinner("Loading…"):
            st.write("")


def skeleton_kpi_row(count: int = 4) -> None:
    cols = st.columns(count)
    for c in cols:
        with c:
            if ui_v2_enabled():
                st.markdown(
                    '<div class="venus-kpi" aria-hidden="true">'
                    '<div class="venus-skeleton" style="height:12px;width:40%;margin-bottom:12px"></div>'
                    '<div class="venus-skeleton" style="height:28px;width:60%"></div></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.metric("…", "…")


def skeleton_list(rows: int = 3) -> None:
    for _ in range(rows):
        if ui_v2_enabled():
            st.markdown(
                '<div class="venus-card" style="margin-bottom:12px" aria-hidden="true">'
                '<div class="venus-skeleton" style="height:14px;width:45%;margin-bottom:8px"></div>'
                '<div class="venus-skeleton" style="height:12px;width:70%"></div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.write("…")


def skeleton_table(rows: int = 5) -> None:
    if ui_v2_enabled():
        st.markdown(
            '<div class="venus-card" aria-hidden="true">'
            + "".join(
                '<div class="venus-skeleton" style="height:14px;width:100%;margin-bottom:10px"></div>'
                for _ in range(rows)
            )
            + "</div>",
            unsafe_allow_html=True,
        )
    else:
        with st.spinner("Loading…"):
            st.write("")
