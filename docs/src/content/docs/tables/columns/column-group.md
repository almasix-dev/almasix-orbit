---
title: Column group
description: ColumnGroup — a shared header above related columns, with its own alignment and header wrapping.
---

`ColumnGroup` draws one header above a set of child columns — use it when related fields should share a label, like shipping address fields or payment totals:

```python
from almasix.orbit.tables import ColumnGroup, TextColumn

ColumnGroup.make("Customer", [
    TextColumn.make("customer_name").searchable(),
    TextColumn.make("email").copyable(),
])
```

The constructor mirrors Filament's shape — `ColumnGroup.make('Label', [columns])`. An alternate shape is also available when you'd rather set the label afterwards:

```python
ColumnGroup.make([
    TextColumn.make("city"),
    TextColumn.make("country"),
]).label("Location")
```

Child columns keep every helper they'd normally have — sorting, searching, money, badges, and editable inputs all still work exactly as if the column weren't grouped. The group only adds a second header row above them.

## Customizing the group header alignment

The group's header can be aligned independently of its children:

```python
ColumnGroup.make("Totals", [...]).align_end()
```

## Wrapping the group header

If the group's label is long, allow it to wrap instead of clipping:

```python
ColumnGroup.make("Shipping details", [...]).wrap_header()
```

## Full example

```python
from almasix.orbit.tables import Table, TextColumn, ColumnGroup

Table.make("orders").columns([
    TextColumn.make("number").label("#").sortable(),
    ColumnGroup.make("Customer", [
        TextColumn.make("customer_name").searchable(),
        TextColumn.make("email").copyable(),
    ]),
    ColumnGroup.make("Totals", [
        TextColumn.make("amount").money("USD").align_end().sortable(),
        TextColumn.make("status").badge().color("success"),
    ]).align_end(),
]).records([
    {
        "id": 1,
        "number": "#1042",
        "customer_name": "Ada Lovelace",
        "email": "ada@example.com",
        "amount": 4899,
        "status": "paid",
    },
    {
        "id": 2,
        "number": "#1043",
        "customer_name": "Grace Hopper",
        "email": "grace@example.com",
        "amount": 1200,
        "status": "due",
    },
])
```

## Key methods

| Method | Effect |
|--------|--------|
| `ColumnGroup.make(label, [columns])` | Labeled constructor |
| `ColumnGroup.make([columns]).label(...)` | Alternate shape |
| `.columns([...])` / `.get_columns()` | Set / inspect children |
| `.align_start()` / `.align_center()` / `.align_end()` | Group header alignment |
| `.wrap_header()` | Allow the group label to wrap |
| Children | Any [`Column`](/tables/columns/overview/) — including money, badges, and editable columns |

## Preview

![Column group (light)](/examples/light/tables/column-group.png)
![Column group (dark)](/examples/dark/tables/column-group.png)
