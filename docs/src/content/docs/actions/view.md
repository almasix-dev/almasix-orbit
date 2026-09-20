---
title: View action
description: ViewAction preset — read-only modal forms or view-page URLs.
---

## Introduction

`ViewAction` opens a record in read-only mode. Defaults: name `view`, label **View**, magnifying-glass icon, gray color.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import ViewAction
from almasix.orbit.forms import TextInput, Textarea

ViewAction.make()
    .modal()
    .modal_heading("View post")
    .form([
        TextInput.make("title"),
        Textarea.make("body"),
    ])
```

![Orbit ViewAction (light)](/examples/light/actions/view.png)

![Orbit ViewAction (dark)](/examples/dark/actions/view.png)

Calling `.form([...])` on `ViewAction` automatically sets `.modal()` and `.disabled_form()` so fields render locked.

## View page URL

Prefer a dedicated ViewRecord page:

```python title="app/orbit/actions/view_url.py"
from almasix.orbit.actions import ViewAction

ViewAction.make().url(lambda record, **_: f"/posts/{record['id']}")
```

Pair with an [Infolist](/infolists/overview/) on the resource for Filament-style show pages.

## Authorization

```python title="app/orbit/actions/view_auth.py"
from almasix.orbit.actions import ViewAction

ViewAction.make().authorize(lambda record, user, **_: can_view(user, record))
```

Unauthorized view actions hide by default — use `.authorization_tooltip(...)` if you want a disabled trigger instead.
