---
title: Color column
description: ColorColumn — hex swatches in the grid, optionally one-click copyable.
---

`ColorColumn` renders a color swatch from a hex value (or any CSS color string). Use it for brand colors, tag colors, and similar fields.

## Standalone example

```python
from almasix.orbit.tables import Table, TextColumn, ColorColumn

table = (
    Table.make("brands")
    .columns([
        TextColumn.make("name").searchable(),
        ColorColumn.make("hex").copyable().label("Swatch"),
        TextColumn.make("hex").copyable().label("Value"),
    ])
    .records([
        {"id": 1, "name": "Orbit Blue", "hex": "#2563eb"},
        {"id": 2, "name": "Conduit Ink", "hex": "#0f172a"},
    ])
)
```

`.copyable()` adds a clipboard control so operators can copy the hex value.

## In a Resource example

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, ColorColumn, TextColumn

class TagResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            ColorColumn.make("color").copyable().align_center(),
            TextColumn.make("name").searchable().sortable(),
            TextColumn.make("slug").copyable(),
        ])
```

Empty or missing state falls back to `#000000` so the cell still renders a swatch.

## Key methods

- `.copyable()` — clipboard button on the swatch
- `.label(...)` / `.align_center()` / `.toggleable(...)`
- `.format_state_using(callback)` — normalize `#rgb` → `#rrggbb` if needed

## Preview

![Color column (light)](/examples/light/tables/image-color.png)
![Color column (dark)](/examples/dark/tables/image-color.png)
