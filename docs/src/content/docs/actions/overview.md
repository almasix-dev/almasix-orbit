---
title: Overview
description: Buttons, links, icon buttons, badges, modals, notifications, and CRUD presets for Orbit tables and forms.
---

## Introduction

**Actions** are the verbs in your admin UI — save, delete, “archive selected”, anything that should feel like a button with a story. Orbit mirrors Filament 5’s fluent action API: configure chrome, optional modal / form, authorize, then run a callback.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import Action
from almasix.orbit.forms import TextInput

Action.make("save")
    .label("Save changes")
    .color("primary")
    .icon("heroicon-o-check")
    .requires_confirmation()
    .modal_heading("Save post?")
    .modal_description("This will publish the current draft.")
    .form([TextInput.make("note").label("Changelog note")])
    .authorize(lambda user, **_: user is not None)
    .success_notification("Saved")
    .action(lambda **ctx: do_save(**ctx))
```

![Orbit Actions overview (light)](/examples/light/actions/overview.png)

![Orbit Actions overview (dark)](/examples/dark/actions/overview.png)

Rendered triggers speak Conduit: `wire:click="mountAction('save')"` plus `data-confirm` when confirmation is required. URL actions render as `<a>` when no modal is involved.

## Trigger styles

Pick how the trigger looks with `.button()`, `.link()`, `.icon_button()`, or `.badge()` (as a style). Default is a solid button.

```python title="app/orbit/actions/triggers.py"
from almasix.orbit.actions import Action

Action.make("save").label("Save").button().color("primary")
Action.make("docs").label("Docs").link().url("https://orbit.almasix.com")
Action.make("settings").label("Settings").icon("heroicon-o-cog-6-tooth").icon_button()
Action.make("inbox").label("Inbox").badge().color("primary")
```

![Orbit Action trigger styles (light)](/examples/light/actions/overview/triggers.png)

![Orbit Action trigger styles (dark)](/examples/dark/actions/overview/triggers.png)

## Size

`.size("sm" | "md" | "lg")` maps to `or-btn-{size}` classes.

```python title="app/orbit/actions/sizes.py"
from almasix.orbit.actions import Action

Action.make("sm").label("Small").size("sm")
Action.make("md").label("Medium").size("md")
Action.make("lg").label("Large").size("lg")
```

![Orbit Action sizes (light)](/examples/light/actions/overview/sizes.png)

![Orbit Action sizes (dark)](/examples/dark/actions/overview/sizes.png)

## Outlined

`.outlined()` keeps the color accent on the border / text instead of a filled background.

```python title="app/orbit/actions/outlined.py"
from almasix.orbit.actions import Action

Action.make("a").label("Primary").color("primary").outlined()
Action.make("b").label("Danger").color("danger").outlined().without_confirmation()
```

![Orbit Action outlined (light)](/examples/light/actions/overview/outlined.png)

![Orbit Action outlined (dark)](/examples/dark/actions/overview/outlined.png)

## Icons

`.icon(...)` adds a Heroicon. `.icon_position("before" | "after")` places it relative to the label. Icon-only triggers use `.icon_button()` (label becomes `aria-label`).

```python title="app/orbit/actions/icons.py"
from almasix.orbit.actions import Action

Action.make("before").label("Before").icon("heroicon-o-check").icon_position("before")
Action.make("after").label("After").icon("heroicon-o-chevron-right").icon_position("after")
```

![Orbit Action icons (light)](/examples/light/actions/overview/icons.png)

![Orbit Action icons (dark)](/examples/dark/actions/overview/icons.png)

### Labeled from breakpoint

`.labeled_from("sm")` (and friends) keeps an icon-forward compact trigger until the breakpoint, then shows the label — useful in dense table toolbars.

## Tooltip

`.tooltip(...)` sets the native `title` on the trigger (string or callable).

```python title="app/orbit/actions/tooltip.py"
from almasix.orbit.actions import Action

Action.make("publish")
    .label("Publish")
    .icon("heroicon-o-check")
    .tooltip("Publish this draft to production")
```

![Orbit Action tooltip (light)](/examples/light/actions/overview/tooltip.png)

![Orbit Action tooltip (dark)](/examples/dark/actions/overview/tooltip.png)

## Keybindings

`.key_bindings(["mod+s", "mod+enter"])` emits `data-key-bindings` for the panel host / Alpine layer to wire shortcuts. Bindings are declarative — the host owns the listener.

```python title="app/orbit/actions/keys.py"
from almasix.orbit.actions import Action

Action.make("save").label("Save").key_bindings(["mod+s"]).action(lambda **_: None)
```

## URL + new tab

`.url(...)` turns the action into a link when no modal / confirmation is required. Pass `open_in_new_tab=True` on `.url(...)`, or chain `.open_url_in_new_tab()`.

```python title="app/orbit/actions/url.py"
from almasix.orbit.actions import Action

Action.make("site")
    .label("Open site")
    .icon("heroicon-o-document-text")
    .url("https://orbit.almasix.com", open_in_new_tab=True)
```

![Orbit Action URL (light)](/examples/light/actions/overview/url.png)

![Orbit Action URL (dark)](/examples/dark/actions/overview/url.png)

Call `.modal()` when you want a dialog even if a URL is also configured — modal wins.

## Authorize

`.authorize(bool | Callable)` gates visibility via `.can(**ctx)`. By default unauthorized actions render nothing. Prefer UX alternatives when you want a disabled affordance:

- `.authorization_tooltip("…")` — disabled button with that tooltip
- `.authorization_notification("…")` — still rendered; host can toast on click

```python title="app/orbit/actions/authorize.py"
from almasix.orbit.actions import Action

