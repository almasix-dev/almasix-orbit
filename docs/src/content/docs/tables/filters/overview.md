---
title: Table filters
description: Select, ternary, custom query, trashed, and grouped filters for Orbit tables.
---

Filters narrow which rows appear in a table. Define them on the table; the index host keeps `table_filters` state and applies them when rendering. Live selects call `setTableFilter(name, value)` on the host (Conduit only supports top-level props, so nested `table_filters.*` model paths are not used).

```python
from almasix.orbit.tables import (
    Table, TextColumn, Filter, SelectFilter, TernaryFilter, FilterGroup,
)

table = (
    Table.make("posts")
    .columns([TextColumn.make("title").searchable()])
    .filters([
        SelectFilter.make("status")
            .label("Status")
            .options({
                "draft": "Draft",
                "published": "Published",
            }),
        # Filter name ≠ column: point at the attribute
        SelectFilter.make("author")
            .attribute("author_id")
            .options(lambda **ctx: ctx.get("authors", {})),
        TernaryFilter.make("featured").label("Featured"),
        Filter.make("mine").query(
            lambda q, value: [r for r in q if r.get("mine")]
        ),
    ])
)
```

![Filters (light)](/examples/light/tables/filters.png)
![Filters (dark)](/examples/dark/tables/filters.png)

## Filter types

| Class | Role |
|-------|------|
| `Filter` | Base — `.options(...)`, `.query(callback)`, `.attribute(...)`, `.apply(query, value)` |
| `SelectFilter` | Dropdown; default equality on `attribute` or name |
| `TernaryFilter` | All / Yes / No for booleans |
| `TrashedFilter` | Soft-delete scopes |
| `FilterGroup` | Nest filters under a named group via `.filters([...])` |

`.apply()` is a no-op when the value is `None`, `""`, or `[]` (unless a custom `.query()` handles empty values on purpose).

### Filter groups

```python
from almasix.orbit.tables import FilterGroup, SelectFilter, TernaryFilter

FilterGroup.make("visibility").label("Visibility").filters([
    SelectFilter.make("status").options({
        "draft": "Draft",
        "published": "Published",
    }),
    TernaryFilter.make("featured"),
])
```

### Soft deletes

```python
from almasix.orbit.tables import TrashedFilter

table.filters([TrashedFilter.make()])
```

## Index chrome

List pages render a **Filters** dropdown with indicator chips for active values. Search sits on the **right** of the same toolbar row as the Filters trigger.

```python
table.defer_filters()  # require Apply instead of live updates
```

Use deferred filters when each change is expensive (large queries, remote APIs) or when operators prefer to set several values before applying.

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, TextColumn, SelectFilter, TernaryFilter

class PostResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.columns([
                TextColumn.make("title").searchable().sortable(),
                TextColumn.make("status").badge(),
            ])
            .filters([
                SelectFilter.make("status").options({
                    "draft": "Draft",
                    "review": "Review",
                    "published": "Published",
                }),
                TernaryFilter.make("featured").label("Featured"),
            ])
            .defer_filters()
        )
```

## Empty after filtering

When filters match no rows, the empty state still renders. Customize the copy on the table:

```python
table.empty_state_heading("No matches")
table.empty_state_description("Try clearing filters or broadening search.")
```

![Empty after filters (light)](/examples/light/tables/empty.png)
![Empty after filters (dark)](/examples/dark/tables/empty.png)

See also [Tables overview](/tables/overview/) and [standalone tables](/components/table/).
