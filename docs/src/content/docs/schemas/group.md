---
title: Group
description: Group fuses fields without fieldset chrome — Filament-style inline grouping with optional column grid.
---

## Introduction

Group fuses fields without fieldset chrome — Filament-style inline grouping with optional column grid.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic group

SKU and quantity on one row.

```python
Group.make()
    .columns(2)
    .schema([TextInput.make('sku'), TextInput.make('qty')])
```

![Orbit Basic group (light)](/examples/light/schemas/group/basic.png)

![Orbit Basic group (dark)](/examples/dark/schemas/group/basic.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
