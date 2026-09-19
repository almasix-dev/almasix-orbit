# Feature polish tracker

Process: see [`.cursor/rules/feature-polish.mdc`](rules/feature-polish.mdc).

## Queue

| Order | Feature | Docs | Status |
|------:|---------|------|--------|
| 1 | Panel Configuration | `docs/src/content/docs/panels/configuration.md` | **closed** |
| 2 | Tables overview | `docs/src/content/docs/tables/overview.md` | **closed** |
| 3 | Columns overview | `docs/src/content/docs/tables/columns/overview.md` | **closed** |
| 4–16 | Column types | `docs/src/content/docs/tables/columns/*` | **closed** |
| 17 | Filters overview | `docs/src/content/docs/tables/filters/overview.md` | **closed** |
| 18 | Schemas overview | `docs/src/content/docs/schemas/overview.md` | **closed** |
| 19 | Layouts | `docs/src/content/docs/schemas/layouts.md` | **closed** |
| 20 | Grid | `docs/src/content/docs/schemas/grid.md` | **closed** |
| 21 | Flex | `docs/src/content/docs/schemas/flex.md` | **closed** |
| 22 | Group | `docs/src/content/docs/schemas/group.md` | **closed** |
| 23 | Split | `docs/src/content/docs/schemas/split.md` | **closed** |
| 24 | Fieldset | `docs/src/content/docs/schemas/fieldset.md` | **closed** |
| 25 | Sections | `docs/src/content/docs/schemas/sections.md` | **closed** |
| 26 | Tabs | `docs/src/content/docs/schemas/tabs.md` | **closed** |
| 27 | Wizards | `docs/src/content/docs/schemas/wizards.md` | **closed** |
| 28 | Callouts | `docs/src/content/docs/schemas/callouts.md` | **closed** |
| 29 | Empty states | `docs/src/content/docs/schemas/empty-states.md` | **closed** |
| 30 | Primes | `docs/src/content/docs/schemas/primes.md` | **closed** |
| 31+ | Remaining Orbit doc features | docs nav | queued |

## Schemas autopilot — closed

Filament 5 parity for every page under Schemas.

### Overview APIs

`Schema.operation` / `get_operation`, `defer_loading`, `configure_using`, state/fill/dehydrate, columns.

### Layout / prime highlights

| Surface | Highlights |
|---------|------------|
| Fieldset | `contained(False)` bare fieldset |
| Section | `secondary`, aside, persist_collapsed (docs) |
| Text prime | `font_family` |
| Image prime | `align_start` / `align_center` / `align_end` |

### Deferred

Breakpoint column maps on Grid, full Filament container-query grid system, custom schema components page, Livewire-only defer viewport loading.

### Close checklist

- [x] Gap matrices implemented for schemas pages
- [x] Docs rewritten Filament-depth; screenshots updated
- [x] Tests at 100% coverage
- [x] Status → **closed** for 18–30
