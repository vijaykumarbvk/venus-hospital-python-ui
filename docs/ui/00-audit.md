# Phase 0 — Discovery & Feasibility Report

**Project:** Venus Multispecialty Hospital (Streamlit frontend)  
**Audit date:** 2026-09-23  
**Streamlit version pinned:** `1.38.0`  
**Scope:** Presentation layer only.

## A. Inventory (summary)
- Pages: Home.py, 1_Dashboard, 2_Appointments, 3_Directory, 4_Settings
- Auth: session_state token/user; require_login/require_role; no refresh usage
- Roles: PATIENT, DOCTOR, ASSISTANT_DOCTOR, SURGEON, ADMIN
- Fabricated data: ASSISTANT tasks/metrics, SURGEON surgeries/OT, ADMIN system status
- APIs: users, doctors, patients, appointments only (no surgery/OT/tasks/health)

## B. Streamlit 1.38
st.dialog, st.fragment, st.toast, st.popover, st.query_params, theming available.

## C–D. Decision
Stay on Streamlit. Feature-flag VENUS_UI_V2. Confine brittle CSS. No backend changes.

Full detail retained from prior audit session.
