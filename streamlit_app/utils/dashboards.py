"""
Role dashboards — presentation only.
Phase 5: real API data only. Fabricated metrics/tasks/OT/surgery boards removed.
When VENUS_UI_V2 is on, uses design-system components; otherwise legacy metrics.
"""
from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from utils import api_client
from utils import data_cache

try:
    from ui.theme import ui_v2_enabled
    from ui.components import (
        kpi_row,
        status_badge,
        empty_state,
        error_state,
    )
    from ui.components.api_feedback import handle_api_error
except Exception:
    def ui_v2_enabled() -> bool:
        return False


def _na(value, fallback="Not available"):
    if value is None or value == "":
        return fallback
    return value


def _legacy_status(status: str) -> str:
    colors = {
        "SCHEDULED": "🔵", "CONFIRMED": "🟣", "IN_PROGRESS": "🟡",
        "COMPLETED": "🟢", "CANCELLED": "🔴", "NO_SHOW": "⚪",
    }
    return f"{colors.get(status, '⚪')} {(status or '').replace('_', ' ').title()}"


# ------------------------------------------------------------------ #
# PATIENT
# ------------------------------------------------------------------ #
def render_patient_dashboard(user: dict):
    first = user.get("firstName") or user.get("username") or "there"
    if ui_v2_enabled():
        st.markdown(f"### Welcome back, {first}")
    else:
        st.header(f"Welcome back, {first}!")

    profile_resp = data_cache.get_patient_by_user_id(user["id"])
    patient = profile_resp.get("data") if profile_resp.get("success") else None

    appointments: list = []
    if patient:
        appt_resp = data_cache.get_patient_appointments(patient["id"])
        if appt_resp.get("success"):
            appointments = appt_resp.get("data") or []
        elif not appt_resp.get("success"):
            if ui_v2_enabled():
                try:
                    handle_api_error(appt_resp, fallback="Could not load appointments")
                except Exception:
                    error_state("Could not load appointments", detail=appt_resp.get("message"))
            else:
                st.warning(appt_resp.get("message") or "Could not load appointments")

    upcoming = [a for a in appointments if a.get("status") in ("SCHEDULED", "CONFIRMED")]
    completed = [a for a in appointments if a.get("status") == "COMPLETED"]

    # KPIs — only from real lists / profile fields
    kpi_items = [
        ("Upcoming appointments", len(upcoming)),
        ("Completed visits", len(completed)),
        ("Blood group", _na(patient.get("bloodGroup") if patient else None)),
        (
            "BMI",
            _na(patient.get("bmi") if patient else None),
        ),
    ]
    if ui_v2_enabled():
        # BMI tooltip basis if present
        hints = [None, None, None, None]
        if patient and patient.get("bmi") is not None and patient.get("height") and patient.get("weight"):
            hints[3] = f"From height {patient.get('height')} cm and weight {patient.get('weight')} kg"
        kpi_row(
            [
                {"label": kpi_items[0][0], "value": kpi_items[0][1]},
                {"label": kpi_items[1][0], "value": kpi_items[1][1]},
                {"label": kpi_items[2][0], "value": kpi_items[2][1]},
                {"label": kpi_items[3][0], "value": kpi_items[3][1], "hint": hints[3]},
            ]
        )
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(*kpi_items[0])
        c2.metric(*kpi_items[1])
        c3.metric(*kpi_items[2])
        c4.metric(*kpi_items[3])

    st.divider()
    left, right = st.columns([2, 1])

    with left:
        st.subheader("Upcoming appointments")
        if upcoming:
            for a in sorted(upcoming, key=lambda x: x.get("appointmentDateTime") or ""):
                doctor = _na(a.get("doctorName"), f"Doctor #{a.get('doctorId')}")
                when = _na(a.get("appointmentDateTime"))
                if ui_v2_enabled():
                    badge = status_badge(a.get("status"))
                    st.markdown(
                        f"**{doctor}** · {when} · {badge}",
                        unsafe_allow_html=True,
                    )
                    if a.get("chiefComplaint"):
                        st.caption(a["chiefComplaint"])
                else:
                    st.write(f"**{doctor}** — {when} — {_legacy_status(a.get('status', ''))}")
            st.page_link("pages/2_Appointments.py", label="Manage appointments")
        else:
            if ui_v2_enabled():
                empty_state(
                    "No upcoming appointments",
                    description="Book one from the Appointments page when you're ready.",
                    icon_name="calendar",
                )
            else:
                st.info("No upcoming appointments. Book one from the Appointments page.")
            st.page_link("pages/2_Appointments.py", label="Book an appointment")

    with right:
        st.subheader("Health profile")
        if patient:
            st.write(f"**Age:** {_na(patient.get('age'))}")
            st.write(f"**Gender:** {_na(patient.get('gender'))}")
            st.write(f"**Height:** {_na(patient.get('height'))} cm" if patient.get("height") is not None else "**Height:** Not available")
            st.write(f"**Weight:** {_na(patient.get('weight'))} kg" if patient.get("weight") is not None else "**Weight:** Not available")
            allergies = patient.get("allergies")
            if allergies:
                if ui_v2_enabled():
                    st.markdown(
                        f'<div class="venus-badge venus-badge--critical" role="status">'
                        f"Allergies: {allergies}</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.warning(f"**Allergies:** {allergies}")
            else:
                st.caption("No allergies recorded.")
        else:
            if ui_v2_enabled():
                empty_state(
                    "Profile incomplete",
                    description="Complete your patient profile in Settings.",
                    icon_name="user",
                )
            else:
                st.info("Complete your patient profile to see health insights here.")
            st.page_link("pages/4_Settings.py", label="Go to Settings")


# ------------------------------------------------------------------ #
# DOCTOR
# ------------------------------------------------------------------ #
def render_doctor_dashboard(user: dict):
    last = user.get("lastName") or user.get("firstName") or ""
    if ui_v2_enabled():
        st.markdown(f"### Good day, Dr. {last}")
    else:
        st.header(f"Good day, Dr. {last}")

    profile_resp = data_cache.get_doctor_by_user_id(user["id"])
    doctor = profile_resp.get("data") if profile_resp.get("success") else None

    appointments: list = []
    if doctor:
        appt_resp = data_cache.get_doctor_appointments(doctor["id"])
        if appt_resp.get("success"):
            appointments = appt_resp.get("data") or []
        elif appt_resp.get("message"):
            if ui_v2_enabled():
                error_state("Could not load schedule", detail=appt_resp.get("message"))
            else:
                st.warning(appt_resp.get("message"))
    else:
        if ui_v2_enabled():
            empty_state(
                "No doctor profile linked",
                description="Complete your professional profile in Settings.",
                icon_name="stethoscope",
            )
        else:
            st.info("No doctor profile linked to this account yet.")
        st.page_link("pages/4_Settings.py", label="Go to Settings")
        return

    today_str = datetime.now().date().isoformat()
    today_appts = [
        a for a in appointments
        if (a.get("appointmentDateTime") or "").startswith(today_str)
    ]
    completed_today = [a for a in today_appts if a.get("status") == "COMPLETED"]
    pending_today = [
        a for a in today_appts if a.get("status") in ("SCHEDULED", "CONFIRMED", "IN_PROGRESS")
    ]
    unique_patients = len({a.get("patientId") for a in appointments if a.get("patientId") is not None})

    items = [
        ("Today's appointments", len(today_appts)),
        ("Completed today", len(completed_today)),
        ("Pending today", len(pending_today)),
        ("Patients (all time)", unique_patients),
    ]
    if ui_v2_enabled():
        kpi_row([(a, b) for a, b in items])
    else:
        cols = st.columns(4)
        for col, (lab, val) in zip(cols, items):
            col.metric(lab, val)

    st.divider()
    st.subheader("Today's schedule")

    if not today_appts:
        if ui_v2_enabled():
            empty_state("No appointments scheduled for today", icon_name="calendar")
        else:
            st.info("No appointments scheduled for today.")
        return

    for appt in sorted(today_appts, key=lambda a: a.get("appointmentDateTime") or ""):
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 2])
            patient_label = appt.get("patientName") or f"Patient #{appt.get('patientId')}"
            c1.markdown(f"**{patient_label}**")
            c1.caption(appt.get("chiefComplaint") or "No chief complaint noted")
            if ui_v2_enabled():
                c2.markdown(status_badge(appt.get("status")), unsafe_allow_html=True)
            else:
                c2.write(_legacy_status(appt.get("status") or ""))
            c2.caption(_na(appt.get("appointmentDateTime")))

            next_status = {
                "SCHEDULED": "CONFIRMED",
                "CONFIRMED": "IN_PROGRESS",
                "IN_PROGRESS": "COMPLETED",
            }.get(appt.get("status") or "")

            if next_status and c3.button(
                f"Mark {next_status.replace('_', ' ').title()}",
                key=f"appt-{appt['id']}",
            ):
                result = api_client.update_appointment_status(appt["id"], next_status)
                if result.get("success"):
                    data_cache.clear_data_caches()
                    st.rerun()
                else:
                    if ui_v2_enabled():
                        error_state(result.get("message") or "Update failed")
                    else:
                        st.error(result.get("message"))


