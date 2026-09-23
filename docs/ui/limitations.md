# Streamlit constraints & workarounds

Documented as of Streamlit **1.38** and Venus UI Phases 0–8.

| Constraint | Impact | Workaround |
|------------|--------|------------|
| No true fixed app chrome outside Streamlit’s layout | Custom shell can shift on rerun | Inject CSS once per session; `page_frame` standardizes structure |
| Sidebar control is limited | Cannot fully replace Streamlit sidebar | Style via `20_streamlit_overrides.css`; role nav via `st.page_link` |
| Global keyboard shortcuts fragile | Cmd+K palette hard | Visible search / filters; document fallback |
| JS in `st.markdown` does not run (sanitized) | No DOM hacks in markdown | Pure CSS animations; minimal script only in preloader hide |
| `st.components.v1.html` is iframe-sandboxed | No parent DOM access | Avoid for core shell |
| Rerun model | Full script re-exec | Session state for wizards; fragments later if needed |
| Token refresh not implemented in UI | Session ends on 401 | Designed session-expiry screen |
| No surgery / OT / assistant-task APIs | Those dashboards stay minimal | Honest empty states (Phase 5) |
| Brittle internal CSS selectors | Breaks on Streamlit upgrades | Confine to `20_streamlit_overrides.css` only |

## Responsive strategy

| Width | Layout behaviour |
|-------|------------------|
| ≥1280 | 4-col KPI grids, split auth |
| ≤1023 | 2-col grids, stacked auth |
| ≤767 | 1-col grids, tighter touch targets, wrap long strings |
| ≤390 | Slight preloader scale-down |

## Future migration note

A dedicated SPA (e.g. Next.js) would improve fixed shell, global shortcuts, and offline PWA. Not required until clinical users outgrow Streamlit limits in production.
