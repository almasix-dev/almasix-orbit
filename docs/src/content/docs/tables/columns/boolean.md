---
title: Boolean column
description: BooleanColumn and IconColumn.boolean() render check/X icons; TextColumn.boolean() renders Yes/No text.
---

## Introduction

Boolean fields show up often in admin tables — enabled flags, verification state, feature toggles. Orbit gives you three ways to display that state: icon check/X cells, the same icons via `IconColumn`, or plain Yes/No text.

`BooleanColumn` is a convenience column that is already an [`IconColumn`](/tables/columns/icon/) with `.boolean()` applied — a check icon (`success`) when truthy, an X icon (`danger`) when falsy:

```python
from almasix.orbit.tables import BooleanColumn

BooleanColumn.make("enabled")
```

## `BooleanColumn` vs. `IconColumn.boolean()` vs. `TextColumn.boolean()`

All three read the same underlying state; they differ only in what renders:

| API | Renders |
|-----|---------|
| `BooleanColumn.make(...)` | Check / X icons |
| `IconColumn.make(...).boolean()` | Same icons — customize with [`.true_icon()` / `.false_icon()`](/tables/columns/icon/#customizing-the-boolean-icons) |
| `TextColumn.make(...).boolean()` | `"Yes"` / `"No"` text |

```python
from almasix.orbit.tables import BooleanColumn, IconColumn, TextColumn

BooleanColumn.make("enabled")
IconColumn.make("verified").boolean().true_icon("heroicon-o-check")
TextColumn.make("featured").boolean()
```

## Customizing the icons and colors

Because `BooleanColumn` *is* an `IconColumn`, every [icon column](/tables/columns/icon/#boolean-icons) helper works on it directly:

```python
BooleanColumn.make("verified")
    .true_icon("heroicon-o-check")
    .false_icon("heroicon-o-x-mark")
    .true_color("info")
    .false_color("gray")
```

## Full example

```python
from almasix.orbit.tables import Table, TextColumn, BooleanColumn, IconColumn

Table.make("features").columns([
    TextColumn.make("name").searchable(),
    BooleanColumn.make("enabled").sortable().align_center(),
    IconColumn.make("verified")
        .boolean()
        .true_icon("heroicon-o-check")
        .false_icon("heroicon-o-x-mark")
        .align_center(),
    TextColumn.make("beta").boolean().label("Beta?"),
]).records([
    {"id": 1, "name": "Dark mode", "enabled": True, "verified": True, "beta": False},
    {"id": 2, "name": "AI summaries", "enabled": False, "verified": False, "beta": True},
])
```

## Key methods

| Method | Effect |
|--------|--------|
| `.boolean()` | Switch icon (or text, on `TextColumn`) mode on |
| `.true_icon(...)` / `.false_icon(...)` | Heroicon names (`IconColumn` / `BooleanColumn`) |
| `.true_color(...)` / `.false_color(...)` | Override the default success / danger colors |
| `.size(...)` | Icon size class |
| `.color(str \| callable)` | Explicit color — wins over true/false color |
| `.sortable()` / `.align_center()` | Inherited [shared helpers](/tables/columns/overview/) |

## Preview

![Boolean column (light)](/examples/light/tables/boolean-column.png)
![Boolean column (dark)](/examples/dark/tables/boolean-column.png)

![Icon / boolean (light)](/examples/light/tables/icon-boolean.png)
![Icon / boolean (dark)](/examples/dark/tables/icon-boolean.png)
