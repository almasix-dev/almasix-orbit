---
title: Text input column
description: TextInputColumn — inline text fields with input type, step, prefix/suffix, and update hooks.
---

`TextInputColumn` renders an `<input>` in the cell so operators can edit short values — SKUs, nicknames, quantities — without leaving the index:

```python
from almasix.orbit.tables import TextInputColumn

TextInputColumn.make("sku")
```

It's an editable column like [`SelectColumn`](/tables/columns/select/), [`ToggleColumn`](/tables/columns/toggle/), and [`CheckboxColumn`](/tables/columns/checkbox/): it renders `data-orbit-column-edit="text"`, and changes persist through `ListRecordsHost.update_column_state`.

## Changing the input's type

The input defaults to `type="text"`. Switch to any HTML input type — commonly `number` or `email`:

```python
TextInputColumn.make("quantity").type("number")
```

### Setting the input mode

Pair a numeric type with `.input_mode()` to hint the correct mobile keyboard:

```python
TextInputColumn.make("quantity").type("number").input_mode("decimal")
```

### Setting a step

For numeric inputs, `.step()` controls the increment used by the browser's up/down controls:

```python
TextInputColumn.make("quantity").type("number").step("0.01")
```

## Adding affix text

Prefix and/or suffix text render alongside the input without becoming part of its value — pass a string or a callback:

```python
TextInputColumn.make("amount")
    .type("number")
    .prefix("$")
    .suffix(lambda record=None, **_: record.get("currency", "USD"))
```

## Disabling the column

Lock specific rows from editing with `.disabled()`:

```python
TextInputColumn.make("sku").disabled(
    lambda record=None, **_: record.get("locked"),
)
```

## Reacting to updates

`.before_state_updated()` / `.after_state_updated()` fire around persistence, each receiving `(record, state, old)`:

```python
TextInputColumn.make("sku").after_state_updated(
    lambda record=None, state=None, old=None, **_: reindex_sku(record, state),
)
```

For long-form content, use a form field instead of an inline input.

## Full example

```python
from almasix.orbit.tables import Table, TextColumn, TextInputColumn

Table.make("skus").columns([
    TextColumn.make("product").searchable(),
    TextInputColumn.make("sku").label("SKU"),
    TextInputColumn.make("price")
        .label("Price")
        .type("number")
        .input_mode("decimal")
        .step("0.01")
        .prefix("$"),
]).records([
    {"id": 1, "product": "Widget", "sku": "ORB-1", "price": "19.99"},
    {"id": 2, "product": "Gadget", "sku": "ORB-2", "price": "42.00"},
])
```

## Key methods

| Method | Effect |
|--------|--------|
| `.type(value)` | HTML input `type` attribute |
| `.input_mode(value)` | Mobile keyboard hint |
| `.step(value)` | Numeric increment |
| `.prefix(str \| callable)` / `.suffix(str \| callable)` | Affix text |
| `.disabled(bool \| callable)` | Lock rows that should not change |
| `.before_state_updated(callback)` / `.after_state_updated(callback)` | Hooks around persistence |
| `.label(...)` / `.align_end()` / `.sortable()` | Inherited [shared helpers](/tables/columns/overview/) |
| Markup | `data-orbit-column-edit="text"`, `data-record-id`, `data-column`; class `or-input or-input-inline` |

## Preview

![Text input column (light)](/examples/light/tables/text-input-column.png)
![Text input column (dark)](/examples/dark/tables/text-input-column.png)

![Editable columns (light)](/examples/light/tables/editable.png)
![Editable columns (dark)](/examples/dark/tables/editable.png)
