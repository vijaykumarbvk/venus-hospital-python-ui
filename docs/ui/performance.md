# Performance notes (Phase 9)

## Budgets (targets)

| Asset | Target | Measured (approx, uncompressed) |
|-------|--------|----------------------------------|
| CSS bundle (all layers) | &lt; 60 KB gzipped | ~34 KB raw → well under gzip budget |
| Preloader (CSS + SVG in loading.py) | &lt; 20 KB | ~12 KB combined raw |
| New runtime deps | None beyond Streamlit/pandas/requests | Met |

## Strategies applied

1. **CSS loaded once per process** — `st.cache_resource` in `ui/theme.py` (`_load_css_bundle`).
2. **GET caching** — `utils/data_cache.py` wraps list/detail GETs with `st.cache_data(ttl=30)` keyed by session user id so data never crosses users.
3. **Cache invalidation** — `clear_data_caches()` after book, status update, and profile create.
4. **Preloader once per session** — session_state guard; not on every navigation.
5. **No layout-shifting ads/images** — skeletons reserve approximate space; no external font CDN required (system stack fallback).

## What we did not add

- No new animation libraries  
- No client-side SPA framework  
- No aggressive infinite caching of clinical data (30s TTL keeps lists fresh enough)

## Recommended local checks

```bash
# CSS size
find streamlit_app/styles -name '*.css' | xargs cat | wc -c

# Gzip estimate
find streamlit_app/styles -name '*.css' | xargs cat | gzip -c | wc -c
```

Lighthouse (Login + Dashboard) should be run in a real browser against a running stack; document before/after in QA (Phase 10).

## Streamlit rerun cost

Each widget interaction re-runs the script. Caching GETs reduces duplicate network work within the TTL window. Wizards keep state in `st.session_state` so steps do not refetch unnecessarily beyond the cached helpers.
