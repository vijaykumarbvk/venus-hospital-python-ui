"""
Appointments — Phase 6.
Patient: multi-step booking wizard + segmented My Appointments.
Clinician: schedule list with status updates.
Admin: guidance only.
Real API data only; no invented slots.
"""
from __future__ import annotations

import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
import streamlit as st

from ui.components import empty_state, error_state, status_badge
from ui.a11y import announce
from ui.shell import render_shell
from ui.theme import apply_theme, ui_v2_enabled
from utils import api_client, auth
from utils import data_cache

st.set_page_config(page_title="Appointments | Venus Hospital", page_icon="📅", layout="wide")

_BOOK_STEPS = ("Doctor", "Date & time", "Details", "Confirm")


def _na(v, fallback="Not available"):
    return fallback if v is None or v == "" else v


# ---------------------------------------------------------------------------
# Patient booking wizard (session state)
# ---------------------------------------------------------------------------
def _init_book_state():
    if "book_step" not in st.session_state:
        st.session_state.book_step = 0
    if "book_data" not in st.session_state:
        st.session_state.book_data = {}


def _book_stepper(step: int) -> None:
    if not ui_v2_enabled():
        st.caption(f"Step {step + 1} of {len(_BOOK_STEPS)}: {_BOOK_STEPS[step]}")
        return
    parts = []
    for i, name in enumerate(_BOOK_STEPS):
        cls = "venus-stepper__step"
        if i < step:
            cls += " is-done"
        elif i == step:
            cls += " is-active"
        parts.append(f'<div class="{cls}">{name}</div>')
    st.markdown(f'<div class="venus-stepper">{" ".join(parts)}</div>', unsafe_allow_html=True)