Action.make("admin")
    .label("Admin only")
    .authorize(False)
    .authorization_tooltip("You need admin access")
    .color("danger")
    .without_confirmation()
```

![Orbit Action authorize (light)](/examples/light/actions/overview/authorize.png)

![Orbit Action authorize (dark)](/examples/dark/actions/overview/authorize.png)

## Schema / form

`.form([...])` (alias `.schema([...])`) collects fields before the callback runs. The panel modal host clones the embedded `<template class="or-action-form-tpl">`. Use `.fill_form({...})` to seed values and `.disabled_form()` for read-only (ViewAction does this automatically).

```python title="app/orbit/actions/schema.py"
from almasix.orbit.actions import Action
from almasix.orbit.forms import TextInput

Action.make("note")
    .label("Add note")
    .modal()
    .modal_heading("Changelog note")
    .form([TextInput.make("note").label("Note")])
```

![Orbit Action schema (light)](/examples/light/actions/overview/schema.png)

![Orbit Action schema (dark)](/examples/dark/actions/overview/schema.png)

## Notifications

Toast intent rides on data attributes for the host:

| Method | Role |
|--------|------|
| `.success_notification` | Body after success (`None` clears the default) |
| `.success_notification_title` | Title |
| `.failure_notification` / `.failure_notification_title` | Failure copy |
| `.success_redirect_url` | Navigate after success |

```python title="app/orbit/actions/notifications.py"
from almasix.orbit.actions import Action

Action.make("save")
    .label("Save")
    .success_notification("Saved")
    .success_notification_title("Success")
    .failure_notification("Could not save")
```

![Orbit Action notifications (light)](/examples/light/actions/overview/notifications.png)

![Orbit Action notifications (dark)](/examples/dark/actions/overview/notifications.png)

## Badges

Two badge modes:

1. **Trigger style** — `.badge()` (bool) renders the button as a badge chip.
2. **Count indicator** — `.badge(3)` / `.badge(callable)` plus `.badge_color(...)` adds a small indicator next to the label.

```python title="app/orbit/actions/badge.py"
from almasix.orbit.actions import Action

Action.make("inbox").label("Inbox").icon("heroicon-o-bell").badge(3).badge_color("danger")
```

![Orbit Action badge (light)](/examples/light/actions/overview/badge.png)

![Orbit Action badge (dark)](/examples/dark/actions/overview/badge.png)

## Lifecycle overview

`.call(**ctx)` runs:

1. `.before(...)` — call `action.halt()` / `action.cancel()` to stop
2. `.mutate_data_using(...)` when `data=` is present
3. `.mutate_record_data_using(...)` when `record=` is present
4. `.using(...)` if set, else `.action(...)`
5. `.after(...)` unless halted / cancelled

Presets (Create / Edit / Delete / …) add persistence hooks on top — see each preset page. Full modal chrome lives on [Modals](/actions/modals/). Groups live on [Grouping actions](/actions/grouping-actions/).

```python title="app/orbit/actions/lifecycle.py"
from almasix.orbit.actions import Action

Action.make("publish")
    .before(lambda action, **_: action.halt() if dry_run else None)
    .mutate_data_using(lambda data, **_: {**data, "published": True})
    .using(lambda record, data, **_: persist(record, data))
    .after(lambda **_: notify_slack())
```

## Presets

| Class | Defaults |
|-------|----------|
| [`CreateAction`](/actions/create/) | `create`, plus icon, primary; `.create_another` |
| [`EditAction`](/actions/edit/) | `edit`, pencil, primary |
| [`ViewAction`](/actions/view/) | `view`, magnifying glass, gray; disabled form |
| [`DeleteAction`](/actions/delete/) | `delete`, trash, danger, confirmation |
| `DeleteBulkAction` | `delete_bulk`, “Delete selected”, confirmation |
| [`ReplicateAction`](/actions/replicate/) | replica helpers + exclude attributes |
| [`ForceDeleteAction`](/actions/force-delete/) | permanent delete |
| [`RestoreAction`](/actions/restore/) | soft-delete restore |
| [`ImportAction`](/actions/import/) / [`ExportAction`](/actions/export/) | file adapters |

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import (
    CreateAction, EditAction, ViewAction, DeleteAction, DeleteBulkAction,
)

table.header_actions([CreateAction.make()])
table.actions([ViewAction.make(), EditAction.make(), DeleteAction.make()])
table.bulk_actions([DeleteBulkAction.make()])
```

Resources auto-wire these when you leave the slots empty — see [Resources](/resources/overview/).

## Fluent surface cheat sheet

| Method | Role |
|--------|------|
| `.label` / `.color` / `.icon` / `.icon_position` | Chrome |
| `.button` / `.link` / `.icon_button` / `.badge` | Trigger style |
| `.size` / `.outlined` / `.labeled_from` | Density |
| `.tooltip` / `.key_bindings` | Affordances |
| `.url` / `.open_url_in_new_tab` | Link mode |
| `.requires_confirmation` / `.without_confirmation` | Confirm gate |
| `.modal` / `.slide_over` / `.modal_*` | Dialog chrome — [Modals](/actions/modals/) |
| `.form` / `.schema` / `.fill_form` / `.disabled_form` | Fields before run |
| `.authorize` / `.authorization_tooltip` | Gate with `.can(**ctx)` |
| `.success_notification` / `.failure_notification` | Toast intent |
| `.before` / `.after` / `.using` / `.halt` / `.cancel` | Lifecycle |
| `.action` | What runs on `.call(...)` |

Colors map to `or-btn-{color}` (`primary`, `danger`, `gray`, `success`, `warning`, `info`, …).
