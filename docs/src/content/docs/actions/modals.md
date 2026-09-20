---
title: Modals
description: Confirmation dialogs, form modals, slide-overs, sticky chrome, and modal labels for Orbit actions.
---

## Introduction

Any action that needs confirmation or a form opens the shared **action modal host** in the panel shell. Call `.modal()`, `.requires_confirmation()`, or `.form([...])` — danger-colored actions confirm by default unless you call `.without_confirmation()`.

```python title="app/orbit/actions/confirm.py"
from almasix.orbit.actions import Action

Action.make("archive")
    .label("Archive")
    .color("warning")
    .requires_confirmation()
    .modal_heading("Archive post?")
    .modal_description("Hidden from the default list until restored.")
```

![Orbit Action confirmation modal (light)](/examples/light/actions/modals/confirm.png)

![Orbit Action confirmation modal (dark)](/examples/dark/actions/modals/confirm.png)

The host reads `data-modal-*` attributes from the trigger and dispatches `orbit:mount-action` for Alpine `orbitActionModal`.

## Form modals

`.form([...])` (or `.schema([...])`) embeds field HTML in a `<template>` on the trigger. The modal clones those fields when opened. Prefer this for quick create/edit without a full page.

```python title="app/orbit/actions/form_modal.py"
from almasix.orbit.actions import EditAction
from almasix.orbit.forms import TextInput, Select

EditAction.make()
    .modal()
    .modal_heading("Edit post")
    .modal_description("Update the title and status.")
    .form([
        TextInput.make("title").label("Title").required(),
        Select.make("status").label("Status").options({
            "draft": "Draft",
            "published": "Published",
        }),
    ])
```

![Orbit Action form modal (light)](/examples/light/actions/modals/form.png)

![Orbit Action form modal (dark)](/examples/dark/actions/modals/form.png)

Seed values with `.fill_form({...})` or by passing `record=` at render time. `.disabled_form()` locks fields (used by [View action](/actions/view/)).

## Slide over

`.slide_over()` opens a side panel instead of a centered dialog. `.slide_over_position("left" | "right")` chooses the edge (default `right`).

```python title="app/orbit/actions/slide_over.py"
from almasix.orbit.actions import Action
from almasix.orbit.forms import TextInput

Action.make("quick_edit")
    .label("Quick edit")
    .slide_over()
    .slide_over_position("right")
    .modal_heading("Quick edit")
    .form([TextInput.make("title").label("Title")])
```

![Orbit Action slide over (light)](/examples/light/actions/modals/slide-over.png)

![Orbit Action slide over (dark)](/examples/dark/actions/modals/slide-over.png)

## Width

`.modal_width("sm" | "md" | "lg" | "xl" | "2xl" | …)` maps to `or-modal-{width}` on the host.

```python title="app/orbit/actions/modal_width.py"
from almasix.orbit.actions import Action

Action.make("edit").modal().modal_width("2xl").modal_heading("Wide editor")
```

## Submit and cancel labels

Override footer buttons with `.modal_submit_action_label(...)` and `.modal_cancel_action_label(...)`.

```python title="app/orbit/actions/modal_labels.py"
from almasix.orbit.actions import Action

Action.make("archive")
    .requires_confirmation()
    .modal_heading("Archive post?")
    .modal_description("Move this post to the archive.")
    .modal_submit_action_label("Archive")
    .modal_cancel_action_label("Keep editing")
```

![Orbit Action modal labels (light)](/examples/light/actions/modals/labels.png)

![Orbit Action modal labels (dark)](/examples/dark/actions/modals/labels.png)

## Icon and alignment

`.modal_icon(...)` / `.modal_icon_color(...)` show an icon above the heading. `.modal_alignment("start" | "center")` centers header and actions when set to `center`.

```python title="app/orbit/actions/modal_icon.py"
from almasix.orbit.actions import Action

Action.make("publish")
    .requires_confirmation()
    .modal_heading("Publish?")
    .modal_description("Make this draft live on the public site.")
    .modal_icon("heroicon-o-check")
    .modal_icon_color("success")
    .modal_alignment("center")
```

![Orbit Action modal icon (light)](/examples/light/actions/modals/icon.png)

![Orbit Action modal icon (dark)](/examples/dark/actions/modals/icon.png)

## Sticky header / footer

For tall forms, pin chrome:

```python title="app/orbit/actions/sticky.py"
from almasix.orbit.actions import Action

Action.make("edit")
    .modal()
    .sticky_modal_header()
    .sticky_modal_footer()
    .modal_heading("Edit post")
```

## Close behavior

| Method | Default | Notes |
|--------|---------|-------|
| `.close_modal_by_clicking_away` | `True` | Backdrop click |
| `.close_modal_by_escaping` | `True` | Escape key |
| `.modal_close_button` | `True` | × in the corner |
| `.modal_autofocus` | `True` | Focus first field / primary |

```python title="app/orbit/actions/close_behavior.py"
from almasix.orbit.actions import Action

Action.make("critical")
    .requires_confirmation()
    .modal_heading("Irreversible")
    .close_modal_by_clicking_away(False)
    .close_modal_by_escaping(False)
    .modal_close_button(False)
```

## Confirmation defaults

- `.requires_confirmation()` forces a confirm dialog
- `.without_confirmation()` opts out (even for danger colors)
- Danger color without opt-out confirms automatically with heading `{label}?` and “This action cannot be undone.”

See [Delete](/actions/delete/) and [Force-delete](/actions/force-delete/) for preset copy.
