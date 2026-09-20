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
| 87–91 | Widgets + Dashboard | `docs/src/content/docs/widgets/*`, `panels/dashboard.md` | **closed** |
| 92–95 | Navigation | `docs/src/content/docs/navigation/*` | **closed** |
| 96 | Notifications overview | `docs/src/content/docs/notifications/overview.md` | **closed** |
| 97 | Database notifications | `docs/src/content/docs/notifications/database-notifications.md` | **closed** |
| 98 | Broadcast notifications | `docs/src/content/docs/notifications/broadcast-notifications.md` | **closed** |
| 99+ | Remaining Orbit doc features | docs nav | queued |

## Notifications autopilot — closed

**Bar:** 100% Filament 5 Notifications parity (API + UX + DX), toast host + JS client, database bell, broadcast adapter, Filament-depth docs + light/dark screenshots, 100% coverage, orbit-admin sample.

### Scope

Fluent API (title/body/icon/color/duration/persistent/actions/send), Alpine toast host, OrbitNotification JS client, action→toast wiring, database notifications panel UI, broadcast/live notifier, testing helpers.
