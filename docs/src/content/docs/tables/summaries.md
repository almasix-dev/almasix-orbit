---
title: Table summaries, grouping & layout
description: Sum/Average/Count/Range summarizers, row groups, and Split/Stack/Panel cell layouts.
---

## Summaries

```python
from almasix.orbit.tables import Table, TextColumn, Sum, Average, Count

table = Table.make().columns([
    TextColumn.make("amount").money("USD").summarize(
        Sum.make().attribute("amount").label("Total"),
        Average.make().attribute("amount"),
    ),
    TextColumn.make("id").summarize(Count.make()),
])
```

## Grouping

```python
from almasix.orbit.tables import Group

group = Group.make("status").label("Status").collapsible()
buckets = group.group_records(records)
```

## Layout components

Use `Split`, `Stack`, and `Panel` when composing rich cell layouts (card-like rows). Wire them into custom `ViewColumn` content or host table layouts.

## Preview

![Table (light)](/examples/light/tables/overview.png)

![Table (dark)](/examples/dark/tables/overview.png)