def _patient_booking(patient: dict) -> None:
    _init_book_state()
    step = st.session_state.book_step
    data = st.session_state.book_data

    doctors_resp = data_cache.get_active_doctors()
    doctors = doctors_resp.get("data") or [] if doctors_resp.get("success") else []
    if not doctors:
        empty_state(
            "No doctors available",
            description="Please check back later. Availability comes from the live directory.",
            icon_name="users",
        )
        return

    _book_stepper(step)

    # Summary side panel content (always show chosen values)
    summary_bits = []
    if data.get("doctor_label"):
        summary_bits.append(f"**Doctor:** {data['doctor_label']}")
    if data.get("datetime_iso"):
        summary_bits.append(f"**When:** {data['datetime_iso']}")
    if data.get("consultation_type"):
        summary_bits.append(f"**Mode:** {data['consultation_type'].replace('_', ' ').title()}")
    if data.get("appointment_type"):
        summary_bits.append(f"**Type:** {data['appointment_type'].replace('_', ' ').title()}")

    main, side = st.columns([2, 1]) if ui_v2_enabled() else (st.container(), None)

    with main:
        # Step 0 — Doctor
        if step == 0:
            options = {
                f"{d.get('doctorName') or 'Doctor'} — {d.get('specialization') or 'General'}": d
                for d in doctors
            }
            labels = list(options.keys())
            default_ix = 0
            if data.get("doctor_label") in labels:
                default_ix = labels.index(data["doctor_label"])
            choice = st.selectbox("Choose a doctor", labels, index=default_ix)
            if st.button("Continue", type="primary"):
                doc = options[choice]
                data["doctor_id"] = doc["id"]
                data["doctor_label"] = choice
                data["doctor_fee"] = doc.get("consultationFee")
                st.session_state.book_step = 1
                st.rerun()

        # Step 1 — Date & time (no invented free slots — user picks; backend validates)
        elif step == 1:
            st.caption(
                "Select a preferred date and time. Final availability is confirmed by the server "
                "when you submit."
            )
            col1, col2 = st.columns(2)
            min_d = date.today()
            max_d = date.today() + timedelta(days=90)
            appt_date = col1.date_input(
                "Date",
                value=date.fromisoformat(data["date"]) if data.get("date") else min_d,
                min_value=min_d,
                max_value=max_d,
            )
            appt_time = col2.time_input(
                "Time",
                value=time.fromisoformat(data["time"]) if data.get("time") else time(9, 0),
            )
            c1, c2 = st.columns(2)
            if c1.button("Back"):
                st.session_state.book_step = 0
                st.rerun()
            if c2.button("Continue", type="primary"):
                if appt_date < date.today():
                    st.error("Choose today or a future date.")
                else:
                    dt = datetime.combine(appt_date, appt_time)
                    data["date"] = appt_date.isoformat()
                    data["time"] = appt_time.isoformat()
                    data["datetime_iso"] = dt.isoformat()
                    st.session_state.book_step = 2
                    st.rerun()

        # Step 2 — Details
        elif step == 2:
            consultation_type = st.radio(
                "Consultation type",
                ["IN_PERSON", "TELEMEDICINE"],
                index=0 if data.get("consultation_type", "IN_PERSON") == "IN_PERSON" else 1,
                horizontal=True,
                format_func=lambda x: x.replace("_", " ").title(),
            )
            appointment_type = st.selectbox(
                "Appointment type",
                ["CONSULTATION", "FOLLOW_UP", "EMERGENCY"],
                index=["CONSULTATION", "FOLLOW_UP", "EMERGENCY"].index(
                    data.get("appointment_type", "CONSULTATION")
                ),
            )
            chief = st.text_input("Chief complaint", value=data.get("chief_complaint", ""))
            symptoms = st.text_area("Symptoms (optional)", value=data.get("symptoms", ""))
            c1, c2 = st.columns(2)
            if c1.button("Back"):
                st.session_state.book_step = 1
                st.rerun()
            if c2.button("Continue", type="primary"):
                if not chief.strip():
                    st.error("Chief complaint is required.")
                else:
                    data.update(
                        {
                            "consultation_type": consultation_type,
                            "appointment_type": appointment_type,
                            "chief_complaint": chief.strip(),
                            "symptoms": symptoms.strip(),
                        }
                    )
                    st.session_state.book_step = 3
                    st.rerun()

        # Step 3 — Confirm
        else:
            st.markdown("**Confirm booking**")
            st.write(f"**Doctor:** {data.get('doctor_label')}")
            st.write(f"**When:** {data.get('datetime_iso')}")
            st.write(f"**Mode:** {_na(data.get('consultation_type')).replace('_', ' ').title()}")
            st.write(f"**Type:** {_na(data.get('appointment_type')).replace('_', ' ').title()}")
            st.write(f"**Complaint:** {data.get('chief_complaint')}")
            if data.get("symptoms"):
                st.write(f"**Symptoms:** {data['symptoms']}")
            if data.get("doctor_fee") is not None:
                st.write(f"**Listed fee:** ₹{data['doctor_fee']}")

            c1, c2 = st.columns(2)
            if c1.button("Back"):
                st.session_state.book_step = 2
                st.rerun()
            if c2.button("Book appointment", type="primary"):
                payload = {
                    "patientId": patient["id"],
                    "doctorId": data["doctor_id"],
                    "appointmentDateTime": data["datetime_iso"],
                    "chiefComplaint": data.get("chief_complaint"),
                    "symptoms": data.get("symptoms") or "",
                    "consultationType": data.get("consultation_type"),
                    "appointmentType": data.get("appointment_type"),
                    "durationMinutes": 30,
                }
                result = api_client.create_appointment(payload)
                if result.get("success"):
                    st.success("Appointment booked successfully.")
                    announce("Appointment booked successfully.")
                    data_cache.clear_data_caches()
                    st.session_state.book_step = 0
                    st.session_state.book_data = {}
                    st.balloons()
                    st.rerun()
                else:
                    error_state(
                        result.get("message") or "Booking failed",
                        detail="The server rejected this slot or request. Adjust details and try again.",
                    )

    if side is not None:
        with side:
            st.markdown("#### Summary")
            if summary_bits:
                for b in summary_bits:
                    st.markdown(b)
            else:
                st.caption("Your selections will appear here.")


