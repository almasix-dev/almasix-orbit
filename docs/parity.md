# Filament 5.x ↔ Orbit parity matrix (maintainer)

Orbit targets FilamentPHP **5.x** API familiarity on Almasix (Conduit + Alpine).

**Status values**

| Status | Meaning |
|--------|---------|
| **Done** | Fluent API + distinct `or-*` render + tests + docs (with screenshots where UI-heavy) |
| **Partial** | API exists; some Filament knobs / host adapters remain |
| **Planned** | Not started |

## Packages

| Filament package | Orbit package | Status |
|------------------|---------------|--------|
| support | `almasix-orbit-support` | Partial |
| schemas | `almasix-orbit-schemas` | Done |
| forms | `almasix-orbit-forms` | Partial |
| tables | `almasix-orbit-tables` | Partial |
| actions | `almasix-orbit-actions` | Done |
| infolists | `almasix-orbit-infolists` | Partial |
| notifications | `almasix-orbit-notifications` | Done |
| widgets | `almasix-orbit-widgets` | Done |
| query-builder | `almasix-orbit-query-builder` | Partial |
| panels | `almasix-orbit` (panels) | Partial |

## Schemas — Done

`Schema`, `Grid`, `Flex`, `Group`, `Split`, `Section` (compact/aside/collapsible/persist), `Tabs` (icons/badges/persist), `Fieldset`, `Wizard` (nav/continue/back/skip), `Callout`, `EmptyState`, primes (`Text`, `Icon`, `Image`, `UnorderedList`).

## Forms — Partial

| Feature | Status |
|---------|--------|
| Nested `validate()` / `dehydrate()` via layout walk | Done |
| Field chrome (hint / prefix / suffix / prefix+suffix actions / helper / autofocus) | Done |
| Validation catalog (+ `required_if` / `required_unless` / `prohibited` / `prohibited_if`) | Done |
| Select: Filament combobox (searchable / multiple / HTML / non-native), relationship AJAX, create/edit mounts | Done |

| FileUpload: disk/visibility/editor/download attrs + preview chrome | Partial |
| Repeater/Builder: defaultItems, simple, table head, grid, clone/reorder + **host mutations** | Done |
| KeyValue / MorphToSelect / ModalTableSelect host mounts | Partial |
| TagsInput suggestions + separator + reorderable flag | Done |
| Radio / CheckboxList descriptions, columns, bulk toggle | Done |
| Date/Time pickers min/max/display_format/`native(False)` | Done |
| `MoneyInput` currency prefix | Done |
| Placeholder respects `hidden()` / visibility | Done |
| TipTap RichEditor toolbar + contenteditable surface | Partial |
| Live MorphTo AJAX / production FilePond upload adapter | Planned |

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
| Filament-style Bulk actions + selection indicator | Done |
| Filament-style Filters icon dropdown (Apply/Reset) | Done |
| Column `alignment` / `align_end` mirrored on headers | Done |
| Filament-style numbered pagination + per-page dropup + 3-zone footer | Done |
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
| Host job runners for import/export | Partial (config + docs adapter contract) |

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

## Panels / platform — Partial

| Feature | Status |
|---------|--------|
| List/Create/Edit/View page hosts + list tabs | Done |
| Dashboard home + multi-dashboard `route_path` | Done |
| Global search helpers | Done |
| Clusters / auth pages / MFA protocol / tenancy | Done |
| Render hooks + Plugin base | Done |
| `discover_*` + `load_discovered` + scaffolding writes files | Done |
| Multi-panel domains / SPA / billing adapters | Partial (domains Done; SPA/billing later) |
| Real DB notification persistence / Echo | Partial |

## Docs / screenshots

| Feature | Status |
|---------|--------|
| Real light/dark PNG examples under `docs/public/examples/{theme}/{section}/{name}.png` | Done |

| Gallery build + Playwright capture scripts | Done |
| Every field page with PNG (not HTML fence) | Partial |

Host-only concerns (SMTP MFA delivery, Spark billing, production queues) remain **interfaces + documented adapters**.

Keywords for smoke tests: resources, pages, relation managers, TextInput, Select, Repeater.
