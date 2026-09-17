---
title: CheckboxColumn
description: Orbit CheckboxColumn — boolean checkbox editor in a cell.
---

Inline checkbox wired to `table.{name}` — bulk-adjacent edits without leaving the grid.

## Standalone

```python
from almasix.orbit.tables import Table, CheckboxColumn

table = (
    Table.make("demo")
    .columns([
        CheckboxColumn.make("featured"),
    ])
    .records(records)
)
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, CheckboxColumn

class PostResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            CheckboxColumn.make("is_active").label("Active"),
            CheckboxColumn.make("featured"),
        ])
```

## Key methods

- `Renders `or-checkbox` with `wire:model="table.{name}"``
- `.label(...) / .sortable()`
- `.format_state_using(...) rarely needed`

## Preview

```html
<td class="or-td">
  <input type="checkbox" class="or-checkbox" name="featured" checked wire:model="table.featured" />
</td>
```
