---
title: Standalone tables
description: Build and render Orbit tables outside a Resource.
---

Tables don’t require a resource registration ceremony. Feed them records, columns, and optional actions — render HTML when you’re ready.

```python
from almasix.orbit.tables import Table, TextColumn, BadgeColumn, SelectFilter
from almasix.orbit.actions import EditAction, DeleteAction

table = (
    Table.make("posts")
    .columns([
        TextColumn.make("title").searchable().sortable(),
        BadgeColumn.make("status").color("primary"),
    ])
    .filters([
        SelectFilter.make("status").options({
            "draft": "Draft",
            "published": "Published",
        }),
    ])
    .records([
        {"id": 1, "title": "Shipping Orbit docs", "status": "published"},
        {"id": 2, "title": "Panel brand colors", "status": "draft"},
    ])
    .search("orbit")
    .sort("title", "asc")
    .paginate(page=1, per_page=15)
    .striped()
    .actions([EditAction.make(), DeleteAction.make()])
)

html = table.render()
```

## Lifecycle

| Step | Method |
|------|--------|
| Shape | `.columns([...])` |
| Narrow | `.filters([...])`, `.search(...)`, `.sort(...)` |
| Feed | `.records([...])` or `.query(...)` |
| Page | `.paginate(page, per_page)` |
| Chrome | `.striped()`, empty-state copy, action slots |
| Paint | `.render()` / `.to_dict()` |

```html
<div class="or-table-wrap">
  <table class="or-table or-table-striped">
    <thead>
      <tr>
        <th class="or-th">Title</th>
        <th class="or-th">Status</th>
        <th class="or-th"></th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="or-td"><span class="or-cell-text">Shipping Orbit docs</span></td>
        <td class="or-td"><span class="or-badge or-color-primary">published</span></td>
        <td class="or-td"><!-- row actions --></td>
      </tr>
    </tbody>
  </table>
</div>
```

In-memory search hits **searchable** columns; sort uses the column name as a key/attribute. Wire `.query()` (or the [query builder](/query-builder/)) when the database should do the heavy lifting.

See [Filters](/tables/filters/) and [column types](/tables/columns/text-column/) for the rest of the kit.
