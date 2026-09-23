# Component architecture summary

```
streamlit_app/
├── Home.py                 # Auth entry (v2 split-screen + stepper | legacy)
├── pages/                  # Thin orchestration + shell
├── ui/
│   ├── theme.py            # Flag, CSS once, density/theme session
│   ├── tokens.py           # Chart color mirrors
│   ├── html.py             # esc / attr / class_names
│   ├── icons.py            # Inline SVG registry
│   ├── a11y.py             # announce, sr_only
│   ├── shell/              # nav, sidebar, header, page_frame
│   └── components/         # kpi, badge, empty, error, skeleton, loading, api_feedback
├── styles/                 # 00 tokens → 60 motion
├── utils/
│   ├── api_client.py       # HTTP + error_code
│   ├── data_cache.py       # 30s TTL reads
│   ├── auth.py             # session + expiry UI hook
│   └── dashboards.py       # Role views (real data only)
└── tests/
```

**Data flow:** Page → (optional cache) → `api_client` → gateway → view rendering via components.  
**No** mixing of raw HTML strings with unescaped API fields in v2 paths.

## Files created (UI phases)

- `docs/ui/*` (audit, design system, motion, a11y, limitations, performance, rollout, QA, architecture)
- `styles/*.css`, `ui/**`, `utils/data_cache.py`, `tests/test_*`, `.streamlit/config.toml`, `CHANGELOG-UI.md`

## Files modified (presentation)

- `Home.py`, `pages/*.py`, `utils/dashboards.py`, `utils/api_client.py`, `utils/auth.py`

## Explicitly not modified

- `services/**`, `EKS-Terraform/**`, `k8s-*/**`, Dockerfiles for services, CI workflows, database schemas
