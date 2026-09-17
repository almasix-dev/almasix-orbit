---
title: Grouping rows
description: Group table rows with default_group, collapsible headers, and Group buckets.
---

Grouping partitions the list into buckets by a field such as status, author, or date. Related rows appear under a shared header.

```python
from almasix.orbit.tables import Table, TextColumn, Group

table = (
    Table.make("posts")
    .columns([
        TextColumn.make("title").searchable(),
        TextColumn.make("status").badge(),
        TextColumn.make("amount").money("USD").align_end(),
    ])
    .default_group(
        Group.make("status").label("Status").collapsible()
    )
    .collapsed_groups_by_default(False)
    .records(records)
)
```

Orbit renders an `or-group-header` row per bucket and marks members with `or-group-member`. Click a collapsible header to hide or show its rows (client-side in `orbit.js`).

![Grouped rows (light)](/examples/light/tables/grouping.png)
![Grouped rows (dark)](/examples/dark/tables/grouping.png)

## Standalone example

```python
from almasix.orbit.tables import Table, TextColumn, Group, Sum

records = [
    {"id": 1, "title": "Launch", "status": "published", "amount": 1200},
    {"id": 2, "title": "Draft notes", "status": "draft", "amount": 120},
    {"id": 3, "title": "Polish", "status": "published", "amount": 450},
]

group = Group.make("status").label("Status").collapsible()

table = (
    Table.make("posts")
    .columns([
        TextColumn.make("title"),
        TextColumn.make("amount").money("USD").align_end().summarize(
            Sum.make().money("USD"),
        ),
    ])
    .default_group(group)
    .records(records)
)

# Inspect buckets without rendering:
buckets = group.group_records(records)
for bucket in buckets:
    print(bucket.title, len(bucket.records))
```

Pass a string shorthand when the attribute name is enough:

```python
table.default_group("status")  # → Group.make("status")
```

## In a Resource example

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, TextColumn, Group, Sum

class PostResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.columns([
                TextColumn.make("title").searchable().sortable(),
                TextColumn.make("status").badge(),
                TextColumn.make("amount")
                    .money("USD")
                    .align_end()
                    .summarize(Sum.make().money("USD")),
            ])
            .default_group(
                Group.make("status")
                    .label("Status")
                    .collapsible()
                    .get_title_from_record_using(
                        lambda record=None, **_: str(record.get("status", "")).title()
                    )
            )
            .collapsed_groups_by_default(False)
        )
```

Demo: **Columns → Grouped rows** in `examples/orbit-admin`.

## Key methods

On `Group`:

- `.label(...)` — prefix on header titles
- `.collapsible()` — clickable expand/collapse
- `.date()` — treat keys as dates
- `.direction("asc" | "desc")` — bucket order
- `.get_title_from_record_using(fn)` / `.get_description_from_record_using(fn)`
- `.get_key_from_record_using(fn)` — custom partition key
- `.title_prefixed_with_label(bool)`

On `Table`:

- `.default_group(Group | str | None)`
- `.groups([...])` / `.groups_only()` — multi-group / headers-only modes
- `.collapsed_groups_by_default(bool)`

Pair with [summaries](/tables/summaries/) for per-group totals.
