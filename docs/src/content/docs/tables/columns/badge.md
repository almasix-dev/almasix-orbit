---
title: Badge column
description: Orbit BadgeColumn — always renders state inside an or-badge.
---

TextColumn that already checked `.badge()` for you — status pills without the extra call.

## Standalone

```python
from almasix.orbit.tables import Table, BadgeColumn

table = (
    Table.make("demo")
    .columns([
        BadgeColumn.make("status").color("success"),
    ])
    .records(records)
)
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, BadgeColumn

class PostResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            BadgeColumn.make("status")
                .color(lambda record=None, state=None, **_: "success" if state == "published" else "gray"),
        ])
```

## Key methods

- `Badge styling is on by default`
- `.color(str|callable) with `record` / `state` context`
- `.sortable() / .searchable()`
- `.format_state_using(...) / .label(...)`

## Preview

![Orbit table example (light)](/examples/light/tables/overview.png)

![Orbit table example (dark)](/examples/dark/tables/overview.png)

