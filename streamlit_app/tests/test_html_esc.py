"""Unit tests for safe HTML helpers — Phase 1 gate."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ui.html import esc, attr, class_names


def test_esc_basic():
    assert esc("hello") == "hello"
    assert esc(None) == ""
    assert esc(42) == "42"


def test_esc_hostile():
    assert esc("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"
    assert esc('"onclick=alert(1)"') == "&quot;onclick=alert(1)&quot;"
    assert esc("a&b") == "a&amp;b"


def test_attr():
    assert ' data-id="1"' in attr("data-id", 1)
    assert attr("hidden", True).strip() == "hidden"
    assert attr("x", None) == ""
    assert attr("x", False) == ""


def test_class_names():
    assert class_names("a", "b", disabled=True) == "a b disabled"
    assert class_names(None, "", active=False) == ""
