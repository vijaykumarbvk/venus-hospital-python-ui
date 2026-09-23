"""
Directory — Phase 6.
Search + specialization filters; optional query-param persistence when V2.
Role-gated patient list. Real API data only.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
import streamlit as st

from ui.components import empty_state, permission_denied
from ui.shell import render_shell
from ui.theme import apply_theme, ui_v2_enabled
from utils import api_client, auth
from utils import data_cache

st.set_page_config(page_title="Directory | Venus Hospital", page_icon="👥", layout="wide")


def _na(v, fallback="Not available"):
    return fallback if v is None or v == "" else v


def _content(user: dict) -> None:
    tab_doctors, tab_patients = st.tabs(["Doctors", "Patients"])

    with tab_doctors:
        doctors_resp = data_cache.get_active_doctors()
        doctors = doctors_resp.get("data") or [] if doctors_resp.get("success") else []

        # Query-param restore (V2)
        qp_spec = ""
        qp_q = ""
        if ui_v2_enabled():
            try:
                params = st.query_params
                qp_spec = params.get("spec", "") or ""
                qp_q = params.get("q", "") or ""
            except Exception:
                pass

        specializations = sorted(
            {d.get("specialization") for d in doctors if d.get("specialization")}
        )

        c1, c2 = st.columns([2, 2])
        q = c1.text_input(
            "Search by name or department",
            value=qp_q,
            placeholder="Type a name or department",
        )
        default_specs = [s for s in specializations if s and s in qp_spec.split(",")] if qp_spec else []
        chosen = c2.multiselect(
            "Specialization",
            specializations,
            default=default_specs,
        )

        if ui_v2_enabled():
            # Persist filters in URL for shareable views
            try:
                new_params = {}
                if q:
                    new_params["q"] = q
                if chosen:
                    new_params["spec"] = ",".join(chosen)
                st.query_params.clear()
                for k, v in new_params.items():
                    st.query_params[k] = v
            except Exception:
                pass

        q_lower = (q or "").strip().lower()
        filtered = []
        for d in doctors:
            if chosen and d.get("specialization") not in chosen:
                continue
            if q_lower:
                hay = " ".join(
                    [
                        str(d.get("doctorName") or ""),
                        str(d.get("department") or ""),
                        str(d.get("specialization") or ""),
                    ]
                ).lower()
                if q_lower not in hay:
                    continue
            filtered.append(d)

        view = st.radio("Layout", ["Table", "Cards"], horizontal=True) if ui_v2_enabled() else "Table"

        if not filtered:
            empty_state("No doctors match this filter", icon_name="users")
        elif view == "Cards" and ui_v2_enabled():
            cols = st.columns(2)
            for i, d in enumerate(filtered):
                with cols[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"**{_na(d.get('doctorName'))}**")
                        st.caption(_na(d.get("specialization")))
                        st.write(f"Department: {_na(d.get('department'))}")
                        exp = d.get("experienceYears")
                        st.write(
                            f"Experience: {exp} years"
                            if exp is not None
                            else "Experience: Not available"
                        )
                        fee = d.get("consultationFee")
                        st.write(f"Fee: ₹{fee}" if fee is not None else "Fee: Not available")
                        st.write(
                            "Telemedicine: Yes"
                            if d.get("availableForTelemedicine")
                            else "Telemedicine: No"
                        )
        else:
            df = pd.DataFrame(
                [
                    {
                        "Name": _na(d.get("doctorName")),
                        "Specialization": _na(d.get("specialization")),
                        "Department": _na(d.get("department")),
                        "Experience (yrs)": d.get("experienceYears")
                        if d.get("experienceYears") is not None
                        else "Not available",
                        "Fee": d.get("consultationFee")
                        if d.get("consultationFee") is not None
                        else "Not available",
                        "Telemedicine": "Yes" if d.get("availableForTelemedicine") else "No",
                    }
                    for d in filtered
                ]
            )
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"{len(filtered)} doctor(s)")

    with tab_patients:
        if user["role"] not in ("ADMIN", "DOCTOR", "ASSISTANT_DOCTOR", "SURGEON"):
            permission_denied("You don't have permission to view the patient directory.")
            return

        patients_resp = data_cache.get_active_patients()
        patients = patients_resp.get("data") or [] if patients_resp.get("success") else []
        pq = st.text_input("Search patients by name or city", key="patient_q")
        pq_lower = (pq or "").strip().lower()
        if pq_lower:
            patients = [
                p
                for p in patients
                if pq_lower
                in " ".join(
                    [str(p.get("patientName") or ""), str(p.get("city") or "")]
                ).lower()
            ]

        if patients:
            df = pd.DataFrame(
                [
                    {
                        "Name": _na(p.get("patientName")),
                        "Age": p.get("age") if p.get("age") is not None else "Not available",
                        "Gender": _na(p.get("gender")),
                        "Blood Group": _na(p.get("bloodGroup")),
                        "City": _na(p.get("city")),
                    }
                    for p in patients
                ]
            )
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"{len(patients)} patient(s)")
        else:
            empty_state("No patients match this view", icon_name="users")


if ui_v2_enabled():
    with render_shell("Directory", active_page="3_Directory.py", breadcrumbs=["Home", "Directory"]):
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
    st.title("Directory")
    _content(user)
