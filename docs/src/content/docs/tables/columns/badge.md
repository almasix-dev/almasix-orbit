---
title: Badge column
description: BadgeColumn — a TextColumn that always renders as a badge.
---

`BadgeColumn` is a thin subclass of [`TextColumn`](/tables/columns/text/) with `.badge()` already applied. Use it when a column is *always* a status, tier, or label — you get every `TextColumn` helper (color, icon, format, sort, search) without having to remember `.badge()`:

```python
from almasix.orbit.tables import BadgeColumn

BadgeColumn.make("status").color(
    lambda state=None, **_: {"open": "warning", "closed": "success", "blocked": "danger"}.get(
        state, "gray",
    ),
)
```

## `BadgeColumn` vs. `TextColumn.badge()`

Both produce identical markup:

```python
TextColumn.make("status").badge().color("primary")
# renders the same as:
BadgeColumn.make("status").color("primary")
```

Prefer `BadgeColumn` when the column is always a badge — it documents intent at a glance. Prefer `TextColumn.badge()` (with a boolean or callable condition) when the same column sometimes renders as plain text, e.g. only badging non-default states.

## Adding an icon

`BadgeColumn` supports every [`TextColumn`](/tables/columns/text/) helper, including icons:

```python
BadgeColumn.make("priority").icon("heroicon-o-exclamation-triangle").color("danger")
```

## Full example

```python
from almasix.orbit.tables import Table, TextColumn, BadgeColumn

Table.make("tickets").columns([
    TextColumn.make("subject").searchable(),
    BadgeColumn.make("status").sortable().color(
        lambda state=None, **_: {"open": "warning", "closed": "success"}.get(state, "gray"),
    ),
    BadgeColumn.make("priority").color("primary"),
]).records([
    {"id": 1, "subject": "Payments down", "status": "open", "priority": "urgent"},
    {"id": 2, "subject": "Typo on homepage", "status": "closed", "priority": "low"},
])
```

## Key methods

| Method | Effect |
|--------|--------|
| `.color(str \| callable)` | Badge background color |
| `.icon(...)` / `.icon_position(...)` | Icon inside the badge |
| `.format_state_using(callback)` | Map raw values → labels |
| `.sortable()` / `.searchable()` / `.toggleable(...)` | Inherited [shared helpers](/tables/columns/overview/) |
| `.align_center()` | Center the badge |
| Inherited from [`TextColumn`](/tables/columns/text/) | `.limit(...)`, `.copyable()`, `.weight(...)`, … |

## Preview

![Badge column (light)](/examples/light/tables/badge-column.png)
![Badge column (dark)](/examples/dark/tables/badge-column.png)

![Text features (light)](/examples/light/tables/text-features.png)
![Text features (dark)](/examples/dark/tables/text-features.png)
