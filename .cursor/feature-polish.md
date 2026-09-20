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
| 92 | Navigation overview | `docs/src/content/docs/navigation/overview.md` | **closed** |
| 93 | Custom pages | `docs/src/content/docs/navigation/custom-pages.md` | **closed** |
| 94 | User menu | `docs/src/content/docs/navigation/user-menu.md` | **closed** |
| 95 | Clusters | `docs/src/content/docs/navigation/clusters.md` | **closed** |
| 96+ | Remaining Orbit doc features | docs nav | queued |

## Navigation autopilot — closed

**Bar:** 100% Filament 5 Navigation parity (API + UX + DX), Filament-depth docs + light/dark screenshots, 100% coverage on touched surface, orbit-admin sample.

### Delivered

- Overview: layouts, groups, subgroups, badges, parent items, custom items, builder, sidebar collapse/width
- Custom pages: nav knobs + `can_access` / `should_register_navigation`
- User menu: `UserMenuItem` depth, groups, profile/logout, disable, position
- Clusters: discover/register, `$cluster`, sub-nav positions, URL prefix, breadcrumbs
- Gallery: `build_navigation_variants` + `capture-navigation.mjs` → `docs/public/examples/{light,dark}/navigation/`
- orbit-admin: focused Navigation showcase (badges, subgroup/parent, custom item, user menu, small cluster)
