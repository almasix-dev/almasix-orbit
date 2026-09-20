---
title: Edit action
description: EditAction preset — page or modal edit with fill, mutate, and notifications.
---

## Introduction

`EditAction` is the row / header preset for updating a record. Defaults: name `edit`, label **Edit**, pencil icon, primary color.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import EditAction
from almasix.orbit.forms import TextInput

EditAction.make()
    .modal()
    .modal_heading("Edit post")
    .form([TextInput.make("title").required()])
    .success_notification("Saved")
```

![Orbit EditAction (light)](/examples/light/actions/edit.png)

![Orbit EditAction (dark)](/examples/dark/actions/edit.png)

Point at a full page with `.url(...)` when you do not want a modal:

```python title="app/orbit/actions/edit_url.py"
from almasix.orbit.actions import EditAction

EditAction.make().url(lambda record, **_: f"/posts/{record['id']}/edit")
```

## Filling the form

When rendered with `record=`, field names hydrate from the record. Override with `.fill_form(...)`:

```python title="app/orbit/actions/edit_fill.py"
from almasix.orbit.actions import EditAction

EditAction.make()
    .modal()
    .form([...])
    .fill_form(lambda record, **_: {"title": record["title"].upper()})
```

## Lifecycle

```python title="app/orbit/actions/edit_lifecycle.py"
from almasix.orbit.actions import EditAction

EditAction.make()
    .mutate_data_using(lambda data, **_: {**data, "updated_by": user_id()})
    .mutate_record_data_using(lambda record, **_: record)
    .using(lambda record, data, **_: update_post(record, data))
    .after(lambda record, **_: bust_cache(record))
```

| Hook | Role |
|------|------|
| `.mutate_data_using` | Transform submitted `data` |
| `.mutate_record_data_using` | Touch / replace `record` before persist |
| `.using` / `.action` | Persist body |
| `.before` / `.after` | Gate and side effects |

## On a table

```python title="app/orbit/resources/post_resource.py"
table.actions([
    EditAction.make().modal().form(list(_FORM)),
])
```
