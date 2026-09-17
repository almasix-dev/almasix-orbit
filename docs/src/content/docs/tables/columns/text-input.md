---
title: Text input column
description: TextInputColumn — inline text fields for quick edits without opening a form.
---

`TextInputColumn` renders an `<input>` in the cell for short editable values such as SKUs or nicknames.

It persists like other editable columns via `data-orbit-column-edit="text"` → `ListRecordsHost.update_column_state` / `orbit.js`.

```python
SelectColumn, TextInputColumn, ToggleColumn, CheckboxColumn
# persist via ListRecordsHost.update_column_state / orbit.js
```

## Standalone example

```python
from almasix.orbit.tables import Table, TextColumn, TextInputColumn

table = (
    Table.make("skus")
    .columns([
        TextColumn.make("product").searchable(),
        TextInputColumn.make("sku").label("SKU"),
        TextInputColumn.make("qty").align_end(),
    ])
    .records(records)
)
```

## In a Resource example

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, TextColumn, TextInputColumn

class ProductResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            TextColumn.make("name").searchable().sortable(),
            TextInputColumn.make("sku")
                .label("SKU")
                .disabled(lambda record=None, **_: record.get("locked")),
            TextInputColumn.make("nickname"),
        ])
```

For long-form content, use a form field instead of an inline input.

## Key methods

- `.disabled(bool | callable)` — lock rows that should not change
- `.label(...)` / `.align_end()` / `.sortable()`
- Markup: `data-orbit-column-edit="text"`, `data-record-id`, `data-column`
- Class: `or-input or-input-inline`

## Preview

![Text input column (light)](/examples/light/tables/editable.png)
![Text input column (dark)](/examples/dark/tables/editable.png)
