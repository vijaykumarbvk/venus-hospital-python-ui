# Rollout guide — Venus UI v2

## Feature flag

```bash
export VENUS_UI_V2=1
streamlit run streamlit_app/Home.py
```

Or in Kubernetes / Docker:

```yaml
env:
  - name: VENUS_UI_V2
    value: "1"
  - name: API_BASE_URL
    value: "http://api-gateway:80"
```

When **unset**, the classic UI runs (rollback with zero code change).

## Recommended rollout steps

1. Deploy image with UI v2 code but **flag off** in production.
2. Enable `VENUS_UI_V2=1` in a staging namespace; run QA checklist below.
3. Enable for a small user cohort (or single role) if your platform supports env per deployment.
4. Full enable after sign-off; keep flag for one release cycle before removing dead legacy branches (optional cleanup later).

## QA checklist (manual)

### Auth
- [ ] Register stepper (all 4 steps, back/next, validation)
- [ ] Login success → Dashboard
- [ ] Login failure shows clear message (no account enumeration)
- [ ] Logout returns to Home; preloader can show again on next cold session

### Roles
- [ ] Patient dashboard: real KPIs / empty states; no fake stats
- [ ] Doctor: today’s schedule + status advance
- [ ] Assistant / Surgeon: no fabricated OT/tasks; honest empty copy
- [ ] Admin: real counts; “Health data unavailable” (not fake greens)

### Flows
- [ ] Book appointment wizard → success toast/live region
- [ ] My appointments segments (Upcoming / Past / Cancelled)
- [ ] Clinician status → confirm for CANCELLED / NO_SHOW / COMPLETED
- [ ] Directory search + specialization filter + cards/table
- [ ] Settings profile create + theme/density preferences

### States
- [ ] Stop API / wrong `API_BASE_URL` → offline message
- [ ] Expired token path → session expired UI
- [ ] Permission on patient directory as PATIENT → denied state

### A11y / responsive
- [ ] Keyboard-only login and booking
- [ ] 390px and 1280px widths, no horizontal scroll
- [ ] `prefers-reduced-motion`: static preloader

### Regression
- [ ] Flag **off**: classic Home + pages still work
- [ ] Backend services / k8s manifests unchanged

## Rollback

```bash
unset VENUS_UI_V2
# or set value to "0"
```

Redeploy not required if flag is env-only.

## Removing the flag (later)

Only after sustained production confidence: delete legacy branches in `Home.py` / pages and make v2 the default. Not required for this release.
