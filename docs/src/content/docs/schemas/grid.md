---
title: Grid
description: Grid lays out child components in a fixed column count — pair with TextInput pairs, metric tiles, or mixed fields.
---

## Introduction

Grid lays out child components in a fixed column count — pair with TextInput pairs, metric tiles, or mixed fields.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic grid

![Orbit Basic grid (light)](/examples/light/schemas/grid/basic.png)

![Orbit Basic grid (dark)](/examples/dark/schemas/grid/basic.png)

Two-column field grid.

```python
Grid.make()
    .columns(2)
    .schema([TextInput.make('col_a'), TextInput.make('col_b')])
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
