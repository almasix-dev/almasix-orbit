---
title: Checkbox column
description: CheckboxColumn — inline checkboxes with update hooks, persisted via update_column_state.
---

`CheckboxColumn` renders an inline checkbox for boolean fields, using the same editable-column pipeline as select, toggle, and text input:

```python
from almasix.orbit.tables import CheckboxColumn

CheckboxColumn.make("approved")
```

Use [`ToggleColumn`](/tables/columns/toggle/) when a switch fits your UI better. Reach for `CheckboxColumn` for standard checkbox semantics — approval flags, permissions, bulk-style booleans.

## Disabling the column

Prevent specific rows from being edited with `.disabled()`:

```python
CheckboxColumn.make("featured").disabled(
    lambda record=None, **_: not record.get("approved"),
)
```

## Reacting to updates

`.before_state_updated()` / `.after_state_updated()` run around the persisted change, each receiving `(record, state, old)`:

```python
CheckboxColumn.make("approved").after_state_updated(
    lambda record=None, state=None, old=None, **_: notify_review(record, state),
)
```

For read-only booleans, use [`BooleanColumn`](/tables/columns/boolean/) or [`TextColumn.boolean()`](/tables/columns/boolean/) instead — reserve `CheckboxColumn` for values operators should change from the index.

## Full example

```python
from almasix.orbit.tables import Table, TextColumn, CheckboxColumn

Table.make("reviews").columns([
    TextColumn.make("title").searchable(),
    CheckboxColumn.make("approved").label("OK").align_center(),
    CheckboxColumn.make("featured")
        .align_center()
        .disabled(lambda record=None, **_: not record.get("approved")),
]).records([
    {"id": 1, "title": "Great write-up", "approved": True, "featured": False},
    {"id": 2, "title": "Needs edits", "approved": False, "featured": False},
])
```

## Key methods

| Method | Effect |
|--------|--------|
| `.disabled(bool \| callable)` | Prevent changes for a row |
| `.before_state_updated(callback)` / `.after_state_updated(callback)` | Hooks around persistence |
| `.label(...)` / `.align_center()` / `.sortable()` | Inherited [shared helpers](/tables/columns/overview/) |
| Markup | `data-orbit-column-edit="checkbox"`, `data-record-id`, `data-column`; class `or-checkbox` |

## Preview

![Checkbox column (light)](/examples/light/tables/checkbox-column.png)
![Checkbox column (dark)](/examples/dark/tables/checkbox-column.png)

![Editable columns (light)](/examples/light/tables/editable.png)
![Editable columns (dark)](/examples/dark/tables/editable.png)
