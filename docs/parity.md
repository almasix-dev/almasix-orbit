# Orbit feature completeness matrix (maintainer only)

> **Not learner docs.** This file tracks internal completeness against a historical API checklist.
> Public teaching copy lives under `docs/src/content/docs/` and must stay Orbit-first
> (see `.cursor/rules/orbit-first-docs.mdc`).

Orbit’s public packages aim for a rich admin surface on Almasix (Conduit + Alpine).
Maintainers may use the columns below when comparing against prior art; **do not** copy
this framing into learner-facing pages.

**Status values**

| Status | Meaning |
|--------|---------|
| **Done** | Fluent API + distinct `or-*` render + tests + docs (with screenshots where UI-heavy) |
| **Partial** | API exists; some knobs / host adapters remain |
| **Planned** | Not started |

## Packages

| Prior-art package (reference) | Orbit package | Status |
|-------------------------------|---------------|--------|
| support | `almasix-orbit-support` | Done |
| schemas | `almasix-orbit-schemas` | Done |
| forms | `almasix-orbit-forms` | Done |
| tables | `almasix-orbit-tables` | Partial |
| actions | `almasix-orbit-actions` | Done |
| infolists | `almasix-orbit-infolists` | Partial |
| notifications | `almasix-orbit-notifications` | Done |
| widgets | `almasix-orbit-widgets` | Done |
| query-builder | `almasix-orbit-query-builder` | Done |
| panels | `almasix-orbit` (panels) | Partial |

## Marketplace — Done

