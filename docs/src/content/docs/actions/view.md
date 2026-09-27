---
title: View action
description: ViewAction preset — infolist modals or view-page URLs.
---

## Introduction

`ViewAction` opens a record for reading. On a table row it can open the view page, or a modal that shows the record's infolist. Defaults: name `view`, label **View**, magnifying-glass icon, gray color.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import ViewAction
from almasix.orbit.forms import TextInput, Textarea

ViewAction.make()
    .modal_heading("View post")
    .form([
        TextInput.make("title"),
        Textarea.make("body"),
    ])
```

![Orbit ViewAction (light)](/examples/light/actions/view.png)

![Orbit ViewAction (dark)](/examples/dark/actions/view.png)

`.form([...])` opens the modal and renders those fields as an infolist: labels and values, not inputs. The dialog has a close button and no Save or Cancel action.

Pass infolist entries directly when the view should not follow the form:

```python title="app/orbit/actions/view_infolist.py"
from almasix.orbit.actions import ViewAction
from almasix.orbit.infolists import TextEntry

ViewAction.make().infolist([
    TextEntry.make("title"),
    TextEntry.make("body"),
])
```

## View page URL

Prefer a dedicated ViewRecord page:

```python title="app/orbit/actions/view_url.py"
from almasix.orbit.actions import ViewAction

ViewAction.make().url(lambda record, **_: f"/posts/{record['id']}")
```

![Orbit ViewAction URL (light)](/examples/light/actions/view/url.png)

![Orbit ViewAction URL (dark)](/examples/dark/actions/view/url.png)

The view page uses the resource [infolist](/infolists/overview/).

## Authorization

```python title="app/orbit/actions/view_auth.py"
from almasix.orbit.actions import ViewAction

ViewAction.make().authorize(lambda record, user, **_: can_view(user, record))
```

Unauthorized view actions hide by default — use `.authorization_tooltip(...)` if you want a disabled trigger instead.
