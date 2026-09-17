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
| actions | `almasix-orbit-actions` | Partial |
| infolists | `almasix-orbit-infolists` | Partial |
| notifications | `almasix-orbit-notifications` | Partial |
| widgets | `almasix-orbit-widgets` | Partial |
| query-builder | `almasix-orbit-query-builder` | Partial |
| panels | `almasix-orbit` (panels) | Partial |

## Schemas — Done

`Schema`, `Grid`, `Flex`, `Section`, `Tabs`, `Fieldset`, `Wizard`, `Callout`, `EmptyState`, primes (`Text`, `Icon`, `Image`, `UnorderedList`).

## Forms — Partial

| Feature | Status |
|---------|--------|
| Nested `validate()` / `dehydrate()` via layout walk | Done |
| Field chrome (hint / prefix / suffix / helper / autofocus / live blur+debounce) | Done |
| Validation catalog (unique/exists/confirmed/in/dates/regex/between/mimes/…) | Done |
| Select: searchable Alpine, enum, AJAX attrs, create/edit option mounts | Partial |
| FileUpload: disk/visibility/editor/download attrs + preview chrome | Partial |
| Repeater/Builder: defaultItems, simple, table, per-block schema, mutate hooks | Partial |
| TipTap RichEditor toolbar + contenteditable surface | Partial |
| Live MorphTo AJAX / production FilePond upload adapter | Planned |

## Tables — Partial

| Feature | Status |
|---------|--------|
| Summaries (`Sum`/`Average`/`Count`/`Range`) | Done |
| Row grouping (`Group`) | Done |
| Layout `Split`/`Stack`/`Panel` | Done |
| TextColumn money/date/description | Done |
| `TrashedFilter` + filter persist/defer flags | Done |
| Index search / sortable headers / pagination chrome | Done |
| Filter chrome (dropdown) + indicator chips + `setTableFilter` | Done |
| Empty state Create CTA + `record_url` row click | Done |
| Bulk selection + `BulkActionGroup` Actions dropdown | Done |
| Column `alignment` / `align_end` mirrored on headers | Done |
| Numbered pagination + per-page on one row | Done |
| Content-grid cards (title + stacked fields) | Done |
| Column visibility manager / breakpoint CSS | Partial |

## Actions — Partial

| Feature | Status |
|---------|--------|
| Create/Edit/View/Delete + modal URL modes | Done |
| Replicate / ForceDelete / Restore / Import / Export | Done |
| `ActionGroup` / `BulkActionGroup` + slide-over / modal width / sticky | Done |
| Host job runners for import/export | Partial (config + docs) |

## Panels / platform — Partial

| Feature | Status |
|---------|--------|
| List/Create/Edit/View page hosts + list tabs | Done |
| Global search helpers | Done |
| Clusters / auth pages / MFA protocol / tenancy | Done |
| Render hooks + Plugin base | Done |
| `discover_*` + `load_discovered` + scaffolding writes files | Done |
| User menu / multi-panel domains / SPA / billing adapters | Partial |
| Real DB notification persistence / Echo | Partial |

## Docs / screenshots

| Feature | Status |
|---------|--------|
| Real light/dark PNG examples under `docs/public/examples/{theme}/{section}/{name}.png` | Done |

| Gallery build + Playwright capture scripts | Done |
| Every field page with PNG (not HTML fence) | Partial |

Host-only concerns (SMTP MFA delivery, Spark billing, production queues) remain **interfaces + documented adapters**.

Keywords for smoke tests: resources, pages, relation managers, TextInput, Select, Repeater.
