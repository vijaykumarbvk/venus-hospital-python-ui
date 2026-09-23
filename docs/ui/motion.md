# Venus motion specification — Preloader

**Phase 3** · Pure SVG + CSS · Payload target &lt; 20 KB

## Behaviour rules

| Rule | Implementation |
|------|----------------|
| Once per browser session | `st.session_state["_venus_preloader_shown"]` |
| Duration | Master overlay animation 2.5s; hard hide at 2.6s via script fallback |
| Skip | Button visible after 800ms; sets `is-done` + `hidden` |
| Reduced motion | Static heart + ECG + progress bar; overlay ~1.2s |
| No libraries | No Lottie, video, GIF, or JS animation frameworks |
| Properties animated | `opacity`, `transform`, `stroke-dashoffset` only |

## Timeline (easing `cubic-bezier(.22,.61,.36,1)` unless noted)

| t (ms) | Element | Event |
|--------|---------|--------|
| 0–200 | Overlay | Fade in + radial glow |
| 150–500 | `#mark` | Wordmark fade/scale in |
| 300–900 | `#heart-outline` | Stroke draw (`stroke-dashoffset`) |
| 850–1200 | `#heart-fill` | Fill fade in |
| 900–1400 | `#heart-fill` | Two-beat lub-dub scale |
| 500–1500 | `#ecg-path` | ECG stroke travel + soft glow |
| 1000–1700 | `#tube` | Stethoscope tube draw |
| 1150–1650 | `#chestpiece` | Ease in + slight rotation |
| 1700–1900 | `#ripple` | Contact ripple from heart |
| 950–2200 | `#particles` | 6 particles drift up (opacity ≤ 0.35) |
| 0–2200 | Progress bar | Width 0 → 100% |
| 0 / 900 / 1700 | Status text | Preparing → Loading → Ready |
| 2200–2500 | Overlay | Fade/lift away |

## Named SVG groups

| ID | Role |
|----|------|
| `#heart` | Outline + fill + ripple |
| `#heart-outline` | Path stroke draw |
| `#heart-fill` | Fill + heartbeat |
| `#ecg` / `#ecg-path` | ECG polyline |
| `#tube` | Stethoscope tube |
| `#chestpiece` | Chest-piece group |
| `#ripple` | Contact ring |
| `#particles` | Ambient dots |
| `#mark` | Wordmark |

## Status copy (honest)

- “Preparing your workspace”
- “Loading your dashboard”
- “Ready”

No claims about “secure connection” unless verified by the app.

## Global motion budget

| Category | Duration |
|----------|----------|
| Micro (hover/focus) | 120–200ms |
| Cards / panels | 200–300ms |
| Page / shell | 300–450ms |
| Continuous pulse | ≤3 elements; pause under reduced motion |

## Preview

Open `streamlit_app/ui/components/preloader_preview.html` in a browser for isolated review (no Streamlit required).