# ------------------------------------------------------------------ #
# ASSISTANT DOCTOR — no fabricated tasks or metrics
# ------------------------------------------------------------------ #
def render_assistant_doctor_dashboard(user: dict):
    name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip() or "Assistant"
    if ui_v2_enabled():
        st.markdown(f"### Assistant dashboard — {name}")
    else:
        st.header(f"Assistant Dashboard — {name}")

    # Real data only: assigned doctors list from active doctors API (limited context)
    doctors_resp = data_cache.get_active_doctors()
    doctors = doctors_resp.get("data") or [] if doctors_resp.get("success") else []

    # Try linked doctor profile for this user's own appointments if any
    profile_resp = data_cache.get_doctor_by_user_id(user["id"])
    doctor = profile_resp.get("data") if profile_resp.get("success") else None
    appointments: list = []
    if doctor:
        appt_resp = data_cache.get_doctor_appointments(doctor["id"])
        if appt_resp.get("success"):
            appointments = appt_resp.get("data") or []

    today_str = datetime.now().date().isoformat()
    today_appts = [
        a for a in appointments
        if (a.get("appointmentDateTime") or "").startswith(today_str)
    ]

    if ui_v2_enabled():
        kpi_row(
            [
                ("Today's appointments", len(today_appts)),
                ("Active doctors (directory)", len(doctors)),
                ("Your linked profile", "Yes" if doctor else "Not set up"),
            ]
        )
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Today's appointments", len(today_appts))
        c2.metric("Active doctors", len(doctors))
        c3.metric("Linked profile", "Yes" if doctor else "No")

    st.divider()
    left, right = st.columns([2, 1])

    with left:
        st.subheader("Today's appointments")
        if today_appts:
            for appt in sorted(today_appts, key=lambda a: a.get("appointmentDateTime") or ""):
                with st.container(border=True):
                    label = appt.get("patientName") or f"Patient #{appt.get('patientId')}"
                    st.markdown(f"**{label}**")
                    st.caption(_na(appt.get("appointmentDateTime")))
                    if ui_v2_enabled():
                        st.markdown(status_badge(appt.get("status")), unsafe_allow_html=True)
                    else:
                        st.write(_legacy_status(appt.get("status") or ""))
        else:
            if ui_v2_enabled():
                empty_state(
                    "No appointments for today",
                    description="Task boards and hand-off notes are not available from the API yet.",
                    icon_name="calendar",
                )
            else:
                st.info(
                    "No appointments for today. "
                    "Detailed assistant task boards are not available from the API."
                )

    with right:
        st.subheader("Doctors in directory")
        if doctors:
            for doc in doctors[:8]:
                st.write(
                    f"**{_na(doc.get('doctorName'), 'Doctor')}** — "
                    f"{_na(doc.get('specialization'))}"
                )
            if len(doctors) > 8:
                st.caption(f"Showing 8 of {len(doctors)}. See Directory for the full list.")
            st.page_link("pages/3_Directory.py", label="Open directory")
        else:
            if ui_v2_enabled():
                empty_state("No doctors listed", icon_name="users")
            else:
                st.info("No doctors in the directory yet.")

        if not doctor:
            st.divider()
            st.caption("Link a clinical profile in Settings to see your own schedule here.")
            st.page_link("pages/4_Settings.py", label="Settings")


