---
title: Repeater
description: Repeater repeats a nested schema for line items, addresses, or JSON arrays.
---

## Introduction

Repeater repeats a nested schema for line items, addresses, or JSON arrays. Clone, reorder, collapse, and table layouts mirror Filament repeaters.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic repeater

Simple stacked items with add/remove.

```python
Repeater.make('items')
    .label('Line items')
    .schema([TextInput.make('name').label('Name')])
    .default_items(1)
```

![Orbit Basic repeater (light)](/examples/light/forms/repeater/basic.png)

![Orbit Basic repeater (dark)](/examples/dark/forms/repeater/basic.png)

## Cloneable and reorderable

Duplicate rows and move up/down.

```python
Repeater.make('items')
    .cloneable()
    .reorderable()
    .collapsible()
    .schema([...])
```

![Orbit Cloneable and reorderable (light)](/examples/light/forms/repeater/cloneable-reorderable.png)

![Orbit Cloneable and reorderable (dark)](/examples/dark/forms/repeater/cloneable-reorderable.png)

## Table layout

Column headers for spreadsheet-like entry.

```python
Repeater.make('items')
    .table(['Name', 'Qty'])
    .schema([TextInput.make('name'), TextInput.make('qty')])
```

![Orbit Table layout (light)](/examples/light/forms/repeater/table.png)

![Orbit Table layout (dark)](/examples/dark/forms/repeater/table.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
