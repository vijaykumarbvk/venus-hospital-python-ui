import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st

from ui.shell import render_shell
from ui.theme import apply_theme, ui_v2_enabled
from utils import auth
from utils.dashboards import ROLE_RENDERERS

st.set_page_config(page_title="Dashboard | Venus Hospital", page_icon="🏥", layout="wide")

if ui_v2_enabled():
    with render_shell("Dashboard", active_page="1_Dashboard.py", breadcrumbs=["Home", "Dashboard"]):
        user = auth.current_user()
        renderer = ROLE_RENDERERS.get(user["role"]) if user else None
        if renderer:
            renderer(user)
        else:
            from ui.components import error_state
            error_state(f"No dashboard configured for role: {user.get('role') if user else 'unknown'}")
else:
    apply_theme()  # no-op when flag off
    auth.require_login()
    user = auth.current_user()
    with st.sidebar:
        st.markdown(f"### 👤 {user['firstName']} {user['lastName']}")
        st.caption(user["role"].replace("_", " ").title())
        st.divider()
        if st.button("Log Out", use_container_width=True):
            auth.logout_user()
            st.switch_page("Home.py")
    renderer = ROLE_RENDERERS.get(user["role"])
    if renderer:
        renderer(user)
    else:
        st.error(f"No dashboard configured for role: {user['role']}")
