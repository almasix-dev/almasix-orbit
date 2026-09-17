---
title: ImageColumn
description: Orbit ImageColumn — avatar-style image cells from a URL state.
---

When the cell is a URL, you get a tidy `or-avatar` image. Empty state stays empty.

## Standalone

```python
from almasix.orbit.tables import Table, ImageColumn

table = (
    Table.make("demo")
    .columns([
        ImageColumn.make("avatar_url").label("Avatar"),
    ])
    .records(records)
)
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, ImageColumn

class PostResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            ImageColumn.make("cover"),
            ImageColumn.make("avatar_url").label(""),
        ])
```

## Key methods

- `Renders `<img class="or-avatar">` when state is truthy`
- `.format_state_using(...) to build CDN URLs`
- `.label(...)`

## Preview

```html
<td class="or-td"><img class="or-avatar" src="/media/ada.png" alt="" /></td>
```