Docs-hosted catalog UI at `/plugins/` (on the **main** docs tree; `/0.x/` is the latest release tag). Listing YAML and images live in [almasix-dev/orbit-plugins](https://github.com/almasix-dev/orbit-plugins); the docs build syncs that registry. JSON feed + `/plugins/develop` catalog API, `smith make:orbit-plugin` / `python -m almasix.orbit plugin new` scaffold + draft listing YAML, validator tests, official `orbit-branding` / `orbit-permission` listings. Plugin overview/build/publish stay in Docs. Orbit takes no payment. Parallel docs trees: `/0.x/` from the latest `v0.*` tag, `/main/` from this commit, `/` → `/0.x/`.

## Support — Done

`Component` (`.key` / `.grow` / `.when` / `.live` / `.saved`), `Colors.hex` / `css_class` / `css_var` / `palette` (50–950), Heroicon set + `register_icon` aliases, `HtmlString` + `e` / `classes` / `tag`, `evaluate` utility injection, `resolve_public_url`, `conduit_attr`.

## Schemas — Done

`Schema`, `Grid`, `Flex`, `Group`, `Split`, `Section` (compact/aside/collapsible/persist), `Tabs` (icons/badges/persist), `Fieldset`, `Wizard` (nav/continue/back/skip), `Callout`, `EmptyState`, primes (`Text`, `Icon`, `Image`, `UnorderedList`).

## Forms — Done

| Feature | Status |
|---------|--------|
| Nested `validate()` / `dehydrate()` via layout walk | Done |
| Field chrome (hint / prefix / suffix / prefix+suffix actions / helper / autofocus) | Done |
| Validation catalog (+ `required_if` / `required_unless` / `prohibited` / `prohibited_if`) | Done |
| Select: Orbit combobox (searchable / multiple / HTML / non-native), relationship AJAX, create/edit mounts | Done |

| FileUpload: disk/visibility/editor + **panel upload endpoint** + `UploadStorage` | Done |
| Repeater/Builder: defaultItems, simple, table head, grid, clone/reorder + **host mutations** | Done |
| KeyValue / MorphToSelect / ModalTableSelect host mounts | Done |
| TagsInput suggestions + separator + reorderable flag | Done |
| Radio / CheckboxList descriptions, columns, bulk toggle | Done |
| Date/Time pickers min/max/display_format/`native(False)` | Done |
| `MoneyInput` currency prefix | Done |
| Placeholder respects `hidden()` / visibility | Done |
| RichEditor toolbar, merge tags, contenteditable surface | Done |
| Live MorphTo AJAX (`.options_using` + host search) | Done |

## Tables — Partial

| Feature | Status |
|---------|--------|
| Summaries (`Sum`/`Average`/`Count`/`Range`) | Done |
| Row grouping (`Group`) | Done |
| Layout `Split`/`Stack`/`Panel`/`Grid`/`View` | Done |
| TextColumn money/date/description/copyable/weight/wrap/markdown/icon | Done |
| IconColumn boolean + ImageColumn circular/stacked + ColorColumn | Done |
| Editable Select/Toggle/TextInput/Checkbox + `update_column_state` | Done |
| ColumnGroup dual header row | Done |
| `TrashedFilter` + filter persist/defer flags | Done |
| Index search / sortable headers / pagination chrome | Done |
| Always-visible sort carets on orderable columns | Done |
| Filter chrome (dropdown) + indicator chips + `setTableFilter` | Done |
| Empty state Create CTA + `record_url` row click | Done |
| Bulk selection + `BulkActionGroup` Actions dropdown | Done |
| Select all matching results (across pages) | Done |
| Bulk actions + selection indicator | Done |
| Filters icon dropdown (Apply/Reset) | Done |
| Column `alignment` / `align_end` mirrored on headers | Done |
| numbered pagination + per-page dropup + 3-zone footer | Done |
| Filters/Columns above search with toolbar divider | Done |
| Default row actions as ⋮ dropdown | Done |
| Content-grid cards (title + stacked fields) | Done |
| Column visibility manager / breakpoint CSS | Done |
| List tabs with live/callable badges | Done |
| `Table.summaries(page=, all=)` + summary footer chrome | Done |

## Actions — Done

| Feature | Status |
|---------|--------|
| Create/Edit/View/Delete + modal URL modes | Done |
| Modal forms (`Action.form()` in shell dialog) | Done |
| Danger actions always confirm (Conduit-safe) | Done |
| Trigger chrome (button/link/iconButton/badge, size, outlined, tooltip, keys, URL+tab) | Done |
| Full modal API (slide-over, sticky, labels, icon, alignment, close behavior) | Done |
| Replicate / ForceDelete / Restore / Import / Export | Done |
| `ActionGroup` / `BulkActionGroup` + sections / placement | Done |
| CRUD lifecycle hooks (mutate/using/before/after/halt/createAnother) | Done |
| Host job runners for import/export | Done (in-process default; pluggable `JobRunner`) |

## Widgets — Done

| Feature | Status |
|---------|--------|
| Base `Widget` (sort / column_span / polling / lazy / can_view) | Done |
| `StatsOverviewWidget` + fluent `Stat` + sparklines | Done |
| `ChartWidget` Chart.js default + ApexCharts via `.chart_library` | Done |
| `TableWidget` embedding `Table` | Done |
| Dashboard mount (`get_widgets` / `get_columns` / filters / `route_path`) | Done |
| Docs + light/dark gallery shots + orbit-admin sample | Done |

## Navigation — Done

| Feature | Status |
|---------|--------|
| Layouts (`sidebar` / `top` / `apps` / `sidebar_topbar`) + active path matching | Done |
| Groups / subgroups / badges / parent items / custom `NavigationItem` | Done |
| `should_register_navigation` + `NavigationBuilder` / `.navigation(False)` | Done |
| Sidebar collapse / widths / collapsible groups | Done |
| Custom pages nav knobs + `can_access` | Done |
| User menu items / groups / profile+logout specials / position / disable | Done |
| Clusters discover/register, URL prefix, sub-nav positions, breadcrumbs | Done |
| Docs + light/dark gallery shots + orbit-admin sample | Done |

## Notifications — Done

| Feature | Status |
|---------|--------|
| Fluent `Notification` (title / body / icon / color / status / duration / persistent / actions) | Done |
| Flash `.send()` + panel toast host (`orbitNotifications`) | Done |
| `OrbitNotification` / `OrbitNotificationAction` JS client + close-by-id | Done |
| Toast alignment (`Notifications.alignment` / `vertical_alignment`) | Done |
| Database bell (panel enable / seeds / position / polling / mark read) | Done |
| Pluggable `DatabaseNotificationStore` + in-memory default | Done |
| `LiveNotifier` + `orbit:broadcast` / `orbitLiveNotifications` | Done |
| Testing helpers (`assert_notified` / `assert_not_notified` / `reset_notifications`) | Done |
| Docs + light/dark gallery shots + orbit-admin sample | Done |

## Query builder — Done

Typed constraints (`Text` / `Select` / `Boolean` / `Date` / `Number`), operators, `.add_rule()` / `.logic("and"|"or")`, hydrate-from-state render, `QueryBuilderFilter` table chrome + `{logic, rules}` apply, docs + gallery shots.

## Panels / platform — Partial

| Feature | Status |
|---------|--------|
| List/Create/Edit/View page hosts + list tabs | Done |
| Dashboard home + multi-dashboard `route_path` | Done |
| Global search (resource attributes, grouped results, panel endpoint) | Done |
| Relation managers rendered on view/edit (+ create/delete actions) | Done |
| Record titles in page headings and breadcrumbs | Done |
| Resource soft deletes (trashed filter, restore, force delete) | Done |
| Clusters / auth pages / MFA protocol + TOTP/email runners | Done |
| Multi-tenancy (`Tenancy`, switcher, scoping, HasTenants, RegisterTenant / EditTenantProfile, middleware, route prefix, docs + gallery + orbit-admin) | Done |
| Render hooks + Plugin base | Done |
| `discover_*` + `load_discovered` + scaffolding writes files | Done |
| Multi-panel domains / SPA / billing adapters | Done |
| Real DB notification persistence / live hub | Done (SQLite store + `BroadcastHub` + `/orbit-live`) |

## Docs / screenshots

| Feature | Status |
|---------|--------|
| Real light/dark PNG examples under `docs/public/examples/{theme}/{section}/{name}.png` | Done |

| Gallery build + Playwright capture scripts | Done |
| Every field page with PNG (not HTML fence) | Partial |

Host-only concerns (SMTP MFA delivery, production queues, third-party billing processors) remain **interfaces + documented adapters**.

Keywords for smoke tests: resources, pages, relation managers, TextInput, Select, Repeater.
