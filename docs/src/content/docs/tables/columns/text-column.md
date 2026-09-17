---
title: TextColumn
description: Orbit TextColumn — default table cell with sort, search, badge, and URL helpers.
---

The default cell. Text today, badge tomorrow, link when the row deserves a destination.

## Standalone

```python
from almasix.orbit.tables import Table, TextColumn

table = (
    Table.make("demo")
    .columns([
        TextColumn.make("title").searchable().sortable(),
        TextColumn.make("status").badge().color("primary"),
    ])
    .records(records)
)
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, TextColumn

class PostResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            TextColumn.make("title").searchable().sortable().limit(40),
            TextColumn.make("slug").copyable(),
            TextColumn.make("status").badge().color("success"),
        ])
```

## Key methods

- `.sortable() / .searchable() / .toggleable()`
- `.format_state_using(callback)`
- `.badge() / .boolean() / .color(str|callable)`
- `.limit(n) / .wrap() / .weight(...)`
- `.url(str|callable) / .copyable()`
- `.label(...)`

## Preview

![Orbit table example (light)](/examples/light/table.png)

![Orbit table example (dark)](/examples/dark/table.png)

