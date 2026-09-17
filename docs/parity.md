# Filament 5.x ↔ Orbit parity matrix (maintainer)

Orbit targets FilamentPHP **5.x** API familiarity on Almasix (Conduit + Alpine).

**Status values**

| Status | Meaning |
|--------|---------|
| **Done** | Fluent API + distinct `or-*` render + tests; docs list options (screenshots in exhaust PR7) |
| **Partial** | Class/API exists but missing Filament-depth knobs, host wiring, or real runtime |
| **Planned** | Not implemented yet |

Surface checklist ≠ Filament depth. Prefer Partial over Done when in doubt.

## Packages

| Filament package | Orbit package | Status |
|------------------|---------------|--------|
| support | `almasix-orbit-support` | Partial |
| schemas | `almasix-orbit-schemas` | Partial |
| forms | `almasix-orbit-forms` | Partial |
| tables | `almasix-orbit-tables` | Partial |
| actions | `almasix-orbit-actions` | Partial |
| infolists | `almasix-orbit-infolists` | Partial |
| notifications | `almasix-orbit-notifications` | Partial |
| widgets | `almasix-orbit-widgets` | Partial |
| query-builder | `almasix-orbit-query-builder` | Partial |
| panels | `almasix-orbit` (panels) | Partial |

## Support

| Feature | Status |
|---------|--------|
| `Component` + `evaluate()` closures | Done |
| Colors / curated Heroicons / HTML helpers | Partial |
| CSS hooks catalog / render hooks | Planned |
| Theme generator / density themes | Planned |

## Schemas

| Feature | Status |
|---------|--------|
| `Schema` container | Done |
| `Grid` (+ dense/gap/grid_container) | Done |
| `Flex` | Done |
| `Section` / `Tabs` / `Fieldset` / `Wizard` | Done |
| `Callout` / `EmptyState` | Done |
| Primes (`Text`, `Icon`, `Image`, `UnorderedList`) | Done |
| Custom schema components API | Planned |

## Forms

| Feature | Status |
|---------|--------|
| Field type checklist (TextInput, Select, Repeater, …) | Partial |
| Select searchable / relationship / create-option | Partial |
| FileUpload disk/avatar/image editor | Partial |
| Repeater/Builder DnD/clone/blocks | Partial |
| TipTap RichEditor | Partial |
| Full validation catalog | Partial |

## Tables

| Feature | Status |
|---------|--------|
| Search / sort / paginate / column types | Partial |
| Summaries / row grouping / layout Split-Stack | Planned |
| Filter session/defer/trashed UI | Planned |
| TextColumn money/date/markdown | Planned |

## Actions

| Feature | Status |
|---------|--------|
| Base Action + Create/Edit/View/Delete | Partial |
| Replicate / ForceDelete / Restore / Import / Export | Planned |
| ActionGroup + deep modal (slide-over, sticky) | Planned |

## Infolists / Notifications / Widgets / QB

| Feature | Status |
|---------|--------|
| Entry types + readonly form fallback | Partial |
| Flash notifications | Done |
| Database / broadcast notifications | Partial |
| Stats / Chart / Table widgets | Partial |
| Query builder apply + render | Partial |

## Panels / resources / platform

| Feature | Status |
|---------|--------|
| Panel shell + split nav | Partial |
| Resource config + page URL presets | Partial |
| Live CRUD page hosts (List/Create/Edit/View) | Planned |
| Global search / list tabs / clusters / user menu | Planned |
| Auth pages / MFA / tenancy | Planned |
| `discover_*` import walk / scaffolding | Planned |
| Plugins + testing suite depth | Planned |
| Real docs screenshots (PNG) | Planned |
