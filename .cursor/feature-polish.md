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
| 103 | Forms leftovers (FileUpload endpoint, RichEditor, MorphTo live search, ModalTableSelect / KeyValue hosts) | `docs/src/content/docs/forms/{file-upload,rich-editor,morph-to-select,modal-table-select,key-value}.md` | **closed** |
| 104 | Import / export job runners | `docs/src/content/docs/actions/{import,export}.md` | **closed** |
| 105 | Query builder polish | `docs/src/content/docs/query-builder/overview.md` | **closed** |
| 106 | Users / MFA (TOTP + email SMTP) | `docs/src/content/docs/users/multi-factor-authentication.md` | **closed** |
| 107 | Notifications production adapters (SQLite store + broadcast hub + `/orbit-live`) | `docs/src/content/docs/notifications/{database,broadcast}-notifications.md` | **closed** |
| 108 | Panels platform (SPA mode, billing adapters, multi-panel registry) | `docs/src/content/docs/panels/configuration.md` | **closed** |
| 109 | Docs completeness pass (thin pages, unique shots, alignment) | `docs/src/content/docs/**` | **closed** |
| 110 | Support toolkit polish | `docs/src/content/docs/support/*` | **closed** |

## Infolists layout + docs depth — closed

**Bar:** Stacked label-above-value default (`.or-entry-inline` for side-by-side), Orbit-first overview depth (hidden/inline labels, sections, extra attrs, utility injection) with unique gallery shots, 100% coverage on infolists surface, vendor CSS synced.

## Support toolkit — closed

**Bar:** `HtmlString` / `classes` / `e()` `__html__`, `Component.key` / `.grow` / `.when`, `Colors.palette` + `css_var`, Heroicon aliases, Orbit-first support docs with unique gallery shots, 100% coverage.

## Docs completeness — closed

**Bar:** Thin learner pages expanded Orbit-first (`resources/pages`, `testing`, `components/form`+`table`, `configuration`, schemas empty-state/wizard/callout/section, infolist extras), unique light/dark shots for previously shot-less pages, scaffolding/SPA notes aligned with shipped APIs, 100% coverage unchanged (docs-only).

## Panels platform — closed

**Bar:** `.spa()` + `.spa_url_exceptions()` (Alpine fetch of `main.or-content`), default `ManageBilling` + `MemoryBillingProvider` for `.tenant_billing(True)`, `PanelRegistry.get_by_path` / `get_by_domain`, orbit-admin sample, Orbit-first docs + unique gallery shots, 100% coverage.

## Notifications production adapters — closed

**Bar:** `SqliteNotificationStore` (stdlib sqlite3) for the database bell, `MemoryBroadcastHub` / `CallbackBroadcastHub` published from `.broadcast()`, panel GET/POST `/orbit-notifications` and GET `/orbit-live` with Alpine polling, orbit-admin sample, Orbit-first docs + unique gallery shots, 100% coverage.

## Users / MFA — closed

**Bar:** `AppAuthentication` RFC 6238 TOTP + recovery codes, `EmailAuthentication` with `MemoryMailer` / `SmtpMailer`, panel `.multi_factor_authentication()`, login → pending session → `/mfa-challenge` host, Orbit-admin sample, Orbit-first docs + unique gallery shots, 100% coverage.

## Query builder polish — closed

**Bar:** Typed constraint widgets, AND/OR logic, `.add_rule()` / hydrate-from-state, `QueryBuilderFilter` chrome + `{logic, rules}` apply, orbit-admin Posts sample, Orbit-first docs with unique gallery shots, 100% coverage.

## Import / export runners — closed

**Bar:** In-process `ImmediateJobRunner` parses CSV/JSON, maps columns, chunks, and writes rows (or calls a custom importer/exporter). List host `mountAction("import"|"export")` plus `orbit-export-ready` download. Pluggable `set_job_runner` for queues. Orbit-admin Posts header actions, Orbit-first import/export docs, 100% coverage.

## Forms leftovers — closed

**Bar:** Panel `/orbit-upload` endpoint validates against the field and stores via `UploadStorage` (memory default, filesystem disks), FileUpload previews existing files and posts from the browser, RichEditor toolbar + merge tags + min-height, MorphToSelect `.options_using` live search, ModalTableSelect searchable picker + table mount, KeyValue host add/rename/remove, orbit-admin Posts form sample, Orbit-first docs + unique gallery shots, 100% coverage.

## Resources depth — closed

**Bar:** Relation managers render (and delete) on view/edit pages with ORM or in-memory rows, panel global search end to end (resource attributes → grouped results → topbar endpoint), record titles in page headings and breadcrumbs, resource-level soft deletes (trashed filter + restore/force delete), orbit-admin comments relation + searchable resources, Orbit-first docs for every resources page with light/dark shots, 100% coverage.
