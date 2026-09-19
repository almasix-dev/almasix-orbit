---
title: Icon column
description: IconColumn — render a Heroicon from state, boolean check/X icons, sizes, and true/false colors.
---

`IconColumn` renders a [Heroicon](https://heroicons.com) instead of text. The column's state is treated as the icon name unless `.boolean()` is enabled, in which case a fixed check or X icon renders based on truthiness:

```python
from almasix.orbit.tables import IconColumn

IconColumn.make("status")
```

## Customizing the icon

By default, the icon name is the column's raw state, so a record with `"status": "heroicon-o-rocket-launch"` renders that icon directly. Use `.icon(...)` to override it with a static name or a callback:

```python
IconColumn.make("status").icon(
    lambda state=None, **_: {
        "info": "heroicon-o-information-circle",
        "warn": "heroicon-o-exclamation-triangle",
        "crit": "heroicon-o-fire",
    }.get(state, "heroicon-o-question-mark-circle"),
)
```

## Customizing the color

The icon's color can be set the same way as [`TextColumn.color()`](/tables/columns/text/#customizing-the-color) — a static color name, or a callback:

```python
IconColumn.make("severity").color(
    lambda state=None, **_: {"crit": "danger", "warn": "warning"}.get(state, "gray"),
)
```

## Customizing the size

Icons default to a medium size. Use `.size()` to choose a different size class:

```python
IconColumn.make("status").size("lg")
```

## Boolean icons

Pass `.boolean()` for read-only Yes/No fields — it swaps to a check icon when the state is truthy, and an X icon when it's falsy:

```python
IconColumn.make("verified").boolean()
```

Boolean icons default to `success` (check) and `danger` (X) if no color is set. `BooleanColumn` is a Filament-shaped shortcut for exactly this — see [Boolean column](/tables/columns/boolean/).

### Customizing the boolean icons

Use `.true_icon()` and `.false_icon()` to change which Heroicons render for each state:

```python
IconColumn.make("verified")
    .boolean()
    .true_icon("heroicon-o-check")
    .false_icon("heroicon-o-x-mark")
```

### Customizing the boolean colors

`.true_color()` and `.false_color()` override the default success/danger colors independently — each accepts a static color or a callback:

```python
IconColumn.make("verified")
    .boolean()
    .true_color("info")
    .false_color(lambda record=None, **_: "gray" if record.get("archived") else "danger")
```

If you also call `.color(...)` directly, it takes priority over `.true_color()` / `.false_color()`.

## Full example

```python
from almasix.orbit.tables import Table, TextColumn, IconColumn

Table.make("alerts").columns([
    TextColumn.make("title").searchable(),
    IconColumn.make("severity")
        .icon(lambda state=None, **_: {
            "info": "heroicon-o-information-circle",
            "warn": "heroicon-o-exclamation-triangle",
            "crit": "heroicon-o-fire",
        }.get(state, "heroicon-o-question-mark-circle"))
        .color(lambda state=None, **_: {
            "info": "info",
            "warn": "warning",
            "crit": "danger",
        }.get(state, "gray")),
    IconColumn.make("acked")
        .boolean()
        .true_icon("heroicon-o-check")
        .false_icon("heroicon-o-clock")
        .true_color("success")
        .false_color("warning")
        .align_center(),
]).records([
    {"id": 1, "title": "Disk usage high", "severity": "crit", "acked": False},
    {"id": 2, "title": "Deploy finished", "severity": "info", "acked": True},
])
```

For Yes/No **text** instead of icons, use [`TextColumn.boolean()`](/tables/columns/boolean/) instead.

## Key methods

| Method | Effect |
|--------|--------|
| `.icon(str \| callable)` | Icon name (non-boolean mode) |
| `.color(str \| callable)` | Icon color |
| `.size(value)` | Size class (`sm`, `md`, `lg`, …) |
| `.boolean()` | Check / X mode |
| `.true_icon(name)` / `.false_icon(name)` | Boolean icon glyphs |
| `.true_color(str \| callable)` / `.false_color(str \| callable)` | Boolean icon colors |
| `.format_state_using(callback)` | Map domain values → icon names before `.icon()` resolves |
| `.align_center()` / `.sortable()` | Inherited [shared helpers](/tables/columns/overview/) |

## Preview

![Icon colors and sizes (light)](/examples/light/tables/icon-colors.png)
![Icon colors and sizes (dark)](/examples/dark/tables/icon-colors.png)

![Icon / boolean (light)](/examples/light/tables/icon-boolean.png)
![Icon / boolean (dark)](/examples/dark/tables/icon-boolean.png)
