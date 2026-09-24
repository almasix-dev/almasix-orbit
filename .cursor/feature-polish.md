# Feature polish tracker

Process: see [`.cursor/rules/feature-polish.mdc`](rules/feature-polish.mdc).

## Queue

| Order | Feature | Docs | Status |
|------:|---------|------|--------|
| 1–98 | Prior modules (tables → notifications) | (prior) | **closed** |
| 120 | Date / time pickers (Flowbite + Week/Month/Year) | `docs/src/content/docs/forms/{date,date-time,time,week,month,year}-picker.md` | **closed** |
| 99 | Multi-tenancy | `docs/src/content/docs/users/tenancy.md` | **closed** |
| 100 | Infolists UI default layout + docs depth | `docs/src/content/docs/infolists/overview.md` | **closed** |
| 101 | Plugins marketplace | `docs/src/content/docs/plugins/*` | **closed** |
| 111 | Marketplace catalog layout | `docs/src/pages/plugins/**` | **closed** |
| 112 | Header Docs + Plugins menus | `docs/src/components/SiteTitle.astro` | **closed** |
| 113 | Marketplace listing chrome (full width, catalog sidebar, docs guides) | `docs/src/pages/plugins/**` | **closed** |
| 114 | Third-party plugin scaffold + listing YAML | `docs/src/content/docs/panels/plugins.md` | **closed** |
| 115 | Marketplace Star → GitHub API | `docs/src/content/docs/plugins/overview.md` | **closed** |
| 116 | Docs version trees (`/0.x/` vs `/main/`) | `docs/src/content/docs/prologue/versions.md` | **closed** |
| 117 | Official plugin: Orbit Permission | `orbit-plugins` + `/plugins/orbit-permission/` | **closed** |
| 118 | Marketplace registry split | `docs/scripts/marketplace-sync.mjs` | **closed** |
| 119 | Marketplace articles | `docs/src/pages/articles/**` · `orbit-plugins/articles` | **closed** |
| 102 | Resources depth (relation managers, global search, record titles, soft deletes) | `docs/src/content/docs/resources/*` | **closed** |
| 103 | Forms leftovers (FileUpload endpoint, RichEditor, MorphTo live search, ModalTableSelect / KeyValue hosts) | `docs/src/content/docs/forms/{file-upload,rich-editor,morph-to-select,modal-table-select,key-value}.md` | **closed** |
| 104 | Import / export job runners | `docs/src/content/docs/actions/{import,export}.md` | **closed** |
| 105 | Query builder polish | `docs/src/content/docs/query-builder/overview.md` | **closed** |
| 106 | Users / MFA (TOTP + email SMTP) | `docs/src/content/docs/users/multi-factor-authentication.md` | **closed** |
| 107 | Notifications production adapters (Almasix `notifications` table + broadcast hub + `/orbit-live`) | `docs/src/content/docs/notifications/{database,broadcast}-notifications.md` | **closed** |
| 108 | Panels platform (SPA mode, billing adapters, multi-panel registry) | `docs/src/content/docs/panels/configuration.md` | **closed** |
| 109 | Docs completeness pass (thin pages, unique shots, alignment) | `docs/src/content/docs/**` | **closed** |
| 110 | Support toolkit polish | `docs/src/content/docs/support/*` | **closed** |

## Marketplace articles — closed

**Bar:** Articles are first-class registry entries (`articles/*.yaml` + `public/articles/`) with full Markdown bodies, tags, related plugins, and issue/PR templates. Orbit syncs them at build and renders `/articles/` with marketplace chrome, top-bar Articles menu, author cross-list, and `/articles/feed.json`.

## Marketplace registry split — closed

