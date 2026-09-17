---
title: Overview
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

## Guides

| Page | What you’ll find |
|------|------------------|
| [Standalone tables](/components/table/) | Tables outside a Resource |
| [Filters](/tables/filters/overview/) | Select, ternary, groups, `.apply` |
| [Column reference](/tables/columns/text/) | Every column type |

## Feeding records

| Method | Role |
|--------|------|
| `.records([...])` | In-memory list (dicts or objects) |
| `.query(any)` | Stores a query object for your app layer |

`get_records()` / `get_total()` operate on the in-memory list today — search hits **searchable** columns, sort uses the column name as a key/attribute, then pagination slices the result. Apply `.query()` yourself (or the [query builder](/query-builder/overview/)) when you need a real database round-trip.

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

| Column | Page |
|--------|------|
| `TextColumn` | [TextColumn](/tables/columns/text/) |
| `BadgeColumn` | [BadgeColumn](/tables/columns/badge/) |
| `BooleanColumn` | [BooleanColumn](/tables/columns/boolean/) |
| `IconColumn` | [IconColumn](/tables/columns/icon/) |
| `ImageColumn` | [ImageColumn](/tables/columns/image/) |
| `ColorColumn` | [ColorColumn](/tables/columns/color/) |
| `TagsColumn` | [TagsColumn](/tables/columns/tags/) |
| `SelectColumn` | [SelectColumn](/tables/columns/select/) |
| `CheckboxColumn` | [CheckboxColumn](/tables/columns/checkbox/) |
| `TextInputColumn` | [TextInputColumn](/tables/columns/text-input/) |
| `ToggleColumn` | [ToggleColumn](/tables/columns/toggle/) |
| `ViewColumn` | [ViewColumn](/tables/columns/view/) |
| `ColumnGroup` | [ColumnGroup](/tables/columns/column-group/) |

## Filters

See [Filters](/tables/filters/overview/) for `SelectFilter`, `TernaryFilter`, `Filter`, and `FilterGroup`.

## Actions

Three slots:

```python
table.actions([...])         # per row
table.bulk_actions([...])    # selected rows
table.header_actions([...])  # top of the table
```

See [Actions](/actions/overview/) and [Panel actions](/panels/actions/) for presets, modals, and `mountAction`.

## Render

```python
html = table.render()
data = table.to_dict()
```

Markup uses `.or-*` classes so the published Orbit CSS can dress it up.

## Preview

![Table (light)](/examples/light/table.png)

![Table (dark)](/examples/dark/table.png)
