---
title: Column group
description: ColumnGroup — dual headers that group related columns under one label.
---

`ColumnGroup` draws a parent header across child columns. Use it when related fields should share one label, such as shipping address fields or payment totals.

Filament-shaped constructor: `ColumnGroup.make('Label', [cols])` (or `.make([cols]).label(...)`).

## Standalone example

```python
from almasix.orbit.tables import Table, TextColumn, ColumnGroup

table = (
    Table.make("orders")
    .columns([
        TextColumn.make("id").label("#").sortable(),
        ColumnGroup.make("Customer", [
            TextColumn.make("customer_name").searchable(),
            TextColumn.make("email").copyable(),
        ]),
        ColumnGroup.make("Totals", [
            TextColumn.make("amount").money("USD").align_end(),
            TextColumn.make("tax").money("USD", divide_by=100).align_end(),
        ]),
    ])
    .records(records)
)
```

Alternate shape:

```python
ColumnGroup.make([
    TextColumn.make("city"),
    TextColumn.make("country"),
]).label("Location")
```

## In a Resource example

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, TextColumn, ColumnGroup

class OrderResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            TextColumn.make("number").searchable().sortable(),
            ColumnGroup.make("Shipping", [
                TextColumn.make("ship_name"),
                TextColumn.make("ship_city"),
                TextColumn.make("ship_country"),
            ]),
            ColumnGroup.make("Payment", [
                TextColumn.make("amount").money("USD").align_end().sortable(),
                TextColumn.make("status").badge().color("success"),
            ]),
        ])
```

Child columns keep their own sort, search, and formatting helpers. The group only provides the dual header.

## Key methods

- `ColumnGroup.make(label, [columns])` — labeled constructor
- `ColumnGroup.make([columns]).label(...)` — alternate shape
- `.columns([...])` — set / replace children
- `.get_columns()` — inspect children
- Children: any `Column` (including money, badges, editable)

## Preview

![Column group (light)](/examples/light/tables/column-group.png)
![Column group (dark)](/examples/dark/tables/column-group.png)
