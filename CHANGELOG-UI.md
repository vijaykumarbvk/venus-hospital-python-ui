# UI Changelog

## [Unreleased]

### Phase 0 — Audit (2026-09-23)
- Added `docs/ui/00-audit.md` with inventory, API table, Streamlit capability matrix, and architecture decision (stay on Streamlit).

### Phase 1 — Tokens & theme (2026-09-23)
- Design system documented in `docs/ui/DESIGN_SYSTEM.md`.
- CSS layers: `styles/00_tokens.css` … `60_motion.css`.
- Python: `ui/tokens.py`, `ui/theme.py`, `ui/html.py` (esc), `ui/icons.py`.
- Feature flag `VENUS_UI_V2=1` gates new styles (`ui.theme.ui_v2_enabled` / `apply_theme`).
- Streamlit theme baseline: `.streamlit/config.toml`.
- Unit tests: `tests/test_html_esc.py`.
- **No backend, auth, Docker, K8s, or CI files modified.**

### Phase 2 — Shell & primitives (2026-09-23)
- `ui/shell/`: nav map, sidebar (brand, role chip, nav, user card, logout), header (greeting, date, breadcrumbs), page_frame + error boundary.
- `ui/components/`: kpi_card, status_badge, empty_state, error_state, permission_denied, skeleton.
- Protected pages (Dashboard, Appointments, Directory, Settings) use shell when `VENUS_UI_V2=1`; legacy UI when flag is off.
- Settings → Preferences: theme + density session controls.
- Unit tests: nav map + esc.
- **No backend / infra changes.**

### Phase 3 — Preloader & motion (2026-09-23)
- `ui/components/loading.py`: cold-start preloader (heart, ECG, stethoscope), once per session.
- `styles/60_motion.css`: full timeline, skip control, prefers-reduced-motion path.
- `docs/ui/motion.md`: motion spec table and SVG group map.
- `ui/components/preloader_preview.html`: standalone browser preview.
- Wired into `Home.py` (V2 only); logout resets session flag so next login shows preloader again.
- **No backend / infra changes.**

### Phase 4 — Login & registration (2026-09-23)
- Split-screen landing (brand panel + auth card) when `VENUS_UI_V2=1`.
- Login: username/password with autocomplete attributes, clear non-enumerating errors, Enter-to-submit via form.
- Registration stepper: Account → Personal → Role → Review; state preserved in `st.session_state` across steps.
- No fabricated marketing stats (no "500+ doctors" / "25+ specialties").
- Legacy single-page forms retained when the feature flag is off.
- **No backend / API / auth contract changes.**

### Phase 5 — Role dashboards (2026-09-23)
- Rewrote `utils/dashboards.py` for all roles using real API data only.
- **Removed** fabricated assistant tasks/metrics, surgeon OT/surgery boards, admin always-green service health.
- Patient: KPIs, upcoming list, allergies highlight, profile empty state.
- Doctor: today's schedule, status badges, advance-status actions.
- Assistant / Surgeon: appointments when profile exists; honest empty states for missing APIs.
- Admin: live user/doctor/patient counts; "Health data unavailable" instead of fake greens.
- V2 components (`kpi_row`, `status_badge`, `empty_state`, `error_state`) when flag on.
- **No backend changes.**

### Phase 6 — Appointments, Directory, Settings (2026-09-23)
- Appointments (patient): 4-step booking wizard (Doctor → Date & time → Details → Confirm) with summary panel; segmented My Appointments (Upcoming / Past / Cancelled).
- Appointments (clinician): status updates with confirmation for CANCELLED / NO_SHOW / COMPLETED.
- Directory: name/department search, specialization multiselect, table/cards layout, query-param persistence (`q`, `spec`) when V2.
- Settings: About block under Preferences.
- No invented appointment slots; server remains source of truth for conflicts.
- **No backend changes.**

### Phase 7 — States & skeletons (2026-09-23)
- Expanded `error_state` (reference id + retry), `session_expired`, `offline_state`, `partial_state`.
- Skeletons: list + table shapes; KPI row unchanged.
- `api_client`: TIMEOUT / NETWORK / UNAUTHORIZED / FORBIDDEN error_code; 401 sets session-expired flag.
- `auth.require_login` surfaces designed session-expiry UI.
- `handle_api_error` maps codes to UI states.
- Unit test for error reference id shape.
- **No backend contract changes** (same endpoints and payloads).

### Phase 8 — Responsive & a11y (2026-09-23)
- Expanded `50_responsive.css` (1023 / 767 / 390, safe areas, no horizontal scroll, 44px touch targets).
- `prefers-contrast: more` token adjustments; stronger base focus + `.venus-sr-only` + live region.
- `ui/a11y.py`: `announce`, `sr_only`, `page_h1`.
- Docs: `docs/ui/a11y.md`, `docs/ui/limitations.md`.
- Booking success uses aria-live announcement.
- **No backend changes.**

### Phase 9 — Performance (2026-09-23)
- `utils/data_cache.py`: 30s TTL `st.cache_data` for GETs, keyed by user id; `clear_data_caches()` after mutations.
- Dashboards, Appointments, Directory, Settings use cached reads.
- CSS remains single `cache_resource` load; ~34 KB raw (&lt; 60 KB gzipped budget).
- Docs: `docs/ui/performance.md`.
- **No backend changes.**

### Phase 10 — QA & docs (2026-09-23)
- `docs/ui/rollout.md`, `QA_REPORT.md`, `ARCHITECTURE.md`.
- Unit tests: 8 passed.
- Confirmation: no backend/infra files modified during UI phases 0–10.
- Feature flag remains the supported rollback mechanism.
