---
title: BooleanColumn
description: Orbit BooleanColumn — Yes / No cells for boolean attributes.
---

Truthy → Yes, everything else → No. Perfect for flags without inventing icons yet.

## Standalone

```python
from almasix.orbit.tables import Table, BooleanColumn

table = (
    Table.make("demo")
    .columns([
        BooleanColumn.make("featured").label("Featured"),
    ])
    .records(records)
)
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, BooleanColumn

class PostResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            BooleanColumn.make("is_published").sortable(),
            BooleanColumn.make("verified"),
        ])
```

## Key methods

- `Forces boolean rendering (`Yes` / `No`)`
- `.sortable() / .searchable()`
- `.color(...) still applies to the span`
- `.label(...)`

## Preview

![Orbit table example (light)](/examples/light/table.png)

![Orbit table example (dark)](/examples/dark/table.png)

