"""
Venus Multispecialty Hospital — entry / auth.
Phase 4: split-screen login + registration stepper when VENUS_UI_V2=1.
Legacy UI preserved when the flag is off.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

import streamlit as st

from utils import api_client, auth

st.set_page_config(
    page_title="Venus Multispecialty Hospital",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Theme + preloader (Phase 1–3)
try:
    from ui.theme import apply_theme, ui_v2_enabled
    from ui.components.loading import show_preloader

    apply_theme()
    if ui_v2_enabled():
        show_preloader()
except Exception:
    def ui_v2_enabled() -> bool:
        return False


# ---------------------------------------------------------------------------
# Shared auth actions (no UI)
# ---------------------------------------------------------------------------
def _do_login(username: str, password: str) -> None:
    if not username or not password:
        st.error("Please enter both username and password.")
        return
    with st.spinner("Signing in..."):
        response = api_client.login(username, password)
    if response.get("success"):
        data = response["data"]
        auth.login_user(data["token"], data["refreshToken"], data["user"])
        st.success(f"Welcome back, {data['user'].get('firstName', '')}!")
        st.switch_page("pages/1_Dashboard.py")
    else:
        # Clear, non-enumerating failure copy
        st.error(response.get("message") or "Sign-in failed. Check your credentials and try again.")


def _do_register(payload: dict) -> bool:
    with st.spinner("Creating your account..."):
        response = api_client.register(payload)
    if response.get("success"):
        st.success("Account created. Sign in with your new credentials.")
        return True
    st.error(response.get("message") or "Registration failed. Please try again.")
    return False


# ---------------------------------------------------------------------------
# V2 — split-screen landing + login + registration stepper
# ---------------------------------------------------------------------------
_REG_STEPS = ("Account", "Personal", "Role", "Review")


def _render_brand_panel() -> None:
    """Value proposition without fabricated stats (no '500+ doctors' etc.)."""
    from ui.html import esc

    st.markdown(
        f"""
        <div class="venus-auth-brand">
          <div class="venus-auth-brand__mark" aria-hidden="true">V</div>
          <h1 class="venus-auth-brand__title">Venus Multispecialty Hospital</h1>
          <p class="venus-auth-brand__lead">
            Clinical operations in one place — appointments, care teams, and records
            designed for patients and clinicians.
          </p>
          <ul class="venus-auth-brand__list">
            <li><span>✓</span> Book and manage appointments online</li>
            <li><span>✓</span> Role-based access for patients and care staff</li>
            <li><span>✓</span> Secure sign-in with session protection</li>
            <li><span>✓</span> Telemedicine-ready consultation types</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_login_v2() -> None:
    st.markdown(
        '<h2 class="venus-auth-card__title">Sign in</h2>'
        '<p class="venus-auth-card__sub">Use your Venus Hospital account</p>',
        unsafe_allow_html=True,
    )
    with st.form("v2_login_form", clear_on_submit=False):
        username = st.text_input(
            "Username",
            autocomplete="username",
            placeholder="Your username",
        )
        password = st.text_input(
            "Password",
            type="password",
            autocomplete="current-password",
            placeholder="Your password",
            help="Password is never shown in the UI after you type it.",
        )
        submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
        if submitted:
            _do_login(username.strip(), password)


def _reg_stepper(step: int) -> None:
    parts = []
    for i, name in enumerate(_REG_STEPS):
        cls = "venus-stepper__step"
        if i < step:
            cls += " is-done"
        elif i == step:
            cls += " is-active"
        parts.append(f'<div class="{cls}">{name}</div>')
    st.markdown(f'<div class="venus-stepper" role="list">{" ".join(parts)}</div>', unsafe_allow_html=True)


