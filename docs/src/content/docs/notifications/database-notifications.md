---
title: Database notifications
description: Persist notifications to the panel bell — enable, seed, send, poll, position, and mark as read.
---

## Introduction

**Database notifications** stay in a panel bell until the user marks them read. Orbit mirrors Filament’s `databaseNotifications` panel API and `sendToDatabase` channel, with an in-memory store by default and a pluggable `DatabaseNotificationStore` for real persistence.

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit import Panel
from almasix.orbit.panels.users import PanelNotification

Panel.make("admin")
    .path("admin")
    .database_notifications([
        PanelNotification.make("Welcome")
            .body("Database notifications are on.")
            .status("success"),
        PanelNotification.make("Deploy finished")
            .body("v1.4.2 is live.")
            .status("info")
            .read(),
    ])
```

![Orbit Database notifications (light)](/examples/light/notifications/database-notifications.png)

![Orbit Database notifications (dark)](/examples/dark/notifications/database-notifications.png)

## Enabling the bell

Call `.database_notifications(True)` to enable an empty bell, or pass a sequence of `PanelNotification` / dict seeds (enables and registers items). Optional `position` moves the trigger.

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit import Panel

Panel.make("admin")
    .path("admin")
    .database_notifications(True)

Panel.make("admin")
    .path("admin")
    .database_notifications(True, position="sidebar")
```

| Method | Notes |
|--------|-------|
| `.database_notifications` | `True` / `False`, or a sequence of seeds |
| `.database_notifications_position` | `topbar` (default) or `sidebar` |
| `.database_notifications_polling` | `'30s'`, ms int, or `None` to disable |
| `.notification` | Append one seed (also enables the feature) |

![Orbit Database notifications enable (light)](/examples/light/notifications/database-notifications/enable.png)

![Orbit Database notifications enable (dark)](/examples/dark/notifications/database-notifications/enable.png)

## Sending database notifications

Use the fluent API’s `.send_to_database(...)` (or `.to_database()` then `.send()`). Pass a user/recipient when your store keys by principal. Set `is_event_dispatched=True` to record a `DatabaseNotificationsSent`-style event for immediate refresh hooks.

```python title="app/orbit/notifications/database_send.py"
from almasix.orbit.notifications import Notification

Notification.make()
    .title("New comment")
    .body("Alex replied on Launch Orbit.")
    .info()
    .send_to_database(user, is_event_dispatched=True)
```

![Orbit Database notifications send (light)](/examples/light/notifications/database-notifications/send.png)

![Orbit Database notifications send (dark)](/examples/dark/notifications/database-notifications/send.png)

The default `InMemoryDatabaseNotificationStore` is enough for demos and tests. Swap it with `Notifier.use_store(...)` implementing `DatabaseNotificationStore` (`save`, `mark_read`, `mark_unread`, `mark_all_read`, `get_for_user`).

## Position

Top bar (default) places the bell next to theme / user chrome. Sidebar nests it above the nav list.

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit import Panel

Panel.make("admin")
    .path("admin")
    .database_notifications(True)
    .database_notifications_position("sidebar")
```

![Orbit Database notifications position (light)](/examples/light/notifications/database-notifications/position.png)

![Orbit Database notifications position (dark)](/examples/dark/notifications/database-notifications/position.png)

## Polling

Without websockets, the Alpine `orbitDatabaseNotifications` component polls on an interval (default **30s**). Pass `'15s'`, a millisecond int, or `None`.

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit import Panel

Panel.make("admin")
    .path("admin")
    .database_notifications(True)
    .database_notifications_polling("15s")
```

Apps can listen for `orbit:database-notifications-poll` / dispatch `orbit:database-notifications-refresh` to replace or refresh the list.

## Marking as read

The panel UI marks a row read on click and exposes **Mark all as read**. From Python, use the store:

```python title="app/orbit/notifications/mark_read.py"
from almasix.orbit.notifications import get_notifier

store = get_notifier().store
store.mark_read(notification_id, user=user)
store.mark_all_read(user=user)
```

Notification actions can set `.mark_as_read()` / `.mark_as_unread()` for toast/database footers.

![Orbit Database notifications mark read (light)](/examples/light/notifications/database-notifications/mark-read.png)

![Orbit Database notifications mark read (dark)](/examples/dark/notifications/database-notifications/mark-read.png)

Related: [Overview](/notifications/overview/), [Broadcast notifications](/notifications/broadcast-notifications/).
