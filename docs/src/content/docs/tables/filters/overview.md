---
title: Overview
description: Select, ternary, custom query filters, and filter groups for Orbit tables.
---

Filters follow Filament’s fluent style. Define them on the table; the index host keeps `table_filters` state and applies them when rendering.

```python
from almasix.orbit.tables import (
    Table, TextColumn, Filter, SelectFilter, TernaryFilter,
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
        # Filter name ≠ column: use attribute()
        SelectFilter.make("author")
        .attribute("author_id")
        .options(lambda **ctx: ctx.get("authors", {})),
        TernaryFilter.make("featured").label("Featured"),
        Filter.make("mine").query(lambda q, value: [r for r in q if r.get("mine")]),
    ])
)
```

## Filter types

| Class | Role |
|-------|------|
| `Filter` | Base — `.options(...)`, `.query(callback)`, `.attribute(...)`, `.apply(query, value)` |
| `SelectFilter` | Dropdown; default equality on `attribute` or name |
| `TernaryFilter` | All / Yes / No for booleans |
| `TrashedFilter` | Soft-delete scopes |
| `FilterGroup` | Nest filters under a named group via `.filters([...])` |

`.apply()` is a no-op when the value is `None`, `""`, or `[]` (unless a custom `.query()` handles it).

## Index chrome

List pages render a **Filters** dropdown (Filament default) with indicator chips for active values. Live selects call `setTableFilter(name, value)` on the host (Conduit only supports top-level props, so nested `table_filters.*` model paths are not used). Use `.defer_filters()` to require an Apply button.

Search sits on the **right** of the same toolbar row as the Filters trigger.
