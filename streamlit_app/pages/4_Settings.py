import sys
from datetime import date
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st

from ui.components import empty_state, error_state
from ui.shell import render_shell
from ui.theme import apply_theme, ui_v2_enabled
from utils import api_client, auth
from utils import data_cache

st.set_page_config(page_title="Settings | Venus Hospital", page_icon="⚙️", layout="wide")


def _content(user: dict) -> None:
    tab_profile, tab_clinical, tab_prefs = st.tabs(["Account", "Clinical Profile", "Preferences"])

    with tab_profile:
        st.write(f"**Username:** {user.get('username') or 'Not available'}")
        st.write(f"**Email:** {user.get('email') or 'Not available'}")
        st.write(f"**Phone:** {user.get('phoneNumber') or 'Not available'}")
        st.write(f"**Role:** {(user.get('role') or '').replace('_', ' ').title()}")

    with tab_clinical:
        if user["role"] == "PATIENT":
            existing = data_cache.get_patient_by_user_id(user["id"])
            if existing.get("success") and existing.get("data"):
                st.success("Your patient profile is set up. Contact admin to update sensitive fields.")
                data = existing["data"]
                # Honest field display — no raw JSON dump in V2
                for label, key in [
                    ("Age", "age"),
                    ("Gender", "gender"),
                    ("Blood group", "bloodGroup"),
                    ("Height (cm)", "height"),
                    ("Weight (kg)", "weight"),
                    ("BMI", "bmi"),
                    ("Allergies", "allergies"),
                ]:
                    val = data.get(key)
                    st.write(f"**{label}:** {val if val not in (None, '') else 'Not available'}")
            else:
                st.info("Complete your patient profile so clinicians have your health context.")
                with st.form("patient_profile_form"):
                    col1, col2 = st.columns(2)
                    dob = col1.date_input("Date of birth", max_value=date.today())
                    gender = col2.selectbox("Gender", ["Male", "Female", "Other"])
                    blood_group = st.selectbox(
                        "Blood group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
                    )
                    col3, col4 = st.columns(2)
                    height = col3.number_input("Height (cm)", min_value=0.0, step=0.5)
                    weight = col4.number_input("Weight (kg)", min_value=0.0, step=0.5)
                    allergies = st.text_area("Allergies (optional)")
                    emergency_name = st.text_input("Emergency contact name")
                    emergency_phone = st.text_input("Emergency contact phone")
                    submitted = st.form_submit_button("Save Profile", type="primary")
                    if submitted:
                        payload = {
                            "userId": user["id"],
                            "dateOfBirth": dob.isoformat(),
                            "gender": gender,
                            "bloodGroup": blood_group,
                            "height": height,
                            "weight": weight,
                            "allergies": allergies,
                            "emergencyContactName": emergency_name,
                            "emergencyContactPhone": emergency_phone,
                        }
                        result = api_client.create_patient(payload)
                        if result.get("success"):
                            st.success("Profile saved!")
                            st.rerun()
                        else:
                            error_state(result.get("message", "Save failed"))

        elif user["role"] in ("DOCTOR", "ASSISTANT_DOCTOR", "SURGEON"):
            existing = data_cache.get_doctor_by_user_id(user["id"])
            if existing.get("success") and existing.get("data"):
                st.success("Your doctor profile is set up.")
                data = existing["data"]
                for label, key in [
                    ("Specialization", "specialization"),
                    ("Department", "department"),
                    ("Experience (years)", "experienceYears"),
                    ("Consultation fee", "consultationFee"),
                    ("Telemedicine", "availableForTelemedicine"),
                ]:
                    val = data.get(key)
                    if key == "availableForTelemedicine":
                        val = "Yes" if val else "No"
                    st.write(f"**{label}:** {val if val not in (None, '') else 'Not available'}")
            else:
                st.info("Complete your professional profile.")
                with st.form("doctor_profile_form"):
                    specialization = st.text_input("Specialization")
                    license_number = st.text_input("License number")
                    qualification = st.text_input("Qualification")
                    col1, col2 = st.columns(2)
                    experience = col1.number_input("Experience (years)", min_value=0, step=1)
                    department = col2.text_input("Department")
                    fee = st.number_input("Consultation fee (₹)", min_value=0.0, step=50.0)
                    telemedicine = st.checkbox("Available for telemedicine")
                    submitted = st.form_submit_button("Save Profile", type="primary")
                    if submitted:
                        payload = {
                            "userId": user["id"],
                            "specialization": specialization,
                            "licenseNumber": license_number,
                            "qualification": qualification,
                            "experienceYears": experience,
                            "department": department,
                            "consultationFee": fee,
                            "availableForTelemedicine": telemedicine,
                            "workingDays": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"],
                            "availableFrom": "09:00:00",
                            "availableTo": "17:00:00",
                        }
                        result = api_client.create_doctor(payload)
                        if result.get("success"):
                            st.success("Profile saved!")
                            st.rerun()
                        else:
                            error_state(result.get("message", "Save failed"))
        else:
            empty_state("No clinical profile needed for this role", icon_name="settings")

    with tab_prefs:
        if ui_v2_enabled():
            theme = st.radio(
                "Theme",
                ["light", "dark"],
                index=0 if st.session_state.get("venus_theme", "light") == "light" else 1,
                horizontal=True,
            )
            density = st.radio(
                "Density",
                ["comfortable", "compact"],
                index=0 if st.session_state.get("venus_density", "comfortable") == "comfortable" else 1,
                horizontal=True,
            )
            if st.button("Apply preferences", type="primary"):
                st.session_state["venus_theme"] = theme
                st.session_state["venus_density"] = density
                st.success("Preferences saved for this session.")
                st.rerun()
        else:
            st.caption("Theme and density controls are available when VENUS_UI_V2 is enabled.")

        st.divider()
        st.subheader("About")
        st.write("**Application:** Venus Multispecialty Hospital")
        st.write("**UI mode:** " + ("Design system v2" if ui_v2_enabled() else "Classic"))
        st.caption("Clinical profile updates for existing records may require administrator support.")


if ui_v2_enabled():
    with render_shell("Settings", active_page="4_Settings.py", breadcrumbs=["Home", "Settings"]):
        _content(auth.current_user())
else:
    apply_theme()
    auth.require_login()
    user = auth.current_user()
    with st.sidebar:
        st.markdown(f"### 👤 {user['firstName']} {user['lastName']}")
        st.caption(user["role"].replace("_", " ").title())
        if st.button("Log Out", use_container_width=True):
            auth.logout_user()
            st.switch_page("Home.py")
    st.title("⚙️ Settings")
    _content(user)
