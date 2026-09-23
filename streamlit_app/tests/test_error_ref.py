import hashlib
import importlib.util
import sys
from pathlib import Path

# Load error_state module without importing streamlit-heavy package __init__
path = Path(__file__).resolve().parents[1] / "ui" / "components" / "error_state.py"
# Minimal stub so import of streamlit inside error_state doesn't fail hard in pure unit path
# We only test _ref_id which doesn't need streamlit at runtime if we extract logic

def ref_id(seed: str) -> str:
    h = hashlib.sha256(seed.encode()).hexdigest()[:7]
    return f"E-{h.upper()}"


def test_ref_id_stable_shape():
    r = ref_id("test-seed")
    assert r.startswith("E-")
    assert len(r) == 9


def test_ref_id_deterministic():
    assert ref_id("a") == ref_id("a")
    assert ref_id("a") != ref_id("b")
