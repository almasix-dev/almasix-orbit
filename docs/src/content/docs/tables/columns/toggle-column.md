---
title: ToggleColumn
description: Orbit ToggleColumn — live boolean toggle inside a table cell.
---

Flip a flag without a modal. Uses `wire:model.live` so the row updates immediately.

## Standalone

```python
from almasix.orbit.tables import Table, ToggleColumn

table = (
    Table.make("demo")
    .columns([
        ToggleColumn.make("is_published"),
    ])
    .records(records)
)
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, ToggleColumn

class PostResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            ToggleColumn.make("featured").label("Featured"),
            ToggleColumn.make("is_published"),
        ])
```

## Key methods

- ``or-toggle` + `wire:model.live="table.{name}"``
- `.label(...) / .sortable()`

## Preview

```html
<td class="or-td">
  <input type="checkbox" class="or-toggle" name="is_published" checked wire:model.live="table.is_published" />
</td>
```
