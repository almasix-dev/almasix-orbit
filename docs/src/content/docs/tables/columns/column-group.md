---
title: ColumnGroup
description: Orbit ColumnGroup — nest columns under a named group.
---

Group related columns for organization. Call `.columns([...])` with child Column instances.

## Standalone

```python
from almasix.orbit.tables import Table, ColumnGroup, TextColumn, BooleanColumn

table = (
    Table.make("demo")
    .columns([
        ColumnGroup.make("identity").label("Identity").columns([
            TextColumn.make("title").searchable(),
            TextColumn.make("slug"),
        ]),
    ])
    .records(records)
)
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, ColumnGroup, TextColumn, BooleanColumn

class PostResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            ColumnGroup.make("meta").columns([
                TextColumn.make("status").badge(),
                BooleanColumn.make("featured"),
            ]),
        ])
```

## Key methods

- `.columns([...]) — list of Column instances`
- `.get_columns()`
- `.label(...) for the group name`


Import child columns you nest — `ColumnGroup` alone doesn’t render cell HTML.


## Preview

```html
<!-- Grouping is structural; children still render as <td class="or-td">…</td> -->
<th class="or-th" colspan="2">Identity</th>
```
