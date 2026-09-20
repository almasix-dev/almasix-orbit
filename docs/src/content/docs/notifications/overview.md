---
title: Overview
description: Flash toast notifications — title, body, icon, color, status, duration, actions, JS client, and alignment.
---

## Introduction

**Notifications** are short, typed messages built with a fluent `Notification` API. Calling `.send()` flashes them into the panel toast host (Alpine `orbitNotifications`). The same object can also [persist to the database bell](/notifications/database-notifications/) or [broadcast live](/notifications/broadcast-notifications/).

Use them after a save, when a background job finishes, or anywhere you want a non-blocking “it worked / look at this” cue without navigating away.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.notifications import Notification

Notification.make()
    .title("Saved successfully")
    .success()
    .send()
```

![Orbit Notifications overview (light)](/examples/light/notifications/overview.png)

![Orbit Notifications overview (dark)](/examples/dark/notifications/overview.png)

The panel shell renders a toast host when notifications are enabled (default). Pair with action `.success_notification("Saved")` so CRUD flows feel finished — see [Actions](/actions/overview/).

## Setting a title

The main message is the title. Pass it via `.title(...)`, or use `Notification.make(title="…")`.

To give the toast a **stable id** you can close later, pass a single word (no spaces) as the first argument: `Notification.make("greeting")`. Otherwise Orbit assigns a random id.

```python title="app/orbit/notifications/title.py"
from almasix.orbit.notifications import Notification

Notification.make()
    .title("Saved successfully")
    .send()
```

![Orbit Notification title (light)](/examples/light/notifications/overview/title.png)

![Orbit Notification title (dark)](/examples/dark/notifications/overview/title.png)

Or from JavaScript with `OrbitNotification`:

```js title="resources/js/notify.js"
new OrbitNotification()
  .title("Saved successfully")
  .send();
```

## Setting an icon

Optionally show a Heroicon in front of the content. `.icon_color(...)` tints the icon (defaults follow status when you use `.success()` and friends).

```python title="app/orbit/notifications/icon.py"
from almasix.orbit.notifications import Notification

Notification.make()
    .title("Saved successfully")
    .icon("heroicon-o-document-text")
    .icon_color("success")
    .send()
```

![Orbit Notification icon (light)](/examples/light/notifications/overview/icon.png)

![Orbit Notification icon (dark)](/examples/dark/notifications/overview/icon.png)

```js title="resources/js/notify.js"
new OrbitNotification()
  .title("Saved successfully")
  .icon("heroicon-o-document-text")
  .iconColor("success")
  .send();
```

## Status helpers

Notifications often carry a status — `success`, `warning`, `danger`, or `info`. Prefer `.success()` / `.warning()` / `.danger()` / `.info()` (or `.status(...)`). Status sets a default icon and colors unless you already called `.icon(...)` / `.color(...)`.

```python title="app/orbit/notifications/status.py"
from almasix.orbit.notifications import Notification

Notification.make()
    .title("Saved successfully")
    .success()
    .send()
```

![Orbit Notification status (light)](/examples/light/notifications/overview/status.png)

![Orbit Notification status (dark)](/examples/dark/notifications/overview/status.png)

```js title="resources/js/notify.js"
new OrbitNotification()
  .title("Saved successfully")
  .success()
  .send();
```

## Setting a background color

Use `.color(...)` for extra context on the toast chrome (`success`, `warning`, `danger`, `info`, …). Status helpers set color automatically when unset.

```python title="app/orbit/notifications/color.py"
from almasix.orbit.notifications import Notification

Notification.make()
    .title("Saved successfully")
    .color("success")
    .send()
```

![Orbit Notification color (light)](/examples/light/notifications/overview/color.png)

![Orbit Notification color (dark)](/examples/dark/notifications/overview/color.png)

## Setting a duration

By default toasts close after **6 seconds**. Override with `.duration(ms)` or `.seconds(n)`.

```python title="app/orbit/notifications/duration.py"
from almasix.orbit.notifications import Notification

Notification.make()
    .title("Saved successfully")
    .success()
    .duration(5000)
    .send()

Notification.make()
    .title("Saved successfully")
    .success()
    .seconds(5)
    .send()
```

![Orbit Notification duration (light)](/examples/light/notifications/overview/duration.png)

![Orbit Notification duration (dark)](/examples/dark/notifications/overview/duration.png)

### Persistent toasts

`.persistent()` keeps the toast until the user dismisses it (no auto-close).

```python title="app/orbit/notifications/persistent.py"
from almasix.orbit.notifications import Notification

Notification.make()
    .title("Review required")
    .warning()
    .persistent()
    .send()
