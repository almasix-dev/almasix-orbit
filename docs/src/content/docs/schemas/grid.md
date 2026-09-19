---
title: Grid
description: Lay out schema children in a fixed column count — pair with field pairs, metric tiles, or mixed controls.
---

## Introduction

`Grid` places child components in a CSS grid with a fixed column count. Use it for two-up field pairs, metric tiles, or any mixed controls that should align in columns. Nest grids inside [sections](/schemas/sections/) or at the top of a [schema](/schemas/overview/).

```python title="app/orbit/schemas/grid_basic.py"
from almasix.orbit.schemas import Grid
from almasix.orbit.forms import TextInput

Grid.make()
    .columns(2)
    .schema([
        TextInput.make("col_a"),
        TextInput.make("col_b"),
    ])
```

![Basic grid (light)](/examples/light/schemas/grid/basic.png)
![Basic grid (dark)](/examples/dark/schemas/grid/basic.png)

## Columns

`.columns(n)` sets the track count. The default is `2` when you don’t call it:

```python title="app/orbit/schemas/grid_columns.py"
Grid.make().columns(1).schema([...])  # single column stack
Grid.make().columns(3).schema([...])  # three-up metrics / fields
```

Rendered chrome uses `or-grid or-grid-cols-N`.

## Grid container

`.grid_container()` adds `or-grid-container` when the grid should establish its own containing block for nested column spans:

```python title="app/orbit/schemas/grid_container.py"
Grid.make()
    .columns(3)
    .grid_container()
    .schema([...])
```

## Dense and gap

Shared layout helpers tighten or remove gutters — same API as [Flex](/schemas/flex/) and other layouts:

```python title="app/orbit/schemas/grid_dense.py"
Grid.make().columns(2).dense().gap(False).schema([...])
Grid.make().columns(2).gap("sm").schema([...])
```

Also available: `.defer_loading()` for async chrome — see [Layouts](/schemas/layouts/) and [Schemas overview](/schemas/overview/).

## Composition tip

Pair a grid with a section when you want a titled block of columns:

```python title="app/orbit/schemas/grid_in_section.py"
from almasix.orbit.schemas import Section, Grid
from almasix.orbit.forms import TextInput, Select

Section.make("contact").heading("Contact").schema([
    Grid.make().columns(2).schema([
        TextInput.make("email"),
        Select.make("preferred").options({"email": "Email", "phone": "Phone"}),
    ]),
])
```

![Grid + flex gallery (light)](/examples/light/schemas/grid-flex.png)
![Grid + flex gallery (dark)](/examples/dark/schemas/grid-flex.png)

## API reference

| Method | Role |
|--------|------|
| `.columns` | Number of columns |
| `.grid_container` | Add container chrome class |
| `.schema` | Child components |
| `.dense` / `.gap` / `.defer_loading` | Shared layout helpers |