def _patient_my_appointments(patient: dict) -> None:
    appt_resp = data_cache.get_patient_appointments(patient["id"])
    appointments = appt_resp.get("data") or [] if appt_resp.get("success") else []
    if not appt_resp.get("success") and appt_resp.get("message"):
        error_state("Could not load appointments", detail=appt_resp.get("message"))
        return

    if not appointments:
        empty_state(
            "No appointments yet",
            description="Use the Book tab to schedule your first visit.",
            icon_name="calendar",
        )
        return

    now = datetime.now()
    upcoming, past, cancelled = [], [], []
    for a in appointments:
        status = (a.get("status") or "").upper()
        if status in ("CANCELLED", "NO_SHOW"):
            cancelled.append(a)
        else:
            raw = a.get("appointmentDateTime") or ""
            try:
                dt = datetime.fromisoformat(raw.replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                dt = None
            if status == "COMPLETED" or (dt and dt < now):
                past.append(a)
            else:
                upcoming.append(a)

    seg = st.radio(
        "View",
        ["Upcoming", "Past", "Cancelled"],
        horizontal=True,
        label_visibility="collapsed",
    )
    bucket = {"Upcoming": upcoming, "Past": past, "Cancelled": cancelled}[seg]
    if not bucket:
        empty_state(f"No {seg.lower()} appointments", icon_name="calendar")
        return

    for a in sorted(bucket, key=lambda x: x.get("appointmentDateTime") or "", reverse=(seg != "Upcoming")):
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            doctor_label = _na(a.get("doctorName"), f"Doctor #{a.get('doctorId')}")
            c1.markdown(f"**{doctor_label}**")
            c1.caption(_na(a.get("appointmentDateTime")))
            if a.get("chiefComplaint"):
                c1.write(a["chiefComplaint"])
            if ui_v2_enabled():
                c2.markdown(status_badge(a.get("status")), unsafe_allow_html=True)
            else:
                c2.write(a.get("status"))


def _clinician_schedule(user: dict) -> None:
    doctor_resp = data_cache.get_doctor_by_user_id(user["id"])
    doctor = doctor_resp.get("data") if doctor_resp.get("success") else None
    if not doctor:
        empty_state(
            "No doctor profile linked",
            description="Complete your profile in Settings to see your schedule.",
            icon_name="stethoscope",
        )
        st.page_link("pages/4_Settings.py", label="Settings")
        return

    appt_resp = data_cache.get_doctor_appointments(doctor["id"])
    appointments = appt_resp.get("data") or [] if appt_resp.get("success") else []
    if not appointments:
        empty_state("No appointments found", icon_name="calendar")
        return

    statuses = ["SCHEDULED", "CONFIRMED", "IN_PROGRESS", "COMPLETED", "CANCELLED", "NO_SHOW"]
    for appt in sorted(appointments, key=lambda a: a.get("appointmentDateTime") or ""):
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 2])
            patient_label = appt.get("patientName") or f"Patient #{appt.get('patientId')}"
            c1.markdown(f"**{patient_label}**")
            c1.caption(appt.get("chiefComplaint") or "")
            if ui_v2_enabled():
                c2.markdown(status_badge(appt.get("status")), unsafe_allow_html=True)
            else:
                c2.write(appt.get("status"))
            c2.caption(_na(appt.get("appointmentDateTime")))

            cur = appt.get("status") or "SCHEDULED"
            idx = statuses.index(cur) if cur in statuses else 0
            new_status = c3.selectbox(
                "Status",
                statuses,
                index=idx,
                key=f"status-{appt['id']}",
                label_visibility="collapsed",
            )
            if new_status != cur and c3.button("Update", key=f"update-{appt['id']}"):
                # Confirm destructive-ish transitions
                if new_status in ("CANCELLED", "NO_SHOW", "COMPLETED"):
                    st.session_state[f"confirm_{appt['id']}"] = new_status
                else:
                    result = api_client.update_appointment_status(appt["id"], new_status)
                    if result.get("success"):
                        data_cache.clear_data_caches()
                        st.rerun()
                    else:
                        error_state(result.get("message") or "Update failed")

            pending = st.session_state.get(f"confirm_{appt['id']}")
            if pending:
                st.warning(f"Confirm status change to **{pending.replace('_', ' ').title()}**?")
                yes, no = st.columns(2)
                if yes.button("Confirm", key=f"yes-{appt['id']}", type="primary"):
                    result = api_client.update_appointment_status(appt["id"], pending)
                    st.session_state.pop(f"confirm_{appt['id']}", None)
                    if result.get("success"):
                        data_cache.clear_data_caches()
                        st.rerun()
                    else:
                        error_state(result.get("message") or "Update failed")
                if no.button("Cancel", key=f"no-{appt['id']}"):
                    st.session_state.pop(f"confirm_{appt['id']}", None)
                    st.rerun()


def _content(user: dict) -> None:
    if user["role"] == "PATIENT":
        profile_resp = data_cache.get_patient_by_user_id(user["id"])
        patient = profile_resp.get("data") if profile_resp.get("success") else None
        if not patient:
            st.warning("Complete your patient profile before booking an appointment.")
            st.page_link("pages/4_Settings.py", label="Go to Settings")
            return
        tab_book, tab_mine = st.tabs(["Book appointment", "My appointments"])
        with tab_book:
            _patient_booking(patient)
        with tab_mine:
            _patient_my_appointments(patient)

    elif user["role"] in ("DOCTOR", "ASSISTANT_DOCTOR", "SURGEON"):
        _clinician_schedule(user)

    else:
        st.info("Admin appointment oversight — use the Directory to find a clinician’s schedule.")


# ---------------------------------------------------------------------------
if ui_v2_enabled():
    with render_shell(
        "Appointments",
        active_page="2_Appointments.py",
        breadcrumbs=["Home", "Appointments"],
    ):
        _content(auth.current_user())
else:
    apply_theme()
    auth.require_login()
    user = auth.current_user()
    with st.sidebar:
        st.markdown(f"### {user.get('firstName', '')} {user.get('lastName', '')}")
        st.caption(user.get("role", "").replace("_", " ").title())
        if st.button("Log Out", use_container_width=True):
            auth.logout_user()
            st.switch_page("Home.py")
    st.title("Appointments")
    _content(user)
