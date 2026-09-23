"""Role-filtered sidebar: brand, nav, user card, logout."""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from ui.html import esc
from ui.icons import icon
from ui.shell.nav import nav_items_for_role
from ui.theme import ui_v2_enabled
from utils import auth
from ui.components.loading import reset_preloader_flag


def _initials(user: dict) -> str:
    first = (user.get("firstName") or "")[:1]
    last = (user.get("lastName") or "")[:1]
    return (first + last).upper() or "?"


def _role_label(role: str) -> str:
    return (role or "").replace("_", " ").title()


def render_sidebar(*, active_page: str | None = None) -> None:
    """Render sidebar content. Call inside `with st.sidebar:` or it opens one."""
    user = auth.current_user()
    if not user:
        return

    role = user.get("role", "")
    items = nav_items_for_role(role)

    if ui_v2_enabled():
        # Brand
        st.markdown(
            f"""
            <div class="venus-sidebar-brand">
              <div class="venus-sidebar-brand__mark" aria-hidden="true">V</div>
              <div>
                <div class="venus-sidebar-brand__name">Venus Hospital</div>
                <div class="venus-sidebar-brand__tag">Clinical operations</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="venus-role-chip">{esc(_role_label(role))}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="venus-nav-section-label">Navigation</div>', unsafe_allow_html=True)

    else:
        st.markdown(f"### {_initials(user)} {user.get('firstName', '')} {user.get('lastName', '')}")
        st.caption(_role_label(role))
        st.divider()

    # Navigation links
    current_section = None
    for item in items:
        if ui_v2_enabled() and item.section != current_section:
            current_section = item.section
            if current_section != "Main":
                st.markdown(
                    f'<div class="venus-nav-section-label">{esc(current_section)}</div>',
                    unsafe_allow_html=True,
                )

        is_active = active_page is not None and item.page.endswith(active_page)
        # st.page_link is the stable Streamlit nav primitive
        label = item.label
        if ui_v2_enabled():
            # icon + label via page_link (emoji-free label; icon is text fallback)
            st.page_link(item.page, label=label, icon=None)
        else:
            st.page_link(item.page, label=label)

    st.markdown("---")

    # User card + logout
    if ui_v2_enabled():
        name = f"{esc(user.get('firstName', ''))} {esc(user.get('lastName', ''))}".strip()
        st.markdown(
            f"""
            <div class="venus-user-card">
              <div class="venus-user-card__avatar">{esc(_initials(user))}</div>
              <div class="venus-user-card__meta">
                <div class="venus-user-card__name">{name}</div>
                <div class="venus-user-card__role">{esc(_role_label(role))}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    if st.button("Log out", use_container_width=True, key="venus_sidebar_logout"):
        auth.logout_user()
        reset_preloader_flag()
        st.switch_page("Home.py")
