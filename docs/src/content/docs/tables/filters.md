---
title: Table filters
description: Select, ternary, custom query filters, and filter groups for Orbit tables.
---

Filters are the polite bouncers of your index page — they remember options, expose `.apply()`, and leave the actual query surgery to you.

```python
from almasix.orbit.tables import (
    Table, TextColumn, Filter, SelectFilter, TernaryFilter, FilterGroup,
)

table = (
    Table.make("posts")
    .columns([TextColumn.make("title").searchable()])
    .filters([
        SelectFilter.make("status").options({
            "draft": "Draft",
            "published": "Published",
        }),
        TernaryFilter.make("featured").label("Featured"),
        Filter.make("mine").query(lambda q, value: q.where("author_id", value)),
        FilterGroup.make("advanced").filters([
            SelectFilter.make("locale").options({"en": "English", "ar": "Arabic"}),
        ]),
    ])
)
```

## Filter types

| Class | Role |
|-------|------|
| `Filter` | Base — `.options(...)`, `.query(callback)`, `.apply(query, value)` |
| `SelectFilter` | Dropdown-shaped options |
| `TernaryFilter` | Yes / no / all energy for booleans |
| `FilterGroup` | Nest filters under a named group via `.filters([...])` |

```python
SelectFilter.make("status").options(lambda **ctx: ctx.get("statuses", {}))

Filter.make("author").query(lambda q, value: q.where("author_id", value))

# apply when your request layer has a value
query = status_filter.apply(query, request.input("status"))
```

`.apply()` is a no-op when the value is `None`, `""`, or `[]`, or when no `.query()` callback was set.

## Important today

`Table.get_records()` does **not** auto-apply filters yet. Store them on the table, read them in your page/component, and push values into your query layer (or [query builder](/query-builder/)).

```html
<div class="or-filters">
  <div class="or-field or-field-SelectFilter" data-filter="status">
    <label class="or-label">Status</label>
    <select class="or-select" name="filters[status]" wire:model.live="filters.status">
      <option value="">All</option>
      <option value="draft">Draft</option>
      <option value="published">Published</option>
    </select>
  </div>
</div>
```

Options accept callables — same [evaluate](/support/closures/) rules as forms.
