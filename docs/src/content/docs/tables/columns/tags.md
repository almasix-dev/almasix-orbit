---
title: Tags column
description: TagsColumn — turn a list (or CSV string) into a cluster of badges.
---

`TagsColumn` takes an iterable of labels (or a comma-separated string) and renders them as `or-badge` chips. Use it for categories, skills, and other multi-value labels.

## Standalone example

```python
from almasix.orbit.tables import Table, TextColumn, TagsColumn

table = (
    Table.make("articles")
    .columns([
        TextColumn.make("title").searchable().sortable(),
        TagsColumn.make("tags"),
        TagsColumn.make("topics"),  # also accepts "a, b, c" strings
    ])
    .records([
        {"id": 1, "title": "Orbit tables", "tags": ["docs", "ui"], "topics": "python, html"},
        {"id": 2, "title": "Conduit hosts", "tags": ["live"], "topics": "conduit"},
    ])
)
```

## In a Resource example

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, TagsColumn, TextColumn

class ArticleResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            TextColumn.make("title").searchable().sortable().weight("bold"),
            TagsColumn.make("tags").label("Tags"),
            TextColumn.make("published_at").date("%b %d, %Y"),
        ])
```

Empty lists render an empty cell. Pair with a [TagsInput](/forms/tags-input/) on the form so create and edit stay in sync with the list.

## Key methods

- `.label(...)` / `.align_start()` / `.toggleable(...)`
- `.format_state_using(callback)` — normalize dicts / objects → strings
- `.sortable()` — sorts on the raw state (list/string)

## Preview

![Tags column (light)](/examples/light/tables/tags-view.png)
![Tags column (dark)](/examples/dark/tables/tags-view.png)
