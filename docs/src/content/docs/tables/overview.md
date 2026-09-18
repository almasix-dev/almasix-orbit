---
title: Tables overview
description: Orbit tables — records, columns, money, editable cells, filters, actions, grouping, summaries, and layout.
---

Tables render searchable, sortable, filterable, and actionable HTML from records and column definitions. Use them standalone or through a Resource.

```python
from almasix.orbit.tables import (
    Table, TextColumn, SelectColumn, SelectFilter, Sum, Group,
)
from almasix.orbit.actions import CreateAction, EditAction, DeleteAction

table = (
    Table.make("posts")
    .columns([
        TextColumn.make("title").searchable().sortable(),
        TextColumn.make("status").badge().color("primary"),
        TextColumn.make("amount").money("USD").align_end().summarize(Sum.make()),
        SelectColumn.make("priority").options({
            "low": "Low",
            "high": "High",
        }),
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
    .default_group(Group.make("status").collapsible())
    .empty_state_heading("No posts yet")
    .empty_state_description("Create your first post to get going.")
    .header_actions([CreateAction.make()])
    .actions([EditAction.make(), DeleteAction.make()])
)
```

![Table overview (light)](/examples/light/tables/overview.png)
![Table overview (dark)](/examples/dark/tables/overview.png)

## Guides

| Page | What you’ll find |
|------|------------------|
| [Standalone tables](/components/table/) | Tables outside a Resource |
| [Columns catalog](/tables/columns/overview/) | Every column type |
| [Text / money](/tables/columns/text/) | Search, sort, badge, currency, copyable, markdown |
| [Editable columns](/tables/columns/select/) | Inline select / toggle / text / checkbox |
| [Filters](/tables/filters/overview/) | Select, ternary, groups, deferred apply |
| [Actions](/tables/actions/) | Row, bulk, header, and dropdowns |
| [Layout](/tables/layout/) | Split, Stack, Panel, Grid, View |
| [Summaries](/tables/summaries/) | Sum, Average, Count, Range (including money) |
| [Grouping](/tables/grouping/) | `default_group` and collapsible groups |

## Feeding records

| Method | Role |
|--------|------|
| `.records([...])` | In-memory list (dicts or objects) |
| `.query(any)` | Stores a query object for your app layer |

`get_records()` / `get_total()` operate on the in-memory list: search uses **searchable** columns, sort uses the column name as a key or attribute, then pagination slices the result. Use `.query()` (or the [query builder](/query-builder/overview/)) when the database should filter, sort, and paginate.

```python
Table.make("orders")
    .columns([TextColumn.make("sku").searchable().sortable()])
    .records([
    {"id": 1, "sku": "ORB-01", "amount": 1200},
    {"id": 2, "sku": "ORB-02", "amount": 450},
])
    .search("ORB")
    .sort("sku", "asc")
    .paginate(page=1, per_page=25)
```

## Columns inventory

Column types live under `almasix.orbit.tables`. Start with [TextColumn](/tables/columns/text/). Use specialized types for icons, images, or inline editors.

| Column | Job |
|--------|-----|
| [`TextColumn`](/tables/columns/text/) | Default cell — money, dates, badges, links |
| [`BadgeColumn`](/tables/columns/badge/) | Always-on badge styling |
| [`BooleanColumn`](/tables/columns/boolean/) / [`IconColumn`](/tables/columns/icon/) | Check / X icons (or Yes/No text via `.boolean()`) |
| [`ImageColumn`](/tables/columns/image/) | Avatars — circular, stacked, sized |
| [`ColorColumn`](/tables/columns/color/) | Hex swatches, optionally copyable |
| [`SelectColumn`](/tables/columns/select/) | Inline `<select>` |
| [`ToggleColumn`](/tables/columns/toggle/) | Inline toggle |
| [`TextInputColumn`](/tables/columns/text-input/) | Inline text field |
| [`CheckboxColumn`](/tables/columns/checkbox/) | Inline checkbox |
| [`TagsColumn`](/tables/columns/tags/) | List → badge cluster |
| [`ViewColumn`](/tables/columns/view/) | Custom HTML |
| [`ColumnGroup`](/tables/columns/column-group/) | Dual header over child columns |

### Money

Currency formatting is available on text columns and summarizers:

```python
TextColumn.make("amount").money("USD")
TextColumn.make("cents").money("USD", divide_by=100).align_end()
```

![Money column (light)](/examples/light/tables/money.png)
![Money column (dark)](/examples/dark/tables/money.png)

### Editable cells

`SelectColumn`, `TextInputColumn`, `ToggleColumn`, and `CheckboxColumn` render controls with `data-orbit-column-edit`. On list hosts, `orbit.js` posts changes through `ListRecordsHost.update_column_state`.

```python
from almasix.orbit.tables import SelectColumn, TextInputColumn, ToggleColumn, CheckboxColumn

# Persist via ListRecordsHost.update_column_state / orbit.js
SelectColumn.make("status").options({"draft": "Draft", "published": "Published"})
TextInputColumn.make("sku")
ToggleColumn.make("featured")
CheckboxColumn.make("approved")
```

![Editable columns (light)](/examples/light/tables/editable.png)
![Editable columns (dark)](/examples/dark/tables/editable.png)

## Filters

Narrow the list without rewriting your query by hand. See [Filters](/tables/filters/overview/) for `SelectFilter`, `TernaryFilter`, `Filter`, `TrashedFilter`, and `FilterGroup`.

```python
from almasix.orbit.tables import SelectFilter, TernaryFilter

table.filters([
    SelectFilter.make("status").options({"draft": "Draft", "published": "Published"}),
    TernaryFilter.make("featured").label("Featured"),
]).defer_filters()  # Apply button instead of live updates
```

![Filters (light)](/examples/light/tables/filters.png)
![Filters (dark)](/examples/dark/tables/filters.png)

## Actions

Three slots:

```python
table.actions([...])         # per row (⋮ dropdown when crowded)
table.bulk_actions([...])    # selected rows
table.header_actions([...])  # top of the table
```

Danger-colored actions confirm by default. Details live on [table actions](/tables/actions/) and [panel actions](/panels/actions/).

![Row / bulk actions (light)](/examples/light/tables/actions.png)
![Row / bulk actions (dark)](/examples/dark/tables/actions.png)

## Grouping & summaries

Partition rows with [`default_group`](/tables/grouping/); roll up numbers with [`.summarize(...)`](/tables/summaries/).

```python
from almasix.orbit.tables import Group, Sum, Average

table.default_group(Group.make("status").label("Status").collapsible())
table.columns([
    TextColumn.make("amount").money("USD").summarize(
        Sum.make().money("USD"),
        Average.make().money("USD"),
    ),
]).summaries(page=True, all=True)
```

## Cell layout

Nest columns inside one cell with [`Split` / `Stack` / `Panel` / `Grid` / `View`](/tables/layout/).

## Empty state

When there are no rows:

```python
table.empty_state_heading("Nothing here")
table.empty_state_description("Try clearing filters, or create a record.")
table.empty_state_actions([CreateAction.make()])
```

![Empty state (light)](/examples/light/tables/empty.png)
![Empty state (dark)](/examples/dark/tables/empty.png)

## Render

```python
html = table.render()
data = table.to_dict()
```

Markup uses `.or-*` classes so published Orbit CSS can style it. Prefer a [Resource](/resources/listing-records/) for CRUD wiring; use a [standalone table](/components/table/) when embedding a list in a custom page or Conduit host.
