---
title: Actions
description: Buttons, modals, confirmations, and CRUD presets for Orbit tables and forms.
---

**Actions** are the verbs in your admin UI — save, delete, “archive selected”, anything that should feel like a button with a story.

```python
from almasix.orbit.actions import Action
from almasix.orbit.forms import TextInput

save = (
    Action.make("save")
    .label("Save changes")
    .color("primary")
    .icon("heroicon-o-check")
    .requires_confirmation()
    .modal_heading("Save post?")
    .modal_description("This will publish the current draft.")
    .form([TextInput.make("note").label("Changelog note")])
    .authorize(lambda user: user is not None)
    .success_notification("Saved")
    .action(lambda **ctx: do_save(**ctx))
)

html = save.render(state={})
```

Rendered buttons speak Conduit: `wire:click="mountAction('save')"` plus `data-confirm` when confirmation is required.

## Fluent surface

| Method | Role |
|--------|------|
| `.label` / `.color` / `.icon` | Chrome |
| `.requires_confirmation()` | Confirm before run |
| `.modal_heading` / `.modal_description` | Modal copy |
| `.form([...])` | Fields collected before the action runs |
| `.url(str \| Callable)` | Link-style action |
| `.authorize(bool \| Callable)` | Gate with `.can(**ctx)` |
| `.success_notification(...)` | Toast after success |
| `.action(callback)` | What runs on `.call(...)` |

Colors map to `or-btn-{color}` classes (`primary`, `danger`, `gray`, …).

## Presets

| Class | Defaults |
|-------|----------|
| `CreateAction` | name `create`, plus icon, primary |
| `EditAction` | `edit`, pencil, primary |
| `ViewAction` | `view`, magnifying glass, gray |
| `DeleteAction` | `delete`, trash, danger, confirmation |
| `DeleteBulkAction` | `delete_bulk`, “Delete selected”, confirmation |

```python
from almasix.orbit.actions import (
    CreateAction, EditAction, ViewAction, DeleteAction, DeleteBulkAction,
)

table.header_actions([CreateAction.make()])
table.actions([ViewAction.make(), EditAction.make(), DeleteAction.make()])
table.bulk_actions([DeleteBulkAction.make()])
```

Resources auto-wire these when you leave the slots empty — see [Resources](/resources/).

## Calling actions

```python
if save.can(user=request.user):
    save.call(record=post, user=request.user)
```

Authorization failures should be treated as hard no’s in your handlers — don’t render what the user can’t run.
