---
title: View column
description: ViewColumn — custom HTML for cells that do not fit a stock column type.
---

When no stock column fits, `ViewColumn` lets you inject HTML (or a callable that returns it). Escape untrusted content.

This is distinct from layout [`View`](/tables/layout/) — `ViewColumn` is a **column type**; layout `View` wraps child columns inside one cell.

## Standalone example

```python
from almasix.orbit.tables import Table, TextColumn, ViewColumn
from almasix.orbit.support.html import e

table = (
    Table.make("customers")
    .columns([
        TextColumn.make("company").searchable(),
        ViewColumn.make("contact").content(
            lambda record=None, state=None, **_: (
                f'<div class="or-view-column">'
                f'<strong>{e(record.get("name", ""))}</strong><br />'
                f'<a href="mailto:{e(record.get("email", ""))}">'
                f'{e(record.get("email", ""))}</a></div>'
            )
        ),
    ])
    .records(records)
)
```

## In a Resource example

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, TextColumn, ViewColumn
from almasix.orbit.support.html import e

class CustomerResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            TextColumn.make("company").searchable().sortable(),
            ViewColumn.make("progress").label("Progress").content(
                lambda state=None, **_: (
                    f'<div class="or-progress" role="progressbar" '
                    f'aria-valuenow="{int(state or 0)}" aria-valuemin="0" '
                    f'aria-valuemax="100">'
                    f'<span style="width:{int(state or 0)}%"></span></div>'
                )
            ),
            ViewColumn.make("raw").content("<em>static HTML is fine too</em>"),
        ])
```

`.content(...)` accepts a string or a callable with `record` / `state`. The result is inserted inside `.or-view-column`. Add your own CSS classes as needed.

## Key methods

- `.content(str | callable)` — HTML body for the cell
- `.label(...)` / `.toggleable(...)` / `.align_start()`
- Callable kwargs commonly include `record`, `state`

## Preview

![View column (light)](/examples/light/tables/tags-view.png)
![View column (dark)](/examples/dark/tables/tags-view.png)