def _render_register_v2() -> None:
    """Multi-step registration; state in session_state across reruns."""
    if "reg_step" not in st.session_state:
        st.session_state.reg_step = 0
    if "reg_data" not in st.session_state:
        st.session_state.reg_data = {}

    step = st.session_state.reg_step
    data = st.session_state.reg_data

    st.markdown(
        '<h2 class="venus-auth-card__title">Create account</h2>'
        '<p class="venus-auth-card__sub">A few steps — you can go back without losing data</p>',
        unsafe_allow_html=True,
    )
    _reg_stepper(step)

    # ---- Step 0: Account ----
    if step == 0:
        with st.form("reg_step_account"):
            username = st.text_input(
                "Username",
                value=data.get("username", ""),
                autocomplete="username",
            )
            email = st.text_input(
                "Email",
                value=data.get("email", ""),
                autocomplete="email",
            )
            password = st.text_input(
                "Password",
                type="password",
                autocomplete="new-password",
                help="At least 8 characters.",
            )
            confirm = st.text_input(
                "Confirm password",
                type="password",
                autocomplete="new-password",
            )
            next_btn = st.form_submit_button("Continue", type="primary", use_container_width=True)
            if next_btn:
                if not username or not email or not password:
                    st.error("Username, email, and password are required.")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                elif "@" not in email:
                    st.error("Enter a valid email address.")
                else:
                    data.update({"username": username.strip(), "email": email.strip(), "password": password})
                    st.session_state.reg_step = 1
                    st.rerun()

    # ---- Step 1: Personal ----
    elif step == 1:
        with st.form("reg_step_personal"):
            c1, c2 = st.columns(2)
            first_name = c1.text_input(
                "First name",
                value=data.get("firstName", ""),
                autocomplete="given-name",
            )
            last_name = c2.text_input(
                "Last name",
                value=data.get("lastName", ""),
                autocomplete="family-name",
            )
            phone = st.text_input(
                "Phone number",
                value=data.get("phoneNumber", ""),
                autocomplete="tel",
            )
            cols = st.columns(2)
            back = cols[0].form_submit_button("Back", use_container_width=True)
            nxt = cols[1].form_submit_button("Continue", type="primary", use_container_width=True)
            if back:
                st.session_state.reg_step = 0
                st.rerun()
            if nxt:
                if not first_name or not last_name:
                    st.error("First and last name are required.")
                else:
                    data.update(
                        {
                            "firstName": first_name.strip(),
                            "lastName": last_name.strip(),
                            "phoneNumber": phone.strip(),
                        }
                    )
                    st.session_state.reg_step = 2
                    st.rerun()

    # ---- Step 2: Role ----
    elif step == 2:
        with st.form("reg_step_role"):
            role = st.selectbox(
                "Register as",
                ["PATIENT", "DOCTOR", "ASSISTANT_DOCTOR", "SURGEON"],
                index=["PATIENT", "DOCTOR", "ASSISTANT_DOCTOR", "SURGEON"].index(
                    data.get("role", "PATIENT")
                ),
                format_func=lambda r: r.replace("_", " ").title(),
            )
            st.caption("Admin accounts are provisioned by your hospital IT team.")
            cols = st.columns(2)
            back = cols[0].form_submit_button("Back", use_container_width=True)
            nxt = cols[1].form_submit_button("Continue", type="primary", use_container_width=True)
            if back:
                st.session_state.reg_step = 1
                st.rerun()
            if nxt:
                data["role"] = role
                st.session_state.reg_step = 3
                st.rerun()

    # ---- Step 3: Review ----
    else:
        st.markdown("**Review your details**")
        st.write(f"**Username:** {data.get('username', '')}")
        st.write(f"**Email:** {data.get('email', '')}")
        st.write(f"**Name:** {data.get('firstName', '')} {data.get('lastName', '')}")
        st.write(f"**Phone:** {data.get('phoneNumber') or 'Not provided'}")
        st.write(f"**Role:** {data.get('role', '').replace('_', ' ').title()}")

        cols = st.columns(2)
        if cols[0].button("Back", use_container_width=True):
            st.session_state.reg_step = 2
            st.rerun()
        if cols[1].button("Create account", type="primary", use_container_width=True):
            payload = {
                "firstName": data.get("firstName"),
                "lastName": data.get("lastName"),
                "username": data.get("username"),
                "email": data.get("email"),
                "phoneNumber": data.get("phoneNumber") or "",
                "role": data.get("role"),
                "password": data.get("password"),
            }
            if _do_register(payload):
                st.session_state.reg_step = 0
                st.session_state.reg_data = {}
                # Stay on page so user can switch to Sign in tab


