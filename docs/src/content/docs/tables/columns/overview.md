---
title: Columns overview
description: Catalog of every Orbit table column type — text, money, icons, images, editable cells, and groups.
---

Columns define how each field is displayed or edited in a table. Choose a type, then chain fluent helpers as needed.

```python
from almasix.orbit.tables import Table, TextColumn, BadgeColumn, ImageColumn

Table.make("inventory").columns([
    ImageColumn.make("avatar_url").circular().size(32),
    TextColumn.make("name").searchable().sortable().weight("bold"),
    BadgeColumn.make("status").color("success"),
    TextColumn.make("price").money("USD").align_end(),
])
```

![Column catalog (light)](/examples/light/tables/overview.png)
![Column catalog (dark)](/examples/dark/tables/overview.png)

## Catalog

| Column | One-liner | Docs |
|--------|-----------|------|
| **TextColumn** | Default cell — search, sort, money, dates, badges, links, markdown | [Text](/tables/columns/text/) |
| **BadgeColumn** | Text that always renders as a badge | [Badge](/tables/columns/badge/) |
| **BooleanColumn** | Check / X icons (Filament `IconColumn.boolean` alias) | [Boolean](/tables/columns/boolean/) |
| **IconColumn** | Icon from state, or boolean icons via `.boolean()` | [Icon](/tables/columns/icon/) |
| **ImageColumn** | Avatars — circular, stacked, sized, default URL | [Image](/tables/columns/image/) |
| **ColorColumn** | Hex swatch, optionally copyable | [Color](/tables/columns/color/) |
| **SelectColumn** | Inline `<select>` — persists via `update_column_state` | [Select](/tables/columns/select/) |
| **ToggleColumn** | Inline toggle switch | [Toggle](/tables/columns/toggle/) |
| **TextInputColumn** | Inline text field | [Text input](/tables/columns/text-input/) |
| **CheckboxColumn** | Inline checkbox | [Checkbox](/tables/columns/checkbox/) |
| **TagsColumn** | List (or CSV string) → badge cluster | [Tags](/tables/columns/tags/) |
| **ViewColumn** | Custom HTML via `.content(...)` | [View](/tables/columns/view/) |
| **ColumnGroup** | Dual header: `ColumnGroup.make('Label', [cols])` | [Column group](/tables/columns/column-group/) |

### Money & numbers

```python
TextColumn.make("amount").money("USD")
TextColumn.make("cents").money("USD", divide_by=100).align_end()
```

![Money (light)](/examples/light/tables/money.png)
![Money (dark)](/examples/dark/tables/money.png)

### Icons & booleans

![Icon / boolean (light)](/examples/light/tables/icon-boolean.png)
![Icon / boolean (dark)](/examples/dark/tables/icon-boolean.png)

### Images & color

![Image / color (light)](/examples/light/tables/image-color.png)
![Image / color (dark)](/examples/dark/tables/image-color.png)

### Editable columns

![Editable cells (light)](/examples/light/tables/editable.png)
![Editable cells (dark)](/examples/dark/tables/editable.png)

```python
SelectColumn, TextInputColumn, ToggleColumn, CheckboxColumn
# persist via ListRecordsHost.update_column_state / orbit.js
```

### Tags, view & groups

![Tags / view (light)](/examples/light/tables/tags-view.png)
![Tags / view (dark)](/examples/dark/tables/tags-view.png)

![Column group (light)](/examples/light/tables/column-group.png)
![Column group (dark)](/examples/dark/tables/column-group.png)

## Shared helpers

Most columns inherit from `Column`, so these are available across types:

- `.label(...)` / `.sortable()` / `.searchable()` / `.toggleable(...)`
- `.align_start()` / `.align_center()` / `.align_end()`
- `.format_state_using(callback)` / `.color(str | callable)`
- `.visible_from(...)` / `.hidden_from(...)` / `.summarize(...)`

Layout wrappers (`Split`, `Stack`, `Panel`, …) nest columns inside one cell — see [Layout](/tables/layout/).
