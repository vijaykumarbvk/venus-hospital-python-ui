"""
Load the design-system CSS bundle once per session and apply theme/density.
Feature flag: VENUS_UI_V2=1 (or truthy) enables the new shell styles.
"""
from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

_STYLES_DIR = Path(__file__).resolve().parents[1] / "styles"
_CSS_FILES = [
    "00_tokens.css",
    "10_base.css",
    "20_streamlit_overrides.css",
    "30_components.css",
    "40_layouts.css",
    "50_responsive.css",
    "60_motion.css",
]


def ui_v2_enabled() -> bool:
    """True when the new UI is active."""
    flag = os.environ.get("VENUS_UI_V2", "").strip().lower()
    if flag in ("1", "true", "yes", "on"):
        return True
    # Allow session override for local demos
    return bool(st.session_state.get("venus_ui_v2"))


@st.cache_resource
def _load_css_bundle() -> str:
    parts: list[str] = []
    for name in _CSS_FILES:
        path = _STYLES_DIR / name
        if path.is_file():
            parts.append(path.read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def apply_theme(
    *,
    theme: str | None = None,
    density: str | None = None,
) -> None:
    """
    Inject CSS once and set data-theme / data-density on a wrapper.
    Call near the top of every page when VENUS_UI_V2 is on.
    """
    if not ui_v2_enabled():
        return

    if "venus_theme" not in st.session_state:
        st.session_state["venus_theme"] = theme or "light"
    if "venus_density" not in st.session_state:
        st.session_state["venus_density"] = density or "comfortable"

    if theme in ("light", "dark"):
        st.session_state["venus_theme"] = theme
    if density in ("comfortable", "compact"):
        st.session_state["venus_density"] = density

    css = _load_css_bundle()
    # Mark body via a class we can target in overrides
    st.markdown(
        f"<style>\n{css}\n</style>",
        unsafe_allow_html=True,
    )
    # data attributes for semantic tokens (applied via a fixed banner element)
    t = st.session_state["venus_theme"]
    d = st.session_state["venus_density"]
    st.markdown(
        f'<div class="venus-v2" data-theme="{t}" data-density="{d}" '
        f'style="display:none" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    # Propagate theme to html element via a tiny script is unreliable in Streamlit;
    # we rely on [data-theme] on descendants and CSS variables already set on :root
    # for light. For dark, Settings will set session + re-run; CSS [data-theme=dark]
    # rules apply to elements under the marker. Streamlit's own chrome uses
    # config.toml primaryColor as a fallback.


def page_frame(title: str, *, subtitle: str | None = None) -> None:
    """Minimal page header used by later phases. Safe HTML."""
    from ui.html import esc

    if not ui_v2_enabled():
        st.title(title)
        if subtitle:
            st.caption(subtitle)
        return

    sub = f'<p class="venus-page__subtitle">{esc(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f'<header class="venus-page__header">'
        f'<div><h1 class="venus-page__title">{esc(title)}</h1>{sub}</div>'
        f"</header>",
        unsafe_allow_html=True,
    )
