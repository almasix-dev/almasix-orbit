---
title: Toggle column
description: ToggleColumn — inline on/off switches that persist via update_column_state.
---

`ToggleColumn` renders an inline switch for boolean fields so operators can change the value without opening a form.

Like other editable columns, it uses `data-orbit-column-edit="toggle"` and persists through `ListRecordsHost.update_column_state` / `orbit.js`.

```python
SelectColumn, TextInputColumn, ToggleColumn, CheckboxColumn
# persist via ListRecordsHost.update_column_state / orbit.js
```

## Standalone example

```python
from almasix.orbit.tables import Table, TextColumn, ToggleColumn

table = (
    Table.make("flags")
    .columns([
        TextColumn.make("name").searchable(),
        ToggleColumn.make("enabled").label("On"),
        ToggleColumn.make("featured"),
    ])
    .records([
        {"id": 1, "name": "Dark mode", "enabled": True, "featured": False},
        {"id": 2, "name": "Beta banner", "enabled": False, "featured": True},
    ])
)
```

## In a Resource example

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, TextColumn, ToggleColumn

class FlagResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            TextColumn.make("name").searchable().sortable(),
            ToggleColumn.make("enabled").align_center(),
            ToggleColumn.make("public")
                .disabled(lambda record=None, **_: record.get("locked")),
        ])
```

Prefer [`BooleanColumn`](/tables/columns/boolean/) / [`IconColumn.boolean()`](/tables/columns/icon/) when the value is read-only. Use `ToggleColumn` when operators should change it from the index.

## Key methods

- `.disabled(bool | callable)` — prevent edits per row
- `.label(...)` / `.align_center()` / `.sortable()`
- Markup: `data-orbit-column-edit="toggle"`, `data-record-id`, `data-column`

## Preview

![Toggle column (light)](/examples/light/tables/editable.png)
![Toggle column (dark)](/examples/dark/tables/editable.png)
