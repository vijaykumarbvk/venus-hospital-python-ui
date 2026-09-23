import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ui.shell.nav import NAV_BY_ROLE, nav_items_for_role, NAV_ITEMS


def test_all_roles_have_nav():
    for role in ("PATIENT", "DOCTOR", "ASSISTANT_DOCTOR", "SURGEON", "ADMIN"):
        items = nav_items_for_role(role)
        assert len(items) >= 1
        labels = {i.label for i in items}
        assert "Dashboard" in labels
        assert "Settings" in labels


def test_nav_items_stable():
    assert len(NAV_ITEMS) == 4
    assert set(NAV_BY_ROLE.keys()) >= {"PATIENT", "DOCTOR", "ADMIN"}
