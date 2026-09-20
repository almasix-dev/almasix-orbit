# Feature polish tracker

Process: see [`.cursor/rules/feature-polish.mdc`](rules/feature-polish.mdc).

## Queue

| Order | Feature | Docs | Status |
|------:|---------|------|--------|
| 1–98 | Prior modules (tables → notifications) | (prior) | **closed** |
| 99 | Multi-tenancy | `docs/src/content/docs/users/tenancy.md` | **closed** |
| 100 | Infolists UI default layout + docs depth | `docs/src/content/docs/infolists/overview.md` | **closed** |
| 101 | Plugin marketplace (v1) | `docs/src/content/docs/plugins/*` | **closed** |
| 102+ | Remaining Orbit doc features | docs nav | queued |

## Plugin marketplace (v1) — closed

**Bar:** YAML registry (`docs/src/data/marketplace/`) with schema + cross-reference validation in the docs build, `/plugins` browse grid with search / price / category / version / official / dark-mode filters and sort, listing and author pages, Orbit-first publish docs (overview, get listed, guidelines, paid vs free), maintainer review pack (`.github/PLUGIN_REVIEW_GUIDELINES.md` + plugin PR template). Catalog ships empty — Orbit takes no payment and hosts no author dashboard in v1.

## Infolists layout + docs depth — closed

**Bar:** Stacked label-above-value default (`.or-entry-inline` for side-by-side), Orbit-first overview depth (hidden/inline labels, sections, extra attrs, utility injection) with unique gallery shots, 100% coverage on infolists surface, vendor CSS synced.
