"""
Venus cold-start preloader — heart, ECG, stethoscope.
Shows once per browser session (st.session_state guard).
Pure SVG + CSS. No video, GIF, Lottie, or animation libraries.
"""
from __future__ import annotations

import streamlit as st

from ui.theme import ui_v2_enabled

# Inline SVG with named groups for the motion timeline.
# viewBox sized for the 220×180 stage.
_PRELOADER_SVG = """
<svg class="venus-preloader__svg" viewBox="0 0 220 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <!-- Particles (behind) -->
  <g id="particles">
    <circle class="venus-pl-particle" cx="40" cy="100" r="1.5"/>
    <circle class="venus-pl-particle" cx="55" cy="90" r="1.2"/>
    <circle class="venus-pl-particle" cx="90" cy="110" r="1.4"/>
    <circle class="venus-pl-particle" cx="130" cy="95" r="1.1"/>
    <circle class="venus-pl-particle" cx="150" cy="105" r="1.3"/>
    <circle class="venus-pl-particle" cx="170" cy="88" r="1.2"/>
  </g>

  <!-- ECG line -->
  <g id="ecg">
    <path id="ecg-path" d="M20 100 H45 L52 100 L58 70 L64 130 L70 90 L76 100 H200"/>
  </g>

  <!-- Heart -->
  <g id="heart">
    <path id="heart-outline" d="M70 78c-6-10-20-10-20 2 0 14 20 26 20 26s20-12 20-26c0-12-14-12-20-2z"/>
    <path id="heart-fill" d="M70 78c-6-10-20-10-20 2 0 14 20 26 20 26s20-12 20-26c0-12-14-12-20-2z"/>
    <circle id="ripple" cx="70" cy="72" r="22"/>
  </g>

  <!-- Stethoscope -->
  <g id="stethoscope">
    <path id="tube" d="M95 55 C110 55, 120 65, 118 80 C116 92, 108 95, 100 88"/>
    <g id="chestpiece">
      <circle cx="118" cy="88" r="10" fill="none" stroke="#94A3B8" stroke-width="2"/>
      <circle cx="118" cy="88" r="4" fill="#64748B"/>
    </g>
  </g>

  <!-- Wordmark -->
  <g class="venus-preloader__mark" id="mark">
    <text x="110" y="160" text-anchor="middle"
          font-family="Inter, system-ui, sans-serif"
          font-size="13" font-weight="600" fill="#E8EEF5">Venus Hospital</text>
  </g>
</svg>
"""


def _preloader_html() -> str:
    return f"""
<div class="venus-preloader" id="venus-preloader" role="status" aria-live="polite" aria-label="Loading Venus Hospital">
  <div class="venus-preloader__glow" aria-hidden="true"></div>
  <div class="venus-preloader__stage">
    {_PRELOADER_SVG}
  </div>
  <div class="venus-preloader__footer">
    <div class="venus-preloader__progress" aria-hidden="true">
      <div class="venus-preloader__progress-bar"></div>
    </div>
    <div class="venus-preloader__status">
      <span>Preparing your workspace</span>
      <span>Loading your dashboard</span>
      <span>Ready</span>
    </div>
    <button type="button" class="venus-preloader__skip" id="venus-preloader-skip"
            onclick="(function(){{var el=document.getElementById('venus-preloader');if(el){{el.classList.add('is-done');el.setAttribute('hidden','');}}}})()">
      Skip
    </button>
  </div>
</div>
<script>
(function () {{
  // Hide after animation ends even if CSS animationend is missed
  var el = document.getElementById('venus-preloader');
  if (!el) return;
  setTimeout(function () {{
    el.classList.add('is-done');
    el.setAttribute('hidden', '');
  }}, 2600);
}})();
</script>
"""


def show_preloader(*, force: bool = False) -> None:
    """
    Inject the cold-start preloader once per Streamlit session.
    Only runs when VENUS_UI_V2 is enabled.
    """
    if not ui_v2_enabled():
        return
    if not force and st.session_state.get("_venus_preloader_shown"):
        return
    st.session_state["_venus_preloader_shown"] = True
    st.markdown(_preloader_html(), unsafe_allow_html=True)


def reset_preloader_flag() -> None:
    """Allow preloader again (e.g. after logout)."""
    st.session_state.pop("_venus_preloader_shown", None)
