# Venus Multispecialty Hospital — Design System

**Version:** 1.0 (Phase 1)  
**Principle:** Clinical clarity over decoration. Real data over mockups. Accessibility and reliability over animation.

---

## 1. Three-tier tokens

| Tier | Prefix examples | Who consumes |
|------|-----------------|--------------|
| Primitive | `--navy-900`, `--teal-500`, `--space-4` | Only semantic tokens and rare one-offs |
| Semantic | `--surface-1`, `--text-muted`, `--status-critical`, `--border-subtle` | Components and layouts |
| Component | `--kpi-bg`, `--badge-success-fg`, `--sidebar-width` | Specific components |

Components **must not** hardcode hex values. Charts may read Python mirrors from `ui/tokens.py`.

### Primitive palette (light)

| Token | Value | Use |
|-------|-------|-----|
| `--navy-950` | `#061525` | Deepest surfaces (dark mode base) |
| `--navy-900` | `#0B1F33` | Primary brand / dark headers |
| `--navy-800` | `#102A43` | Elevated dark surfaces |
| `--navy-700` | `#163A5F` | Borders on dark |
| `--blue-600` | `#1677FF` | Primary interactive (medical blue) |
| `--blue-700` | `#2563EB` | Primary hover |
| `--teal-500` | `#14B8A6` | Accent / success-adjacent |
| `--teal-400` | `#2DD4BF` | Accent hover |
| `--slate-50` | `#F8FAFC` | App background |
| `--slate-100` | `#F5F9FC` | Secondary background |
| `--white` | `#FFFFFF` | Cards, inputs |
| `--slate-200` | `#E2E8F0` | Hairline borders |
| `--slate-400` | `#94A3B8` | Muted icons |
| `--slate-500` | `#64748B` | Secondary text |
| `--slate-700` | `#334155` | Body text |
| `--slate-900` | `#0F172A` | Headings |

### Status (must pass WCAG AA on their surfaces)

| Semantic | FG | BG | Border |
|----------|----|----|--------|
| success | `#15803D` | `#DCFCE7` | `#86EFAC` |
| warning | `#B45309` | `#FEF3C7` | `#FCD34D` |
| critical | `#B91C1C` | `#FEE2E2` | `#FCA5A5` |
| info | `#1D4ED8` | `#DBEAFE` | `#93C5FD` |
| neutral | `#475569` | `#F1F5F9` | `#CBD5E1` |

### Typography

- Family: `"Inter", "Plus Jakarta Sans", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`
- Scale (px): 12 / 13 / 14 / 16 / 20 / 24 / 32 / 44
- Weights: 400 (body), 500 (labels), 600 (headings), 700 (display)
- Line-height: 1.5 body, 1.25 headings
- Tabular nums for counts, times, vitals, currency: `font-variant-numeric: tabular-nums`

### Spacing & shape

- Base grid: 4px
- Space scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64
- Radii: 8 (controls), 12 (cards), 16 (panels), 20 (hero)
- Elevation: three soft layered shadows only
- Borders: 1px hairline using `--border-subtle`

### Density

| Mode | Control height | Table row | Card padding |
|------|----------------|-----------|--------------|
| comfortable (default) | 40px | 48px | 20px |
| compact | 32px | 36px | 12px |

Driven by a single data-attribute on the root (`data-density="comfortable|compact"`).

### Dark theme

Semantic tokens remap under `[data-theme="dark"]` and `@media (prefers-color-scheme: dark)`.  
Clinical dark = deep navy surfaces (`--navy-900` / `--navy-800`), not pure black. Contrast re-verified for AA.

### Motion budget

| Category | Duration | Easing |
|----------|----------|--------|
| Micro (hover, focus) | 120–200ms | ease-out |
| Cards / panels | 200–300ms | cubic-bezier(.22,.61,.36,1) |
| Page / shell | 300–450ms | same |
| Continuous (status pulse) | ≤3 elements; pause when tab hidden / reduced-motion |

Preloader (Phase 3): ≤2.4s, pure SVG+CSS, prefers-reduced-motion → static logo + progress bar.

---

## 2. Iconography

Single inline-SVG registry (`ui/icons.py`), Lucide-style, 1.75 stroke, 20/24px.  
No emoji in chrome or status badges. Emoji only in user-authored content.

---

## 3. Localization readiness

- All UI strings live in one module (later phase).
- Date/time helpers are IST-aware and locale-aware.
- Currency: INR with proper grouping (`₹1,234`).
- No string concatenation that breaks translation order.

---

## 4. Accessibility baseline

- WCAG 2.2 AA contrast on all text/UI pairs (verified programmatically where possible).
- Visible 2px focus ring with offset on every interactive control.
- Status never color-only (icon + label).
- `prefers-reduced-motion` and `prefers-contrast` respected.
- Skip link, landmarks, one `h1` per page.
- Touch targets ≥ 44px on mobile.

---

## 5. File map (Phase 1)

```
streamlit_app/
  styles/
    00_tokens.css
    10_base.css
    20_streamlit_overrides.css
    30_components.css      # stubs for later phases
    40_layouts.css
    50_responsive.css
    60_motion.css          # preloader hooks in Phase 3
  ui/
    tokens.py              # Python mirrors for charts
    theme.py               # load CSS once per session
    html.py                # esc(), attr(), class_names()
    icons.py               # minimal SVG registry
    shell/                 # Phase 2
    components/            # Phase 2+
  .streamlit/config.toml
```

Feature flag: `VENUS_UI_V2=1` (env). When unset, existing UI runs unchanged.

---

## 6. Contrast verification notes

Status FG on status BG and body text on `--surface-1` / `--surface-2` meet ≥4.5:1.  
UI controls meet ≥3:1. Dark mode uses lighter text tokens on navy surfaces.  
Re-run checks when palette is tuned.