**Bar:** Listing YAML/images/PRs live in [almasix-dev/orbit-plugins](https://github.com/almasix-dev/orbit-plugins). Orbit docs sync the registry at build (`marketplace:sync`), catalog UI stays on orbit.almasix.com/plugins, `repository_dispatch` rebuilds docs after registry merges.

## Official Orbit Permission plugin — closed

**Bar:** First official marketplace product plugin (`almasix-orbit-permission`): Users / Roles / Permissions resources, generator, super-admin command, Access widget, listing + images, Orbit-first README. Repo: [almasix-dev/almasix-orbit-permission](https://github.com/almasix-dev/almasix-orbit-permission).

## Docs version trees — closed

**Bar:** Production docs emit parallel trees: `/0.x/` from the latest stable `v0.*` tag (released docs) and `/main/` from this commit (unreleased). `/` redirects to `/0.x/`. Switcher uses path prefixes, not a shared `?docsVersion=` corpus. Tests + Cloudflare/CI tag fetch.

## Marketplace GitHub star API — closed

**Bar:** Listing **Star on GitHub** `PUT`s `/user/starred` as the visitor via Worker OAuth (`/api/github/*`). Unconfigured or local static preview returns 501 and the button opens the repo. HMAC state, httpOnly token cookie, tests, Orbit-first docs.

## Third-party plugin scaffold — closed

**Bar:** `smith make:orbit-plugin` / `python -m almasix.orbit plugin new` writes a publishable package (`Plugin` subclass, pyproject, smoke test) and draft marketplace YAML (plugin + author). `--listing-only` / `--no-listing` / `--paid`. Orbit-first docs, 100% coverage.

## Marketplace listing chrome — closed

**Bar:** Catalog pages are full-width listing UI with a marketplace-only sidebar (browse, authors, categories, JSON catalog API). Plugin overview, building, and publishing stay in the Docs sidebar.

## Header Docs + Plugins menus — closed

**Bar:** Persistent top-bar `Docs` + `Plugins` menus next to the Almasix mark (visible on the splash landing and every inner page), current-state highlighting, marketplace shots recaptured.

## Marketplace catalog layout — closed

**Bar:** Dedicated marketplace sidebar, top-bar + home CTAs, `max-width: 96rem` catalog, card stats (installs/stars/GitHub/PyPI), listing aside (author + total stars + other plugins), related footer, Star-on-GitHub button, validator tests.

## Plugin marketplace — closed

**Bar:** YAML registry with schema + validator tests, published official listing (`orbit-branding`), browse with shareable query filters, category/author indexes, JSON feed, listing extras (license, keywords, related, copy-install), Orbit-first docs with unique shots, 100% coverage.

## Infolists layout + docs depth — closed

**Bar:** Stacked label-above-value default (`.or-entry-inline` for side-by-side), Orbit-first overview depth (hidden/inline labels, sections, extra attrs, utility injection) with unique gallery shots, 100% coverage on infolists surface, vendor CSS synced.

## Support toolkit — closed

**Bar:** `HtmlString` / `classes` / `e()` `__html__`, `Component.key` / `.grow` / `.when`, `Colors.palette` + `css_var`, Heroicon aliases, Orbit-first support docs with unique gallery shots, 100% coverage.

## Docs completeness — closed

**Bar:** Thin learner pages expanded Orbit-first (`resources/pages`, `testing`, `components/form`+`table`, `configuration`, schemas empty-state/wizard/callout/section, infolist extras), unique light/dark shots for previously shot-less pages, scaffolding/SPA notes aligned with shipped APIs, 100% coverage unchanged (docs-only).

## Panels platform — closed

**Bar:** `.spa()` + `.spa_url_exceptions()` (Alpine fetch of `main.or-content`), default `ManageBilling` + `MemoryBillingProvider` for `.tenant_billing(True)`, `PanelRegistry.get_by_path` / `get_by_domain`, orbit-admin sample, Orbit-first docs + unique gallery shots, 100% coverage.

## Notifications production adapters — closed

**Bar:** Panel bell persists via Almasix `notifications` table (`.database_notifications_using_almasix()`), with `SqliteNotificationStore` retained for tests; `MemoryBroadcastHub` / `CallbackBroadcastHub` published from `.broadcast()`, panel GET/POST `/orbit-notifications` and GET `/orbit-live` with Alpine polling, Orbit-first docs + unique gallery shots, 100% coverage.

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
