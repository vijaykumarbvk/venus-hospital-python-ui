# QA report — Venus UI transformation (Phases 0–10)

**Date:** 2026-09-23  
**Streamlit:** 1.38.0  
**Flag:** `VENUS_UI_V2`

## Unit tests

| Suite | Result |
|-------|--------|
| `tests/test_html_esc.py` | Pass (escaping, attrs, class_names) |
| `tests/test_nav.py` | Pass (role → nav map) |
| `tests/test_error_ref.py` | Pass (reference id shape) |
| **Total** | **8 passed** |

## Automated not run in this environment

| Suite | Reason | Recommendation |
|-------|--------|----------------|
| Playwright E2E | No live stack / browser harness here | Run against staging with flag on |
| Visual regression | No screenshot baseline CI | Capture Login + each role dashboard × light/dark × 390/1280 |
| axe-core | Needs browser | Attach to Playwright |
| Lighthouse | Needs deployed URL | Login + Dashboard; compare to pre-v2 baseline |

## Manual review (code-level)

- No fabricated clinical metrics in dashboards (Phase 5 audit).
- `esc()` required for dynamic HTML; hostile-string unit tests present.
- API surface unchanged: same paths and payloads as original `api_client`.
- Backend / `services/` / `k8s-*` / Terraform not modified in UI phases.

## Risks remaining

1. Streamlit internal CSS selectors may shift on major upgrades → isolated in `20_streamlit_overrides.css`.
2. Assistant/Surgeon specialty UIs limited by missing APIs.
3. Refresh token stored but unused (pre-existing).

## Sign-off criteria

- [ ] Staging QA checklist in `rollout.md` completed  
- [ ] Flag-off regression smoke passed  
- [ ] Product accepts honest empty states for OT/tasks/health  
