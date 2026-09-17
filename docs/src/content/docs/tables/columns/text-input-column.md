---
title: TextInputColumn
description: Orbit TextInputColumn — inline text input with blur-sync.
---

Quick edits in place. Saves on blur via `wire:model.blur`.

## Standalone

```python
from almasix.orbit.tables import Table, TextInputColumn

table = (
    Table.make("demo")
    .columns([
        TextInputColumn.make("title"),
    ])
    .records(records)
)
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, TextInputColumn

class PostResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            TextInputColumn.make("sku").label("SKU"),
            TextInputColumn.make("sort_order"),
        ])
```

## Key methods

- ``or-input or-input-inline``
- ``wire:model.blur="table.{name}"``
- `.label(...) / .format_state_using(...)`

## Preview

```html
<td class="or-td">
  <input class="or-input or-input-inline" name="title" value="Shipping Orbit docs" wire:model.blur="table.title" />
</td>
```
