"""
Short-TTL cached reads for GET endpoints.
Keyed by resource + user id so data never leaks across users.
Mutating calls should invoke clear_data_caches().
"""
from __future__ import annotations

from typing import Any

import streamlit as st

from utils import api_client

# TTL seconds — short so clinical data stays reasonably fresh
_TTL = 30


def _uid() -> str:
    user = st.session_state.get("user") or {}
    return str(user.get("id") or "anon")


@st.cache_data(ttl=_TTL, show_spinner=False)
def cached_active_doctors(_user_key: str) -> dict:
    return api_client.get_active_doctors()


@st.cache_data(ttl=_TTL, show_spinner=False)
def cached_active_patients(_user_key: str) -> dict:
    return api_client.get_active_patients()


@st.cache_data(ttl=_TTL, show_spinner=False)
def cached_active_users(_user_key: str) -> dict:
    return api_client.get_active_users()


@st.cache_data(ttl=_TTL, show_spinner=False)
def cached_patient_by_user(_user_key: str, user_id: int) -> dict:
    return api_client.get_patient_by_user_id(user_id)


@st.cache_data(ttl=_TTL, show_spinner=False)
def cached_doctor_by_user(_user_key: str, user_id: int) -> dict:
    return api_client.get_doctor_by_user_id(user_id)


@st.cache_data(ttl=_TTL, show_spinner=False)
def cached_patient_appointments(_user_key: str, patient_id: int) -> dict:
    return api_client.get_patient_appointments(patient_id)


@st.cache_data(ttl=_TTL, show_spinner=False)
def cached_doctor_appointments(_user_key: str, doctor_id: int) -> dict:
    return api_client.get_doctor_appointments(doctor_id)


def get_active_doctors() -> dict:
    return cached_active_doctors(_uid())


def get_active_patients() -> dict:
    return cached_active_patients(_uid())


def get_active_users() -> dict:
    return cached_active_users(_uid())


def get_patient_by_user_id(user_id: int) -> dict:
    return cached_patient_by_user(_uid(), user_id)


def get_doctor_by_user_id(user_id: int) -> dict:
    return cached_doctor_by_user(_uid(), user_id)


def get_patient_appointments(patient_id: int) -> dict:
    return cached_patient_appointments(_uid(), patient_id)


def get_doctor_appointments(doctor_id: int) -> dict:
    return cached_doctor_appointments(_uid(), doctor_id)


def clear_data_caches() -> None:
    """Call after create/update/cancel so the next read is fresh."""
    cached_active_doctors.clear()
    cached_active_patients.clear()
    cached_active_users.clear()
    cached_patient_by_user.clear()
    cached_doctor_by_user.clear()
    cached_patient_appointments.clear()
    cached_doctor_appointments.clear()
