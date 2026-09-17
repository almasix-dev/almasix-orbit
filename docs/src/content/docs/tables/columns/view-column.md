---
title: ViewColumn
description: Orbit ViewColumn — custom HTML cell content via .content().
---

Bring your own markup. Callable content receives `record` and `state`.

## Standalone

```python
from almasix.orbit.tables import Table, ViewColumn

table = (
    Table.make("demo")
    .columns([
        ViewColumn.make("preview").content(
            lambda record=None, state=None, **_: f'<span class="or-badge">{state}</span>'
        ),
    ])
    .records(records)
)
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, ViewColumn

class PostResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            ViewColumn.make("actions_hint")
                .content("<span class=\"or-muted\">Use row actions →</span>"),
        ])
```

## Key methods

- `.content(str | callable)`
- `Falls back to escaped state when content is unset`
- `.label(...)`

## Preview

![Orbit table example (light)](/examples/light/table.png)

![Orbit table example (dark)](/examples/dark/table.png)

