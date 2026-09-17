---
title: Select column
description: Orbit SelectColumn — inline select editor inside a table cell.
---

Edit without opening a page — options in the cell, `wire:model` on `table.{name}`.

## Standalone

```python
from almasix.orbit.tables import Table, SelectColumn

table = (
    Table.make("demo")
    .columns([
        SelectColumn.make("status").options({
            "draft": "Draft",
            "published": "Published",
        }),
    ])
    .records(records)
)
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, SelectColumn

class PostResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            SelectColumn.make("status")
                .options(lambda record=None, **_: {
                    "draft": "Draft",
                    "published": "Published",
                }),
        ])
```

## Key methods

- `.options(dict | callable) — callable gets `record` / `state``
- `Inline `<select class="or-select or-select-inline">``
- `.label(...) / .sortable()`

## Preview

![Orbit table example (light)](/examples/light/table.png)

![Orbit table example (dark)](/examples/dark/table.png)

