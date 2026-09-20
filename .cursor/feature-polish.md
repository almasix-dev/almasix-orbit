# Feature polish tracker

Process: see [`.cursor/rules/feature-polish.mdc`](rules/feature-polish.mdc).

## Queue

| Order | Feature | Docs | Status |
|------:|---------|------|--------|
| 1–17 | Panel / Tables / Columns / Filters | (prior) | **closed** |
| 18–30 | Schemas module | `docs/src/content/docs/schemas/*` | **closed** |
| 31–65 | Forms module | `docs/src/content/docs/forms/*` | **closed** |
| 66–74 | Infolists module | `docs/src/content/docs/infolists/*` | **closed** |
| 75–86 | Actions module | `docs/src/content/docs/actions/*` | **closed** |
| 87 | Widgets overview | `docs/src/content/docs/widgets/overview.md` | **closed** |
| 88 | Stats overview | `docs/src/content/docs/widgets/stats-overview.md` | **closed** |
| 89 | Chart widgets | `docs/src/content/docs/widgets/charts.md` | **closed** |
| 90 | Table widgets | `docs/src/content/docs/widgets/tables.md` | **closed** |
| 91 | Dashboard / Home | `docs/src/content/docs/panels/dashboard.md` | **closed** |
| 92+ | Remaining Orbit doc features | docs nav | queued |

## Widgets + Dashboard autopilot — closed

**Bar:** 100% Filament 5 Widgets + Dashboard parity (API + UX + DX), Chart.js **or** ApexCharts selectable on chart widgets, Filament-depth docs + light/dark screenshots, 100% test coverage, orbit-admin sample.

### Delivered

- Dashboard mount pipeline (panel widgets → home grid)
- Widget class API (sort / span / can_view / polling / lazy)
- Fluent Stat + sparklines (`orbitSparkline`)
- ChartWidget dual libraries (Chart.js default + ApexCharts via `.chart_library`)
- TableWidget + custom widgets
- Dashboard filters / columns / multi-dashboard `route_path`
- Docs pages + gallery shots (light/dark)
- orbit-admin home Dashboard sample (stats, Chart.js, Apex, table, custom)

## Next

Open the next queued feature only after confirming 87–91 stay closed.
