---
title: Icon column
description: IconColumn — render a Heroicon from state, or boolean check/X with true/false icons.
---

`IconColumn` renders a Heroicon in the cell. Pass an icon name as the state, or use `.boolean()` for check / X icons.

## Standalone example

```python
from almasix.orbit.tables import Table, TextColumn, IconColumn

records = [
    {"id": 1, "name": "Ship", "icon": "heroicon-o-rocket-launch", "ok": True},
    {"id": 2, "name": "Hold", "icon": "heroicon-o-pause", "ok": False},
]

table = (
    Table.make("ops")
    .columns([
        TextColumn.make("name"),
        IconColumn.make("icon").size("lg").color("primary"),
        IconColumn.make("ok").boolean()
            .true_icon("heroicon-o-check")
            .false_icon("heroicon-o-x-mark"),
    ])
    .records(records)
)
```

## In a Resource example

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, IconColumn, TextColumn

class AlertResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            TextColumn.make("title").searchable(),
            IconColumn.make("severity")
                .format_state_using(lambda v: {
                    "info": "heroicon-o-information-circle",
                    "warn": "heroicon-o-exclamation-triangle",
                    "crit": "heroicon-o-fire",
                }.get(v, "heroicon-o-question-mark-circle"))
                .color(lambda state=None, **_: {
                    "info": "info",
                    "warn": "warning",
                    "crit": "danger",
                }.get(state, "gray")),
            IconColumn.make("acked").boolean().align_center(),
        ])
```

Non-boolean state is treated as an icon name (defaulting to `heroicon-o-check` if empty). For Yes/No **text**, use [`TextColumn.boolean()`](/tables/columns/boolean/) instead.

## Key methods

- `.boolean()` — check / X mode
- `.true_icon(name)` / `.false_icon(name)` — override glyphs
- `.size(value)` — size token (`sm`, `md`, `lg`, …)
- `.color(str | callable)` — theme color (boolean defaults success/danger)
- `.format_state_using(callback)` — map domain values → icon names
- `.align_center()` / `.sortable()`

## Preview

![Icon column (light)](/examples/light/tables/icon-boolean.png)
![Icon column (dark)](/examples/dark/tables/icon-boolean.png)
