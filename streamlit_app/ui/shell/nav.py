"""
Single source of truth: role → navigation items.
Mirrors backend permission model. UI hides what the role must not see;
backend still enforces access.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NavItem:
    label: str
    page: str          # Streamlit page path relative to streamlit_app/
    icon: str          # key in ui.icons
    section: str       # group label in sidebar
    roles: tuple[str, ...]  # empty = all authenticated


# page paths match existing multipage files
NAV_ITEMS: tuple[NavItem, ...] = (
    NavItem("Dashboard", "pages/1_Dashboard.py", "home", "Main", ()),
    NavItem("Appointments", "pages/2_Appointments.py", "calendar", "Main", ()),
    NavItem("Directory", "pages/3_Directory.py", "users", "Main", ()),
    NavItem("Settings", "pages/4_Settings.py", "settings", "Account", ()),
)

# Explicit map for clarity / tests
NAV_BY_ROLE: dict[str, tuple[str, ...]] = {
    "PATIENT": ("Dashboard", "Appointments", "Directory", "Settings"),
    "DOCTOR": ("Dashboard", "Appointments", "Directory", "Settings"),
    "ASSISTANT_DOCTOR": ("Dashboard", "Appointments", "Directory", "Settings"),
    "SURGEON": ("Dashboard", "Appointments", "Directory", "Settings"),
    "ADMIN": ("Dashboard", "Appointments", "Directory", "Settings"),
}


def nav_items_for_role(role: str) -> list[NavItem]:
    allowed = set(NAV_BY_ROLE.get(role, ()))
    return [item for item in NAV_ITEMS if not allowed or item.label in allowed]
