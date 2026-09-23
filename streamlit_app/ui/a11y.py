"""Accessibility helpers — live regions, sr-only text, focus notes."""
from __future__ import annotations

import streamlit as st

from ui.html import esc


def sr_only(text: str) -> str:
    """HTML for screen-reader-only text."""
    return f'<span class="venus-sr-only">{esc(text)}</span>'


def announce(message: str, *, assertive: bool = False) -> None:
    """
    Inject an aria-live announcement for async results / toasts.
    Streamlit reruns limit persistence; call after a successful action.
    """
    politeness = "assertive" if assertive else "polite"
    st.markdown(
        f'<div class="venus-live" role="status" aria-live="{politeness}">{esc(message)}</div>',
        unsafe_allow_html=True,
    )


def page_h1(title: str) -> str:
    """Single h1 markup (pages should not emit a second h1)."""
    return f'<h1 class="venus-page__title">{esc(title)}</h1>'
