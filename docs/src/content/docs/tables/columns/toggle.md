---
title: Toggle column
description: ToggleColumn — inline on/off switches with before/after update hooks, persisted via update_column_state.
---

`ToggleColumn` renders an inline switch for boolean fields, so operators can flip a value straight from the index without opening the edit form:

```python
from almasix.orbit.tables import ToggleColumn

ToggleColumn.make("enabled")
```

Like [`SelectColumn`](/tables/columns/select/), [`TextInputColumn`](/tables/columns/text-input/), and [`CheckboxColumn`](/tables/columns/checkbox/), it's an editable column: it renders `data-orbit-column-edit="toggle"`, and `orbit.js` persists changes through `ListRecordsHost.update_column_state`.

## Disabling the column

Prevent specific rows from being changed with `.disabled()`:

```python
ToggleColumn.make("public").disabled(
    lambda record=None, **_: record.get("locked"),
)
```

## Reacting to updates

`.before_state_updated()` and `.after_state_updated()` run around the persisted change — each receives `(record, state, old)`:

```python
ToggleColumn.make("featured").after_state_updated(
    lambda record=None, state=None, old=None, **_: log_feature_toggle(record, state),
)
```

## Choosing icons vs. text vs. toggles

Toggles are for values operators should be able to *change* from the index. If the value is read-only, prefer [`BooleanColumn`](/tables/columns/boolean/) or [`IconColumn.boolean()`](/tables/columns/icon/#boolean-icons) instead — they render check/X icons without implying the cell is interactive.

## Full example

```python
from almasix.orbit.tables import Table, TextColumn, ToggleColumn

Table.make("flags").columns([
    TextColumn.make("name").searchable(),
    ToggleColumn.make("enabled").label("On").align_center(),
    ToggleColumn.make("public")
        .align_center()
        .disabled(lambda record=None, **_: record.get("locked")),
]).records([
    {"id": 1, "name": "Dark mode", "enabled": True, "public": True, "locked": False},
    {"id": 2, "name": "Beta banner", "enabled": False, "public": False, "locked": True},
])
```

## Key methods

| Method | Effect |
|--------|--------|
| `.disabled(bool \| callable)` | Prevent edits for a row |
| `.before_state_updated(callback)` / `.after_state_updated(callback)` | Hooks around persistence |
| `.label(...)` / `.align_center()` / `.sortable()` | Inherited [shared helpers](/tables/columns/overview/) |
| Markup | `data-orbit-column-edit="toggle"`, `data-record-id`, `data-column` |

## Preview

![Toggle column (light)](/examples/light/tables/toggle-column.png)
![Toggle column (dark)](/examples/dark/tables/toggle-column.png)

![Editable columns (light)](/examples/light/tables/editable.png)
![Editable columns (dark)](/examples/dark/tables/editable.png)
