---
title: Layout
description: Split, Stack, and Panel layouts inside table cells.
---

```python
from almasix.orbit.tables import Table, TextColumn, Split, Stack

Table.make().columns([
    Split.make([
        Stack.make([TextColumn.make("name"), TextColumn.make("email")]),
        TextColumn.make("status"),
    ])
])
```