# ------------------------------------------------------------------ #
# SURGEON — no fabricated OT / surgery schedule
# ------------------------------------------------------------------ #
def render_surgeon_dashboard(user: dict):
    first = user.get("firstName") or ""
    last = user.get("lastName") or ""
    title = f"Dr. {first} {last}".strip() or "Surgeon"
    if ui_v2_enabled():
        st.markdown(f"### Surgeon dashboard — {title}")
    else:
        st.header(f"Surgeon Dashboard — {title}")

    # Reuse doctor appointment data when a doctor profile exists
    profile_resp = data_cache.get_doctor_by_user_id(user["id"])
    doctor = profile_resp.get("data") if profile_resp.get("success") else None

    appointments: list = []
    if doctor:
        appt_resp = data_cache.get_doctor_appointments(doctor["id"])
        if appt_resp.get("success"):
            appointments = appt_resp.get("data") or []

    today_str = datetime.now().date().isoformat()
    today_appts = [
        a for a in appointments
        if (a.get("appointmentDateTime") or "").startswith(today_str)
    ]
    # Surgery-like appointments if type is present
    surgical = [
        a for a in appointments
        if (a.get("appointmentType") or "").upper() in ("SURGERY", "PROCEDURE", "OPERATION")
    ]

    if ui_v2_enabled():
        kpi_row(
            [
                ("Today's appointments", len(today_appts)),
                ("Procedure-type (all)", len(surgical)),
                ("Profile linked", "Yes" if doctor else "Not set up"),
            ]
        )
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Today's appointments", len(today_appts))
        c2.metric("Procedure-type appointments", len(surgical))
        c3.metric("Profile linked", "Yes" if doctor else "No")

    st.divider()
    st.subheader("Schedule")

    if not doctor:
        if ui_v2_enabled():
            empty_state(
                "No surgeon/doctor profile linked",
                description="Complete your professional profile in Settings. "
                "Dedicated OT boards and surgery lists are not provided by the API.",
                icon_name="activity",
            )
        else:
            st.info(
                "No profile linked. OT availability and surgery boards are not available "
                "from the backend API."
            )
        st.page_link("pages/4_Settings.py", label="Go to Settings")
        return

    if today_appts:
        for appt in sorted(today_appts, key=lambda a: a.get("appointmentDateTime") or ""):
            with st.container(border=True):
                label = appt.get("patientName") or f"Patient #{appt.get('patientId')}"
                st.markdown(f"**{label}** · {_na(appt.get('appointmentType'))}")
                st.caption(_na(appt.get("appointmentDateTime")))
                if ui_v2_enabled():
                    st.markdown(status_badge(appt.get("status")), unsafe_allow_html=True)
                else:
                    st.write(_legacy_status(appt.get("status") or ""))
    else:
        if ui_v2_enabled():
            empty_state(
                "No appointments scheduled for today",
                description="Operating-theatre boards and pre-op checklists require dedicated APIs that are not available yet.",
                icon_name="calendar",
            )
        else:
            st.info(
                "No appointments for today. "
                "Dedicated surgery/OT boards are not available from the API."
            )

    st.page_link("pages/2_Appointments.py", label="Open appointments")


