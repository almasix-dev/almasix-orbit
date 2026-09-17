---
title: ColorColumn
description: Orbit ColorColumn — hex color swatches in table cells.
---

Shows a little swatch with the hex as the title tooltip. Brand colors love this.

## Standalone

```python
from almasix.orbit.tables import Table, ColorColumn

table = (
    Table.make("demo")
    .columns([
        ColorColumn.make("brand"),
    ])
    .records(records)
)
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, ColorColumn

class PostResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            ColorColumn.make("accent").label("Accent"),
            ColorColumn.make("color"),
        ])
```

## Key methods

- `Defaults missing state to `#000000``
- `.format_state_using(...) if you store names not hex`
- `.label(...)`

## Preview

![Orbit table example (light)](/examples/light/table.png)

![Orbit table example (dark)](/examples/dark/table.png)

