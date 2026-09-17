---
title: Grouping rows
description: Group table rows with Group.
---

```python
from almasix.orbit.tables import Table, TextColumn, Group

Table.make().columns([TextColumn.make("name")]).default_group(Group.make("status")).records([...])
```

See also [Summaries](/tables/summaries/).

