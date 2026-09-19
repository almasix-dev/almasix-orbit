---
title: Select column
description: SelectColumn — inline dropdown editors with option control and update_column_state persistence.
---

`SelectColumn` puts an inline `<select>` in the cell so operators can change a value without opening the record's edit form:

```python
from almasix.orbit.tables import SelectColumn

SelectColumn.make("status").options({
    "draft": "Draft",
    "review": "Review",
    "published": "Published",
})
```

`SelectColumn` is one of Orbit's editable columns, alongside [`ToggleColumn`](/tables/columns/toggle/), [`TextInputColumn`](/tables/columns/text-input/), and [`CheckboxColumn`](/tables/columns/checkbox/). All four render `data-orbit-column-edit="…"` on the input, and `orbit.js` calls `ListRecordsHost.update_column_state(record_id, column, value)` to persist the change once an operator interacts with it.

## Setting the options

Pass a value → label dict, or a callback that returns one — useful when the choices depend on the row:

```python
SelectColumn.make("status").options(
    lambda record=None, **_: {"draft": "Draft", "review": "Review"}
    if record.get("locked")
    else {"draft": "Draft", "review": "Review", "published": "Published"},
)
```

## Disabling the placeholder option

By default a blank placeholder option is selectable, so operators can clear the value. Disable it with `.selectable_placeholder(False)` when a value is always required:

```python
SelectColumn.make("status").options({...}).selectable_placeholder(False)
```

## Disabling individual options

`.disable_option_when()` disables specific `<option>` entries instead of the whole column — the callback receives `value`, `label`, and `record`:

```python
SelectColumn.make("status")
    .options({"draft": "Draft", "review": "Review", "published": "Published"})
    .disable_option_when(
        lambda value=None, record=None, **_: value == "published" and record.get("locked"),
    )
```

## Disabling the column

Lock the whole cell for specific rows with `.disabled()`:

```python
SelectColumn.make("status").options({...}).disabled(
    lambda record=None, **_: record.get("locked"),
)
```

## Reacting to updates

Run code before and/or after a value is persisted using `.before_state_updated()` / `.after_state_updated()` — both receive `(record, state, old)`:

```python
SelectColumn.make("status").options({...}).after_state_updated(
    lambda record=None, state=None, old=None, **_: notify_status_change(record, old, state),
)
```

## How persistence works

Rendered markup includes the hooks Orbit needs to wire up the edit:

```html
<select class="or-select or-select-inline"
        data-orbit-column-edit="select"
        data-record-id="1"
        data-column="status">
  …
</select>
```

On a resource's `ListRecordsHost`, `update_column_state` writes the new value onto the in-memory record (and runs any `before_state_updated` / `after_state_updated` hooks you registered) — override it if you need to persist elsewhere.

## Full example

```python
from almasix.orbit.tables import Table, TextColumn, SelectColumn

Table.make("posts").columns([
    TextColumn.make("title").searchable().sortable(),
    SelectColumn.make("status")
        .label("Status")
        .options({"draft": "Draft", "review": "Review", "published": "Published"})
        .selectable_placeholder(False),
]).records([
    {"id": 1, "title": "Launch Orbit", "status": "draft"},
    {"id": 2, "title": "Conduit hosts", "status": "published"},
])
```

## Key methods

| Method | Effect |
|--------|--------|
| `.options(dict \| callable)` | Value → label map |
| `.selectable_placeholder(bool)` | Allow / block the blank option |
| `.disable_option_when(callback)` | Disable individual `<option>` entries |
| `.disabled(bool \| callable)` | Lock the whole cell for a row |
| `.before_state_updated(callback)` / `.after_state_updated(callback)` | Hooks around persistence |
| `.label(...)` / `.sortable()` / `.align_start()` | Inherited [shared helpers](/tables/columns/overview/) |
| Markup | `data-orbit-column-edit="select"`, `data-record-id`, `data-column` |

## Preview

![Select column (light)](/examples/light/tables/select-column.png)
![Select column (dark)](/examples/dark/tables/select-column.png)

![Editable columns (light)](/examples/light/tables/editable.png)
![Editable columns (dark)](/examples/dark/tables/editable.png)
