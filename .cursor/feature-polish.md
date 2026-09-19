# Feature polish tracker

Process: see [`.cursor/rules/feature-polish.mdc`](rules/feature-polish.mdc).

## Queue

| Order | Feature | Docs | Status |
|------:|---------|------|--------|
| 1 | Panel Configuration | `docs/src/content/docs/panels/configuration.md` | **closed** |
| 2 | Tables overview | `docs/src/content/docs/tables/overview.md` | **closed** |
| 3 | Columns overview | `docs/src/content/docs/tables/columns/overview.md` | **closed** |
| 4 | Text column | `docs/src/content/docs/tables/columns/text.md` | **closed** |
| 5 | Icon column | `docs/src/content/docs/tables/columns/icon.md` | **closed** |
| 6 | Image column | `docs/src/content/docs/tables/columns/image.md` | **closed** |
| 7 | Color column | `docs/src/content/docs/tables/columns/color.md` | **closed** |
| 8 | Select column | `docs/src/content/docs/tables/columns/select.md` | **closed** |
| 9 | Toggle column | `docs/src/content/docs/tables/columns/toggle.md` | **closed** |
| 10 | Text input column | `docs/src/content/docs/tables/columns/text-input.md` | **closed** |
| 11 | Checkbox column | `docs/src/content/docs/tables/columns/checkbox.md` | **closed** |
| 12 | Badge column | `docs/src/content/docs/tables/columns/badge.md` | **closed** |
| 13 | Boolean column | `docs/src/content/docs/tables/columns/boolean.md` | **closed** |
| 14 | Tags column | `docs/src/content/docs/tables/columns/tags.md` | **closed** |
| 15 | View column | `docs/src/content/docs/tables/columns/view.md` | **closed** |
| 16 | Column group | `docs/src/content/docs/tables/columns/column-group.md` | **closed** |
| 17 | Filters overview | `docs/src/content/docs/tables/filters/overview.md` | **closed** |
| 18+ | Remaining Orbit doc features | docs nav | queued |

## Filters overview — closed

Filament 5 parity for `tables/filters/overview` (single Filters nav page).

### Shipped

- `Filter.toggle()`, checkbox default UI, `indicate` / `indicate_using`
- `SelectFilter.multiple()`, `selectable_placeholder`
- `TernaryFilter` labels / `nullable` / `queries`; working `FilterGroup`
- Defaults, `persist_filters_in_session` (sessionStorage), `hidden_filter_indicators`, `deselect_all_records_when_filtered`

### Deferred

Eloquent `relationship` / searchable selects, full FiltersLayout modes, query-builder product polish (own docs).

## Column types autopilot — closed

Filament 5 parity pass for every page under Columns (excluding overview, closed earlier).

### Shared / Text

`icon_position`, `icon_color`, `size`, `font_family`, `limit(end=)`, `words`, `line_clamp`, `description(position=)`, `separator`, `bulleted`, `time`, `since`, `copy_message` / `copy_message_duration`, `money(decimal_places=)`, callable `badge`, editable `before_state_updated` / `after_state_updated`.

### Per type

| Type | Highlights |
|------|------------|
| Icon | `true_color` / `false_color`; `.icon()` callback for non-boolean |
| Image | `alt`, `square`, `image_width`/`height`, `ring`, `overlap`, `extra_img_attributes` |
| Color | copy message attrs |
| Select | `selectable_placeholder`, `disable_option_when`, lifecycle hooks |
| Toggle / Checkbox | lifecycle hooks |
| Text input | `type`, `input_mode`, `step`, `prefix`, `suffix`, hooks |
| Tags | `separator`, `limit` (+N), color |
| View | URL wrap |
| Column group | `align_*`, `wrap_header` |

### Deferred

Eloquent relationship aggregates, storage disks, native JS selects / searchable options, Laravel policy auto-checks.

### Close checklist

- [x] Gap matrices implemented for all column type pages
- [x] Docs rewritten Filament-depth; screenshots match snippets
- [x] orbit-admin samples updated
- [x] Tests at 100% coverage
- [x] Status → **closed** for types 4–16
