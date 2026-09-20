# Feature polish tracker

Process: see [`.cursor/rules/feature-polish.mdc`](rules/feature-polish.mdc).

## Queue

| Order | Feature | Docs | Status |
|------:|---------|------|--------|
| 1–98 | Prior modules (tables → notifications) | (prior) | **closed** |
| 99 | Multi-tenancy | `docs/src/content/docs/users/tenancy.md` | **closed** |
| 100 | Infolists UI default layout + docs depth | `docs/src/content/docs/infolists/overview.md` | **closed** |
| 101 | Plugins marketplace (v1) | `docs/src/content/docs/plugins/*` | **closed** |
| 102 | Resources depth (relation managers, global search, record titles, soft deletes) | `docs/src/content/docs/resources/*` | **closed** |
| 103+ | Remaining stability milestones (forms leftovers → support toolkit) | docs nav | queued |

## Infolists layout + docs depth — closed

**Bar:** Stacked label-above-value default (`.or-entry-inline` for side-by-side), Orbit-first overview depth (hidden/inline labels, sections, extra attrs, utility injection) with unique gallery shots, 100% coverage on infolists surface, vendor CSS synced.

## Resources depth — closed

**Bar:** Relation managers render (and delete) on view/edit pages with ORM or in-memory rows, panel global search end to end (resource attributes → grouped results → topbar endpoint), record titles in page headings and breadcrumbs, resource-level soft deletes (trashed filter + restore/force delete), orbit-admin comments relation + searchable resources, Orbit-first docs for every resources page with light/dark shots, 100% coverage.
