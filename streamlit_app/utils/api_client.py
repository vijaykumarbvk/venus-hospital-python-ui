"""
Thin requests-based client for the Venus Hospital API Gateway.
Phase 7: clearer 401 / network handling for UI states (no contract change).
"""
from __future__ import annotations

import os
from typing import Any

import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8080")


def _headers() -> dict:
    headers = {"Content-Type": "application/json"}
    token = st.session_state.get("token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _request(method: str, path: str, **kwargs) -> dict:
    url = f"{API_BASE_URL}{path}"
    try:
        resp = requests.request(method, url, headers=_headers(), timeout=10, **kwargs)
    except requests.Timeout:
        return {
            "success": False,
            "message": "The server took too long to respond.",
            "data": None,
            "error_code": "TIMEOUT",
        }
    except requests.RequestException as exc:
        # Do not surface internal exception strings that might leak hosts
        return {
            "success": False,
            "message": "We can't reach the server right now.",
            "data": None,
            "error_code": "NETWORK",
        }

    if resp.status_code == 401:
        st.session_state.pop("token", None)
        st.session_state.pop("user", None)
        st.session_state["_venus_session_expired"] = True
        return {
            "success": False,
            "message": "Your session has expired. Please sign in again.",
            "data": None,
            "error_code": "UNAUTHORIZED",
        }

    if resp.status_code == 403:
        return {
            "success": False,
            "message": "You don't have permission for this action.",
            "data": None,
            "error_code": "FORBIDDEN",
        }

    try:
        body = resp.json()
        if isinstance(body, dict):
            body.setdefault("error_code", None)
            return body
        return {"success": True, "data": body, "error_code": None}
    except ValueError:
        return {
            "success": False,
            "message": f"Unexpected response ({resp.status_code})",
            "data": None,
            "error_code": "BAD_RESPONSE",
        }


# Auth
def login(username: str, password: str) -> dict:
    return _request("POST", "/api/users/login", json={"username": username, "password": password})


def register(payload: dict) -> dict:
    return _request("POST", "/api/users/register", json=payload)


# Users
def get_user(user_id: int) -> dict:
    return _request("GET", f"/api/users/{user_id}")


def get_active_users() -> dict:
    return _request("GET", "/api/users/active")


# Doctors
def create_doctor(payload: dict) -> dict:
    return _request("POST", "/api/doctors", json=payload)


def get_doctor_by_user_id(user_id: int) -> dict:
    return _request("GET", f"/api/doctors/user/{user_id}")


def get_active_doctors() -> dict:
    return _request("GET", "/api/doctors/active")


def get_doctors_by_specialization(specialization: str) -> dict:
    return _request("GET", f"/api/doctors/specialization/{specialization}")


# Patients
def create_patient(payload: dict) -> dict:
    return _request("POST", "/api/patients", json=payload)


def get_patient_by_user_id(user_id: int) -> dict:
    return _request("GET", f"/api/patients/user/{user_id}")


def get_active_patients() -> dict:
    return _request("GET", "/api/patients/active")


# Appointments
def create_appointment(payload: dict) -> dict:
    return _request("POST", "/api/appointments", json=payload)


def get_patient_appointments(patient_id: int) -> dict:
    return _request("GET", f"/api/appointments/patient/{patient_id}")


def get_doctor_appointments(doctor_id: int) -> dict:
    return _request("GET", f"/api/appointments/doctor/{doctor_id}")


def update_appointment_status(appointment_id: int, status: str) -> dict:
    return _request(
        "PATCH",
        f"/api/appointments/{appointment_id}/status",
        params={"status": status},
    )


def cancel_appointment(appointment_id: int, reason: str) -> dict:
    return _request(
        "DELETE",
        f"/api/appointments/{appointment_id}",
        params={"reason": reason},
    )
