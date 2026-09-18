---
title: Group
description: Group fuses fields without fieldset chrome — Filament-style inline grouping with optional column grid.
---

## Introduction

Group fuses fields without fieldset chrome — Filament-style inline grouping with optional column grid.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic group

![Orbit Basic group (light)](/examples/light/schemas/group/basic.png)

![Orbit Basic group (dark)](/examples/dark/schemas/group/basic.png)

SKU and quantity on one row.

```python
Group.make()
    .columns(2)
    .schema([TextInput.make('sku'), TextInput.make('qty')])
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
