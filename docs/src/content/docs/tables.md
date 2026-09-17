---
title: Tables
description: Orbit tables — columns, search, sort, pagination, filters, and action slots.
---

Tables turn a list of records into searchable, sortable, actionable HTML.

```python
from almasix.orbit.tables import Table, TextColumn, SelectFilter
from almasix.orbit.actions import CreateAction, EditAction, DeleteAction

table = (
    Table.make("posts")
    .columns([
        TextColumn.make("title").searchable().sortable(),
        TextColumn.make("status").badge().color("primary"),
        TextColumn.make("published_at").sortable(),
    ])
    .filters([
        SelectFilter.make("status").options({
            "draft": "Draft",
            "published": "Published",
        }),
    ])
    .records(posts)
    .search("orbit")
    .sort("title", "asc")
    .paginate(page=1, per_page=15)
    .striped()
    .empty_state_heading("No posts yet")
    .empty_state_description("Create your first post to get going.")
    .header_actions([CreateAction.make()])
    .actions([EditAction.make(), DeleteAction.make()])
)
```

## Feeding records

| Method | Role |
|--------|------|
| `.records([...])` | In-memory list (dicts or objects) |
| `.query(any)` | Stores a query object for your app layer |

`get_records()` / `get_total()` operate on the in-memory list today — search hits **searchable** columns, sort uses the column name as a key/attribute, then pagination slices the result. Apply `.query()` yourself (or the [query builder](/query-builder/)) when you need a real database round-trip.

## Columns

```python
TextColumn.make("name")
    .label("Name")
    .sortable()
    .searchable()
    .toggleable()
    .format_state_using(lambda v: v.upper())
    .badge()
    .boolean()
    .color("success")          # or a callable
    .limit(40)
    .wrap()
    .url("/posts/{id}")
    .weight("bold")
    .copyable()
```

| Column | Behaviour |
|--------|-----------|
| `TextColumn` | Default |
| `BadgeColumn` | Always badge-styled |
| `BooleanColumn` | Yes / No |
| `ImageColumn` | Avatar-style `<img>` |
| `ColorColumn` | Color swatch |
| `TagsColumn` | List or comma-split → badges |
| `IconColumn`, `SelectColumn`, `CheckboxColumn`, `TextInputColumn`, `ToggleColumn`, `ViewColumn` | Available building blocks |
| `ColumnGroup` | `.columns([...])` grouping |

## Filters

```python
from almasix.orbit.tables import Filter, SelectFilter, TernaryFilter, FilterGroup

SelectFilter.make("status").options({...})
TernaryFilter.make("featured")   # yes / no / all
Filter.make("mine").query(lambda q, value: ...)
FilterGroup.make().filters([...])
```

Filters are stored on the table and expose `.apply(query, value)`. Wire them into your query layer — `get_records()` does not auto-apply them yet.

## Actions

Three slots:

```python
table.actions([...])         # per row
table.bulk_actions([...])    # selected rows
table.header_actions([...])  # top of the table
```

See [Actions](/actions/) for presets and custom callbacks.

## Render

```python
html = table.render()
data = table.to_dict()
```

Markup uses `.or-*` classes so the published Orbit CSS can dress it up.
