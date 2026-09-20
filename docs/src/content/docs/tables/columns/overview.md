---
title: Columns overview
description: Shared Orbit table column APIs — state, sort, search, tooltips, toggleable columns, and the full type catalog.
---

## Introduction

**Columns** are the cells of an Orbit table. Each column has a name (usually a record attribute path), a type that controls how the value renders, and optional fluent helpers for sort, search, alignment, links, and visibility.

Start with a type from the [catalog](#catalog) below (`TextColumn`, `ImageColumn`, `BooleanColumn`, …), then chain shared helpers from the `Column` base — for example `.searchable()`, `.sortable()`, or `.toggleable()`.

```python
from almasix.orbit.tables import Table, TextColumn, BadgeColumn, ImageColumn

Table.make("inventory").columns([
    ImageColumn.make("avatar_url").circular().size(32),
    TextColumn.make("name").searchable().sortable().weight("bold"),
    BadgeColumn.make("status").color("success"),
    TextColumn.make("price").money("USD").align_end(),
])
```

![Columns overview (light)](/examples/light/tables/columns-overview.png)
![Columns overview (dark)](/examples/dark/tables/columns-overview.png)

Live sample: **Columns overview** in `examples/orbit-admin` (`ColumnsOverviewResource`).

## Catalog

| Column | One-liner | Docs |
|--------|-----------|------|
| **TextColumn** | Default cell — search, sort, money, dates, badges, links, markdown | [Text](/tables/columns/text/) |
| **BadgeColumn** | Text that always renders as a badge | [Badge](/tables/columns/badge/) |
| **BooleanColumn** | Check / X icons for truthy / falsy state | [Boolean](/tables/columns/boolean/) |
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

## Column content (state)

By default the column name is an attribute path on each record (including dotted keys like `author.name`).

### Custom state

```python
TextColumn.make("full_name").state(
    lambda record: f"{record['first_name']} {record['last_name']}"
)
```

### Default vs placeholder

`.default(...)` fills empty state and is treated as real state (images/colors still render).
`.placeholder(...)` only shows muted display text when the state is empty.

```python
TextColumn.make("nickname").default("—")
TextColumn.make("nickname").placeholder("No nickname")
```

### Format without changing state

```python
TextColumn.make("slug").format_state_using(lambda value: value.upper())
```

## Label

```python
TextColumn.make("name").label("Full name")
```

## Sorting

```python
TextColumn.make("name").sortable()
TextColumn.make("full_name").sortable(["last_name", "first_name"])
TextColumn.make("full_name").sortable(
    query=lambda records, direction: sorted(
        records,
        key=lambda r: (r["last_name"], r["first_name"]),
        reverse=direction == "desc",
    )
)
```

Table-level defaults: `.default_sort("name", "desc")` (see [Tables overview](/tables/overview/)).

## Searching

```python
TextColumn.make("name").searchable()
TextColumn.make("full_name").searchable(["first_name", "last_name", "email"])
TextColumn.make("name").searchable(
    query=lambda record, search: search in str(record.get("email", "")).lower()
)
```

Enable the search field with any searchable column, or `.searchable()` on the table.

## Tooltips

```python
TextColumn.make("email").tooltip("Click to copy")
TextColumn.make("email").header_tooltip("Primary contact")
```

## Alignment, width, and wrapping

```python
TextColumn.make("amount").align_end().vertically_align_center()
TextColumn.make("title").wrap_header().grow().width(240)
```

## Links

```python
TextColumn.make("website").url(lambda record, state, **_: state).open_url_in_new_tab()
```

## Visibility

```python
TextColumn.make("internal").hidden()
TextColumn.make("notes").visible(False)
TextColumn.make("email").visible_from("md").hidden_from("xl")
```

## Toggleable columns & column manager

```python
TextColumn.make("email").toggleable()
TextColumn.make("website").toggleable(is_toggled_hidden_by_default=True)

Table.make().reorderable_columns().columns([...])
```

![Column manager (light)](/examples/light/tables/columns-overview-manager.png)
![Column manager (dark)](/examples/dark/tables/columns-overview-manager.png)

Users toggle visibility in the columns dropdown. With `.reorderable_columns()`, they can also drag to reorder; the host persists order via `reorderColumns`.

## Extra HTML attributes

```python
TextColumn.make("status").extra_attributes({"data-tour": "status"})
TextColumn.make("status").extra_cell_attributes({"class": "or-status-cell"})
TextColumn.make("status").extra_header_attributes({"data-head": "status"})
```

## Global configuration

```python
from almasix.orbit.tables import Column, TextColumn

Column.configure_using(lambda column: column.align_start())
```

## Shared helpers (quick list)

- `.label(...)` / `.state(...)` / `.default(...)` / `.placeholder(...)`
- `.sortable(...)` / `.searchable(...)` / `.toggleable(...)`
- `.align_start()` / `.align_center()` / `.align_end()` / `.vertically_align_*()`
- `.tooltip(...)` / `.header_tooltip(...)` / `.wrap_header()` / `.width(...)` / `.grow()`
- `.format_state_using(...)` / `.url(...)` / `.open_url_in_new_tab()`
- `.color(...)` / `.visible_from(...)` / `.hidden_from(...)` / `.summarize(...)`
- `.extra_attributes(...)` / `.extra_cell_attributes(...)` / `.extra_header_attributes(...)`

Layout wrappers (`Split`, `Stack`, `Panel`, …) nest columns inside one cell — see [Layout](/tables/layout/).
