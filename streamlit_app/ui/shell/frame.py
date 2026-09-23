"""
Unified page frame: theme, skip link, sidebar, header, error boundary wrapper.
"""
from __future__ import annotations

import traceback
from contextlib import contextmanager
from typing import Callable, Iterator

import streamlit as st

from ui.html import esc
from ui.shell.header import render_header
from ui.shell.sidebar import render_sidebar
from ui.theme import apply_theme, ui_v2_enabled
from utils import auth


def page_frame(
    title: str,
    *,
    subtitle: str | None = None,
    active_page: str | None = None,
    breadcrumbs: list[str] | None = None,
    require_auth: bool = True,
) -> None:
    """
    Call at the top of every protected page when V2 is on.
    Applies theme, sidebar, header, and page title.
    """
    apply_theme()

    if require_auth:
        auth.require_login()

    # Skip link (a11y)
    if ui_v2_enabled():
        st.markdown(
            '<a class="venus-skip-link" href="#venus-main">Skip to main content</a>',
            unsafe_allow_html=True,
        )

    with st.sidebar:
        render_sidebar(active_page=active_page)

    render_header(page_title=title, breadcrumbs=breadcrumbs or [title])

    if ui_v2_enabled():
        sub = f'<p class="venus-page__subtitle">{esc(subtitle)}</p>' if subtitle else ""
        st.markdown(
            f'<main id="venus-main" class="venus-page" role="main">'
            f'<header class="venus-page__header">'
            f'<div><h1 class="venus-page__title">{esc(title)}</h1>{sub}</div>'
            f"</header>",
            unsafe_allow_html=True,
        )
    else:
        st.title(title)
        if subtitle:
            st.caption(subtitle)


def close_page_frame() -> None:
    if ui_v2_enabled():
        st.markdown("</main>", unsafe_allow_html=True)


@contextmanager
def render_shell(
    title: str,
    *,
    subtitle: str | None = None,
    active_page: str | None = None,
    breadcrumbs: list[str] | None = None,
) -> Iterator[None]:
    """Context manager with error boundary."""
    page_frame(
        title,
        subtitle=subtitle,
        active_page=active_page,
        breadcrumbs=breadcrumbs,
    )
    try:
        yield
    except Exception as exc:
        # Never show stack traces or tokens in polished UI
        ref = abs(hash(str(exc))) % 10_000_000
        st.markdown(
            f"""
            <div class="venus-error" role="alert">
              <strong>Something went wrong</strong>
              <p>We could not load this section. Try again, or contact support with reference
              <span class="tabular-nums">E-{ref:07d}</span>.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Sanitized log for operators (no PHI/tokens)
        st.session_state.setdefault("_venus_last_error", str(type(exc).__name__))
    finally:
        close_page_frame()
