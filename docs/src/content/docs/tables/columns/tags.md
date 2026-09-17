---
title: Tags column
description: Orbit TagsColumn — list or comma-split values as badge chips.
---

Lists become badges; comma strings get split. Keyword soup, but polite.

## Standalone

```python
from almasix.orbit.tables import Table, TagsColumn

table = (
    Table.make("demo")
    .columns([
        TagsColumn.make("tags"),
    ])
    .records(records)
)
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, TagsColumn

class PostResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            TagsColumn.make("labels"),
            TagsColumn.make("tags").format_state_using(lambda v: v or []),
        ])
```

## Key methods

- `Accepts list/tuple or comma-separated string`
- `.format_state_using(...)`
- `.label(...) / .sortable() (sorts on raw state)`

## Preview

![Orbit table example (light)](/examples/light/table.png)

![Orbit table example (dark)](/examples/dark/table.png)