def _render_auth_v2() -> None:
    from ui.html import esc

    # Already signed in
    if auth.is_authenticated():
        user = auth.current_user()
        name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
        st.info(f"You're signed in as **{name}** ({user.get('role', '').replace('_', ' ').title()}).")
        c1, c2 = st.columns(2)
        if c1.button("Go to Dashboard", type="primary", use_container_width=True):
            st.switch_page("pages/1_Dashboard.py")
        if c2.button("Log out", use_container_width=True):
            auth.logout_user()
            try:
                from ui.components.loading import reset_preloader_flag
                reset_preloader_flag()
            except Exception:
                pass
            st.rerun()
        return

    left, right = st.columns([1, 1], gap="large")
    with left:
        _render_brand_panel()
    with right:
        st.markdown('<div class="venus-auth-card">', unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["Sign in", "Register"])
        with tab_login:
            _render_login_v2()
        with tab_register:
            _render_register_v2()
        st.markdown(
            '<p class="venus-auth-footer">Protected by session-based authentication. '
            "Never share your password.</p>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Legacy UI (flag off)
# ---------------------------------------------------------------------------
def _render_auth_legacy() -> None:
    st.markdown(
        """
        <style>
        .venus-hero {
            background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%);
            padding: 2.5rem 2rem; border-radius: 16px; color: white; margin-bottom: 2rem;
        }
        .venus-card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.25rem; background: white; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="venus-hero">
            <h1>🏥 Venus Multispecialty Hospital</h1>
            <p style="font-size:1.1rem;opacity:0.9;">
                Your health, our priority — expert care across specialties, available when you need it.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if auth.is_authenticated():
        user = auth.current_user()
        st.info(
            f"You're already signed in as **{user['firstName']} {user['lastName']}** ({user['role']})."
        )
        col1, col2 = st.columns(2)
        if col1.button("Go to Dashboard", type="primary", use_container_width=True):
            st.switch_page("pages/1_Dashboard.py")
        if col2.button("Log Out", use_container_width=True):
            auth.logout_user()
            st.rerun()
        return

    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.subheader("Why Venus Hospital?")
        st.markdown(
            """
            - Easy appointment booking with real-time availability from your care team
            - Secure medical records protected by signed-in sessions
            - Telemedicine consultations when offered by your clinician
            - Role-based access for patients, doctors, and staff
            """
        )
    with col_right:
        st.markdown('<div class="venus-card">', unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Register"])
        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Sign In", use_container_width=True, type="primary"):
                    _do_login(username, password)
        with tab_register:
            with st.form("register_form"):
                col1, col2 = st.columns(2)
                first_name = col1.text_input("First Name")
                last_name = col2.text_input("Last Name")
                username = st.text_input("Username", key="reg_username")
                email = st.text_input("Email")
                phone = st.text_input("Phone Number")
                role = st.selectbox(
                    "Register as",
                    ["PATIENT", "DOCTOR", "ASSISTANT_DOCTOR", "SURGEON"],
                    format_func=lambda r: r.replace("_", " ").title(),
                )
                col3, col4 = st.columns(2)
                password = col3.text_input("Password", type="password")
                confirm_password = col4.text_input("Confirm Password", type="password")
                if st.form_submit_button("Create Account", use_container_width=True, type="primary"):
                    if password != confirm_password:
                        st.error("Passwords do not match.")
                    elif len(password) < 8:
                        st.error("Password must be at least 8 characters.")
                    else:
                        payload = {
                            "firstName": first_name,
                            "lastName": last_name,
                            "username": username,
                            "email": email,
                            "phoneNumber": phone,
                            "role": role,
                            "password": password,
                        }
                        _do_register(payload)
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------
if ui_v2_enabled():
    _render_auth_v2()
else:
    _render_auth_legacy()
