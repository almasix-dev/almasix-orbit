---
title: Badge column
description: BadgeColumn — status and label values rendered as badges.
---

`BadgeColumn` is a `TextColumn` that always renders as a badge. Use it when every value in the column is a short status, tier, or similar label.

## Standalone example

```python
from almasix.orbit.tables import Table, TextColumn, BadgeColumn

table = (
    Table.make("tickets")
    .columns([
        TextColumn.make("subject").searchable(),
        BadgeColumn.make("status").color(
            lambda state=None, **_: {
                "open": "warning",
                "closed": "success",
                "blocked": "danger",
            }.get(state, "gray")
        ),
        BadgeColumn.make("priority").color("primary"),
    ])
    .records(records)
)
```

## In a Resource example

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, BadgeColumn, TextColumn

class TicketResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            TextColumn.make("subject").searchable().sortable(),
            BadgeColumn.make("status")
                .sortable()
                .color(lambda state=None, **_: "success" if state == "done" else "gray"),
        ])
```

Same result with text + badge:

```python
TextColumn.make("status").badge().color("primary")
# vs
BadgeColumn.make("status").color("primary")
```

Prefer `BadgeColumn` when the column is always a badge. Prefer `TextColumn.badge()` when you may switch between plain text and badge styling later.

## Key methods

- `.color(str | callable)` — theme color or per-state callback
- `.sortable()` / `.searchable()` / `.toggleable(...)`
- `.format_state_using(callback)` — map raw values to labels
- `.align_center()` — center the badge
- Inherited: `.label(...)`, `.limit(...)`, `.copyable()`, …

## Preview

![Badge column (light)](/examples/light/tables/text-features.png)
![Badge column (dark)](/examples/dark/tables/text-features.png)
