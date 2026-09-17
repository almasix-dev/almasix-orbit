---
title: Notifications
description: Flash, database, and broadcast notifications with Orbit’s Notifier.
---

Orbit notifications are small, typed messages you can flash to the session, persist, or broadcast — then render with a dash of Alpine.

```python
from almasix.orbit.notifications import Notification, Notifier

note = (
    Notification.make("Post saved")
    .body_text("Your changes are live.")
    .success()          # or .warning() / .danger() / .info()
    .seconds(6)         # duration in seconds → ms under the hood
)

notifier = Notifier()
notifier.send(note)
flash = notifier.flash()          # pop the flash bag
html = notifier.render_flash()    # Alpine orbitNotifications wrapper
```

## Channels

| Method | Channel |
|--------|---------|
| (default) | `flash` |
| `.send_to_database()` | `database` |
| `.broadcast()` | `broadcast` |

```python
Notification.make("Backup done").info().send_to_database()
Notification.make("Deploy finished").success().broadcast()
```

`.persistent_mode()` keeps a toast around until the user dismisses it.

## Status helpers

```python
from almasix.orbit.notifications import NotificationStatus

note.success()
# equivalent idea: status = NotificationStatus.SUCCESS
```

## In the browser

Published `orbit.js` registers Alpine `orbitNotifications` data. Drop `@orbitScripts` (or the vendor script) in the layout, render `notifier.render_flash()`, and toasts have somewhere to live.

Pair with action `.success_notification("Saved")` so CRUD flows feel finished — see [Actions](/actions/).