# ------------------------------------------------------------------ #
# ADMIN — real counts only; no fake service health
# ------------------------------------------------------------------ #
def render_admin_dashboard(user: dict):
    if ui_v2_enabled():
        st.markdown("### Admin dashboard")
        st.caption("Venus Multispecialty Hospital management")
    else:
        st.header("Admin Dashboard")
        st.caption("Venus Multispecialty Hospital Management")

    users_resp = data_cache.get_active_users()
    doctors_resp = data_cache.get_active_doctors()
    patients_resp = data_cache.get_active_patients()

    users = users_resp.get("data") or [] if users_resp.get("success") else []
    doctors = doctors_resp.get("data") or [] if doctors_resp.get("success") else []
    patients = patients_resp.get("data") or [] if patients_resp.get("success") else []

    # Surface load errors honestly
    for label, resp in (
        ("users", users_resp),
        ("doctors", doctors_resp),
        ("patients", patients_resp),
    ):
        if not resp.get("success") and resp.get("message"):
            if ui_v2_enabled():
                error_state(f"Could not load {label}", detail=resp.get("message"))
            else:
                st.warning(f"Could not load {label}: {resp.get('message')}")

    active_doctors = sum(1 for d in doctors if d.get("active") is not False)

    if ui_v2_enabled():
        kpi_row(
            [
                ("Users", len(users)),
                ("Doctors", len(doctors)),
                ("Patients", len(patients)),
                ("Active doctors", active_doctors),
            ]
        )
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Users", len(users))
        c2.metric("Total Doctors", len(doctors))
        c3.metric("Total Patients", len(patients))
        c4.metric("Active Doctors", active_doctors)

    st.divider()
    left, right = st.columns([2, 1])

    with left:
        st.subheader("Doctors")
        if doctors:
            df = pd.DataFrame(
                [
                    {
                        "Name": _na(d.get("doctorName")),
                        "Specialization": _na(d.get("specialization")),
                        "Department": _na(d.get("department")),
                        "Experience": (
                            f"{d.get('experienceYears')} yrs"
                            if d.get("experienceYears") is not None
                            else "Not available"
                        ),
                    }
                    for d in doctors
                ]
            )
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            if ui_v2_enabled():
                empty_state("No doctors registered yet", icon_name="users")
            else:
                st.info("No doctors registered yet.")

        st.subheader("Department distribution")
        if doctors:
            depts = [d.get("department") or "Unknown" for d in doctors]
            st.bar_chart(pd.Series(depts).value_counts())
        else:
            st.caption("Not available — no department data.")

    with right:
        st.subheader("System health")
        # Honest: no health endpoints exist
        if ui_v2_enabled():
            empty_state(
                "Health data unavailable",
                description="Service health endpoints are not exposed by the API gateway.",
                icon_name="activity",
            )
        else:
            st.info("Service health endpoints are not available from the API.")

        st.divider()
        st.subheader("Quick actions")
        st.page_link("pages/3_Directory.py", label="Directory")
        st.page_link("pages/2_Appointments.py", label="Appointments")


ROLE_RENDERERS = {
    "PATIENT": render_patient_dashboard,
    "DOCTOR": render_doctor_dashboard,
    "ASSISTANT_DOCTOR": render_assistant_doctor_dashboard,
    "SURGEON": render_surgeon_dashboard,
    "ADMIN": render_admin_dashboard,
}
