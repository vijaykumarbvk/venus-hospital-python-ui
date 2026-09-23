"""Status badge — icon + text, never color-only."""
from __future__ import annotations

from ui.html import esc, class_names
from ui.icons import icon

STATUS_LABELS = {
    "SCHEDULED": ("info", "Scheduled"),
    "CONFIRMED": ("info", "Confirmed"),
    "IN_PROGRESS": ("warning", "In progress"),
    "COMPLETED": ("success", "Completed"),
    "CANCELLED": ("critical", "Cancelled"),
    "NO_SHOW": ("neutral", "No show"),
    "AVAILABLE": ("success", "Available"),
    "IN_USE": ("critical", "In use"),
    "MAINTENANCE": ("warning", "Maintenance"),
    "ACTIVE": ("success", "Active"),
    "INACTIVE": ("neutral", "Inactive"),
}

_ICON_FOR = {
    "success": "check",
    "warning": "alert-circle",
    "critical": "x",
    "info": "clock",
    "neutral": "activity",
}


def status_badge(status: str | None, *, label: str | None = None) -> str:
    """Return HTML for a status badge. Safe for markdown injection."""
    key = (status or "").upper().replace(" ", "_")
    variant, default_label = STATUS_LABELS.get(key, ("neutral", (status or "Unknown").replace("_", " ").title()))
    text = label or default_label
    ic = icon(_ICON_FOR.get(variant, "activity"), size=14)
    cls = class_names("venus-badge", f"venus-badge--{variant}")
    return f'<span class="{cls}">{ic} {esc(text)}</span>'
