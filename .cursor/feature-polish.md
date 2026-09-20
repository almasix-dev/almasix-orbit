# Feature polish tracker

Process: see [`.cursor/rules/feature-polish.mdc`](rules/feature-polish.mdc).

## Queue

| Order | Feature | Docs | Status |
|------:|---------|------|--------|
| 1–17 | Panel / Tables / Columns / Filters | (prior) | **closed** |
| 18–30 | Schemas module | `docs/src/content/docs/schemas/*` | **closed** |
| 31–65 | Forms module | `docs/src/content/docs/forms/*` | **closed** |
| 66–74 | Infolists module | `docs/src/content/docs/infolists/*` | **closed** |
| 75 | Actions overview | `docs/src/content/docs/actions/overview.md` | **closed** |
| 76 | Modals | `docs/src/content/docs/actions/modals.md` | **closed** |
| 77 | Grouping actions | `docs/src/content/docs/actions/grouping-actions.md` | **closed** |
| 78 | Create action | `docs/src/content/docs/actions/create.md` | **closed** |
| 79 | Edit action | `docs/src/content/docs/actions/edit.md` | **closed** |
| 80 | View action | `docs/src/content/docs/actions/view.md` | **closed** |
| 81 | Delete action | `docs/src/content/docs/actions/delete.md` | **closed** |
| 82 | Replicate action | `docs/src/content/docs/actions/replicate.md` | **closed** |
| 83 | Force-delete action | `docs/src/content/docs/actions/force-delete.md` | **closed** |
| 84 | Restore action | `docs/src/content/docs/actions/restore.md` | **closed** |
| 85 | Import action | `docs/src/content/docs/actions/import.md` | **closed** |
| 86 | Export action | `docs/src/content/docs/actions/export.md` | **closed** |
| 87+ | Remaining Orbit doc features | docs nav | queued |

## Actions autopilot — closed

**Bar:** 100% Filament 5 feature parity on the Orbit Actions surface (API + UX + DX), Filament-depth docs (every subsection = explanation + code + light/dark screenshots), 100% test coverage, orbit-admin sample.

### Shipped

Trigger chrome (button/link/iconButton/badge, size, outlined, tooltip, keybindings, url+new-tab), full modal API, ActionGroup depth, CRUD preset hooks (mutate/using/before/after/halt/cancel/createAnother/notifications/redirects), Replicate persistence, BulkAction helpers, Import/Export config + documented adapter contract, orbit-admin `ActionsOverviewResource`, gallery shots under `docs/public/examples/{light,dark}/actions/`.