```

![Orbit Notification persistent (light)](/examples/light/notifications/overview/persistent.png)

![Orbit Notification persistent (dark)](/examples/dark/notifications/overview/persistent.png)

```js title="resources/js/notify.js"
new OrbitNotification()
  .title("Review required")
  .warning()
  .persistent()
  .send();
```

## Setting body text

`.body(...)` adds a secondary line under the title (`body_text` is a legacy alias).

```python title="app/orbit/notifications/body.py"
from almasix.orbit.notifications import Notification

Notification.make()
    .title("Saved successfully")
    .success()
    .body("Changes to the post have been saved.")
    .send()
```

![Orbit Notification body (light)](/examples/light/notifications/overview/body.png)

![Orbit Notification body (dark)](/examples/dark/notifications/overview/body.png)

## Adding actions

Footer buttons use `NotificationAction`. They can open a URL, dispatch a browser event, close the toast, or mark database rows read/unread.

```python title="app/orbit/notifications/actions.py"
from almasix.orbit.notifications import Notification, NotificationAction

Notification.make()
    .title("Saved successfully")
    .success()
    .body("Changes to the post have been saved.")
    .actions([
        NotificationAction.make("view")
            .button()
            .url("/admin/posts/1", should_open_in_new_tab=True),
        NotificationAction.make("undo")
            .color("gray")
            .dispatch("undoEditingPost", [1])
            .close(),
    ])
    .send()
```

![Orbit Notification actions (light)](/examples/light/notifications/overview/actions.png)

![Orbit Notification actions (dark)](/examples/dark/notifications/overview/actions.png)

```js title="resources/js/notify.js"
new OrbitNotification()
  .title("Saved successfully")
  .success()
  .body("Changes to the post have been saved.")
  .actions([
    new OrbitNotificationAction("view").button().url("/view").openUrlInNewTab(),
    new OrbitNotificationAction("undo").color("gray").dispatch("undoEditingPost").close(),
  ])
  .send();
```

| Method | Notes |
|--------|-------|
| `.button` | Render as a compact button |
| `.url` | Link target; `should_open_in_new_tab` / `.open_url_in_new_tab` |
| `.dispatch` / `.dispatch_self` / `.dispatch_to` | Browser / component events + payload |
| `.close` | Dismiss the toast after the action |
| `.color` | Action chrome color |
| `.mark_as_read` / `.mark_as_unread` | Database bell helpers |

## Sending notifications

`.send()` uses the **flash** channel and the context-local `Notifier` (process default when unset). Prefer calling it from actions, services, or after mutations — the next panel render (or the JS client) shows the toast.

```python title="app/orbit/notifications/send.py"
from almasix.orbit.notifications import Notification, get_notifier

Notification.make().title("Hello").info().send()

# Tests / request scope
notifier = get_notifier()
assert notifier.peek_flash()
```

Testing helpers: `assert_notified`, `assert_not_notified`, `reset_notifications` from `almasix.orbit.notifications`.

## Using the JavaScript objects

Published `orbit.js` assigns `window.OrbitNotification` and `window.OrbitNotificationAction`. They dispatch `orbit:notify` for the Alpine toast host.

```js title="resources/js/notify.js"
new OrbitNotification()
  .title("Saved successfully")
  .success()
  .body("Changes to the post have been saved.")
  .send();
```

Action buttons can also toast without Python via `data-success-notification` / `data-failure-notification` (set by `.success_notification(...)` / `.failure_notification(...)`).

## Closing a notification by id

After `.send()`, call `.get_id()` (Python) or `.getId()` (JS). Dispatch `close-notification` with that id, or pass a custom id when creating the notification.

```python title="app/orbit/notifications/close.py"
from almasix.orbit.notifications import Notification

note = (
    Notification.make("greeting")
    .title("Hello")
    .persistent()
    .send()
)
# Close later: dispatch close-notification with id "greeting"
```

```html title="templates/close_toast.html"
<button
  type="button"
  x-on:click="$dispatch('close-notification', { id: 'greeting' })"
>
  Close
</button>
```

Random ids are safer when you can persist them; reuse a custom id only when you intend to replace/close that toast.

## Positioning notifications

Configure toast alignment process-wide (provider / middleware) with `Notifications.alignment` and `Notifications.vertical_alignment`. Values: `start` / `center` / `end` for both axes (defaults: end + start).

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit.notifications import Alignment, Notifications, VerticalAlignment

Notifications.alignment(Alignment.START)
Notifications.vertical_alignment(VerticalAlignment.END)
```

![Orbit Notification alignment (light)](/examples/light/notifications/overview/alignment.png)

![Orbit Notification alignment (dark)](/examples/dark/notifications/overview/alignment.png)

Related: [Database notifications](/notifications/database-notifications/), [Broadcast notifications](/notifications/broadcast-notifications/).
