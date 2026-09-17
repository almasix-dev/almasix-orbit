---
title: IconColumn
description: Orbit IconColumn — render a Heroicon name from cell state.
---

Cell state is an icon name (or falls back to a check). Great for type indicators.

## Standalone

```python
from almasix.orbit.tables import Table, IconColumn

table = (
    Table.make("demo")
    .columns([
        IconColumn.make("icon"),
    ])
    .records(records)
)
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, IconColumn

class PostResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            IconColumn.make("kind")
                .format_state_using(lambda v: {
                    "user": "heroicon-o-user",
                    "team": "heroicon-o-user-group",
                }.get(v, "heroicon-o-question-mark-circle")),
        ])
```

## Key methods

- `State should be a Heroicon name like `heroicon-o-check``
- `.format_state_using(...) to map domain values → icons`
- `.label(...) / .sortable()`

## Preview

![Orbit table example (light)](/examples/light/table.png)

![Orbit table example (dark)](/examples/dark/table.png)

