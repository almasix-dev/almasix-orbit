---
title: Database notifications
description: Persist notifications to the panel bell — enable, seed, send, poll, position, and mark as read.
---

## Introduction

**Database notifications** stay in a panel **bell** until the user marks them read. Unlike flash toasts (which disappear after a few seconds), these messages accumulate so someone can catch up later.

Enable the feature on the panel, optionally seed demo rows, then send new items with `.send_to_database(...)`. Orbit ships an in-memory store by default. For a process that restarts (or multiple workers sharing a file), call `.sqlite_notifications(...)` — that uses stdlib SQLite and implements the same `DatabaseNotificationStore` contract.

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
    .sqlite_notifications("orbit-notifications.sqlite")
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
| `.sqlite_notifications` | SQLite file path or `':memory:'` (also enables the bell) |
| `.database_notifications_store` | Plug in any `DatabaseNotificationStore` |
| `.notification` | Append one seed (also enables the feature) |

![Orbit Database notifications enable (light)](/examples/light/notifications/database-notifications/enable.png)

![Orbit Database notifications enable (dark)](/examples/dark/notifications/database-notifications/enable.png)

## Sending database notifications

Use the fluent API’s `.send_to_database(...)` (or `.to_database()` then `.send()`). Pass a user/recipient when your store keys by principal. Set `is_event_dispatched=True` when you want an immediate refresh signal for the bell UI (for example after a live write).

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

The default `InMemoryDatabaseNotificationStore` is enough for demos and tests. `.sqlite_notifications("orbit-notifications.sqlite")` persists rows with stdlib SQLite (upsert on `id`). Swap in any `DatabaseNotificationStore` via `.database_notifications_store(...)` or `Notifier.use_store(...)` (`save`, `mark_read`, `mark_unread`, `mark_all_read`, `get_for_user`).

![Orbit Database notifications SQLite store (light)](/examples/light/notifications/database-notifications/sqlite.png)

![Orbit Database notifications SQLite store (dark)](/examples/dark/notifications/database-notifications/sqlite.png)

When the bell is enabled, Orbit also mounts **GET/POST** `{panel}/orbit-notifications`. The Alpine `orbitDatabaseNotifications` component polls that URL and posts mark-read updates so the store stays in sync without a full page reload.

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

The Alpine `orbitDatabaseNotifications` component polls on an interval (default **30s**). Pass `'15s'`, a millisecond int, or `None`. When the panel bell is on, each poll hits `{panel}/orbit-notifications` and replaces the list from the store.

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit import Panel

Panel.make("admin")
    .path("admin")
    .database_notifications(True)
    .database_notifications_polling("15s")
    .sqlite_notifications("orbit-notifications.sqlite")
```

Apps can still listen for `orbit:database-notifications-poll` / dispatch `orbit:database-notifications-refresh` to replace or refresh the list.

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
