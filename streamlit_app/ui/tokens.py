"""
Python mirrors of design tokens for charts and programmatic use.
CSS remains the source of truth for layout/chrome.
"""

# Primitive
NAVY_900 = "#0B1F33"
NAVY_800 = "#102A43"
BLUE_600 = "#1677FF"
BLUE_700 = "#2563EB"
TEAL_500 = "#14B8A6"
SLATE_50 = "#F8FAFC"
SLATE_500 = "#64748B"
SLATE_700 = "#334155"
SLATE_900 = "#0F172A"
WHITE = "#FFFFFF"

# Status (light)
STATUS_SUCCESS = "#15803D"
STATUS_WARNING = "#B45309"
STATUS_CRITICAL = "#B91C1C"
STATUS_INFO = "#1D4ED8"

# Chart-safe sequential palette (color-blind friendly-ish)
CHART_SERIES = [
    "#1677FF",  # medical blue
    "#14B8A6",  # teal
    "#6366F1",  # indigo
    "#F59E0B",  # amber
    "#EC4899",  # pink
    "#64748B",  # slate
]

CHART_STATUS = {
    "SCHEDULED": "#3B82F6",
    "CONFIRMED": "#8B5CF6",
    "IN_PROGRESS": "#F59E0B",
    "COMPLETED": "#16A34A",
    "CANCELLED": "#DC2626",
    "NO_SHOW": "#94A3B8",
}
