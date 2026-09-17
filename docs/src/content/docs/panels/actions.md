---
title: Panel actions
description: Modal vs page URLs, View/Edit defaults, .modal(), and mountAction in Orbit.
---

Actions are how the panel *does* things — open a page, open a modal, confirm a delete, or run a callback with a short form first.

```python
from almasix.orbit.actions import Action, ViewAction, EditAction, DeleteAction
from almasix.orbit.forms import TextInput

archive = (
    Action.make("archive")
    .label("Archive")
    .color("warning")
    .requires_confirmation()
    .modal_heading("Archive this post?")
    .modal_description("It will leave the public index.")
    .form([TextInput.make("reason").label("Reason")])
    .success_notification("Archived")
    .action(lambda record=None, **_: archive_post(record))
)
```

Rendered buttons speak Conduit: `wire:click="mountAction('archive')"`. Link-style actions use `href` instead.

## Modal vs page URL

An action becomes a **link** when it has a URL and is not modal-ish:

```python
ViewAction.make().url("/posts/1")           # <a href="…">
EditAction.make().url(lambda record=None, **_: f"/posts/{record['id']}/edit")
```

It becomes a **button** that mounts a modal / confirm flow when any of these are true:

- `.modal()` was called
- `.requires_confirmation()` is on
- `.form([...])` has fields
- the action color is **`danger`** (always confirms unless `.without_confirmation()`)

Form fields from `.form([...])` render inside the shell dialog (`or-action-form-tpl` → Alpine `orbitActionModal`). Demo: **Columns → Modal forms** in `examples/orbit-admin`.

Destructive deletes always confirm, including when Conduit is present (the click interceptor opens the dialog before `mountAction` runs).

```python
EditAction.make().url("/posts/1/edit")           # navigates
EditAction.make().url("/posts/1/edit").modal() # stays put — mountAction
DeleteAction.make()                              # confirm modal by default
```

`is_modal()` is the boolean behind that choice.

## Resource defaults

When a Resource leaves table action slots empty, Orbit wires:

| Slot | Defaults |
|------|----------|
| Row | `ViewAction` → view URL, `EditAction` → edit URL, `DeleteAction` (confirm) |
| Bulk | `DeleteBulkAction` |
| Header | `CreateAction` → create URL |

```python
# conceptually what get_table() does
ViewAction.make().url(lambda record=None, **_: cls.page_url("view", record))
EditAction.make().url(lambda record=None, **_: cls.page_url("edit", record))
CreateAction.make().url(lambda **_: cls.page_url("create"))
```

Override by setting `.actions([...])` (etc.) yourself. Call `.modal()` on View/Edit if you want quick panels instead of full pages.

## mountAction

Conduit components expose `mountAction(name)` — the button’s `wire:click` target. Your live component should:

1. Resolve the action by name from the table / page / resource.
2. If it needs confirmation or a form, show the modal host.
3. On submit, call `action.call(record=..., user=..., **data)`.

```html
<button type="button" class="or-btn or-btn-danger" data-action="delete"
        data-confirm="true" data-modal-heading="Delete?"
        wire:click="mountAction('delete')">
  <span>Delete</span>
</button>
```

Authorization: `.authorize(bool | callable)` + `.can(**ctx)` — don’t render what the user can’t run.

More presets and the fluent surface live on the package [Actions](/actions/overview/) page.
