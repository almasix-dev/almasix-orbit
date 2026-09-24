---
title: Database notifications
description: Persist notifications to the panel bell using Almasix's notifications table — migrate, enable, send, poll, and mark as read.
---

## Introduction

**Database notifications** stay in a panel **bell** until the user marks them read. The dropdown shows unread items only; **View all** opens the full history deck (newest first, infinite scroll). A detail modal shows the full message and marks it read.

Production apps store those rows in Almasix's polymorphic **`notifications`** table — the same table the framework database channel uses. Generate it with Smith, migrate, mix `Notifiable` onto your user model, then enable the bell with `.database_notifications_using_almasix()`.

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
    .database_notifications_using_almasix()
```

![Orbit Database notifications (light)](/examples/light/notifications/database-notifications.png)

![Orbit Database notifications (dark)](/examples/dark/notifications/database-notifications.png)

## Prerequisites

### 1. Create the notifications table

```shell
smith notifications:table
# or (Laravel 11+ naming)
smith make:notifications-table

smith migrate
```

That migration creates UUID `id`, `type`, morph `notifiable_*`, JSON `data`, nullable `read_at`, and timestamps. Orbit writes bell fields (`title`, `body`, `status`, `icon`, `actions`, …) into the `data` column.

### 2. Make users notifiable

```python title="app/models/user.py"
from almasix.auth import AuthenticatableMixin
from almasix.notifications import Notifiable
from almasix.orm import Model

class User(AuthenticatableMixin, Notifiable, Model):
    fillable = ("name", "email", "password", "remember_token")
    hidden = ("password", "remember_token")
```

`Notifiable` is what Almasix uses for `await user.notify(...)` and for morph identity when listing inbox rows. The panel bell scopes by the same morph columns.

## Enabling the bell

Call `.database_notifications(True)` (or pass seeds), then `.database_notifications_using_almasix()` so the bell reads and writes the framework table.

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit import Panel

Panel.make("admin")
    .path("admin")
    .database_notifications(True)
    .database_notifications_using_almasix()
    .database_notifications_polling("30s")
```

| Method | Notes |
|--------|-------|
| `.database_notifications` | `True` / `False`, or a sequence of seeds |
| `.database_notifications_using_almasix` | Persist via Almasix `notifications` (recommended) |
| `.database_notifications_position` | `topbar` (default) or `sidebar` |
| `.database_notifications_polling` | `'30s'`, ms int, or `None` to disable |
| `.database_notifications_store` | Plug in any `DatabaseNotificationStore` |
| `.sqlite_notifications` | Optional stdlib SQLite file for tests / no-ORM apps |
| `.notification` | Append one seed (also enables the feature) |

![Orbit Database notifications enable (light)](/examples/light/notifications/database-notifications/enable.png)

![Orbit Database notifications enable (dark)](/examples/dark/notifications/database-notifications/enable.png)

## Sending database notifications

Use Orbit's fluent API. Pass the signed-in user (or any notifiable) so the row is scoped correctly. Set `is_event_dispatched=True` when you want an immediate refresh signal for the bell UI.

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

The same `notifications` rows are visible to Almasix helpers:

```python title="examples/list_inbox.py"
unread = await user.unread_notifications()
await user.mark_notifications_as_read()
```

When the bell is enabled, Orbit mounts **GET/POST** `{panel}/orbit-notifications`. The Alpine `orbitDatabaseNotifications` component polls that URL and posts mark-read updates. Rows include `created_at` and are listed **newest first**.

![Orbit Database notifications store (light)](/examples/light/notifications/database-notifications/sqlite.png)

![Orbit Database notifications store (dark)](/examples/dark/notifications/database-notifications/sqlite.png)

## Notifications deck

The bell dropdown lists **unread** notifications only. Use **View all** (or dispatch `open-modal` with `id: "database-notifications"`) to open the **notifications deck** — a right-hand sidebar with the full history, newest first, and infinite scroll as you reach the bottom.

Clicking a row in the dropdown or the deck opens a **detail modal** with the full title and body, and marks that notification as read.

## Position

Top bar (default) places the bell next to theme / user chrome. Sidebar nests it above the nav list.

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit import Panel

Panel.make("admin")
    .path("admin")
    .database_notifications(True)
    .database_notifications_using_almasix()
    .database_notifications_position("sidebar")
```

![Orbit Database notifications position (light)](/examples/light/notifications/database-notifications/position.png)

![Orbit Database notifications position (dark)](/examples/dark/notifications/database-notifications/position.png)

## Polling

The Alpine `orbitDatabaseNotifications` component polls on an interval (default **30s**). Pass `'15s'`, a millisecond int, or `None`.

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit import Panel

Panel.make("admin")
    .path("admin")
    .database_notifications(True)
    .database_notifications_using_almasix()
    .database_notifications_polling("15s")
```

Apps can still listen for `orbit:database-notifications-poll` / dispatch `orbit:database-notifications-refresh` to replace or refresh the list.

## Marking as read

Opening a notification in the detail modal marks it read. The deck and dropdown also expose **Mark all as read**. From Python, use the store:

```python title="app/orbit/notifications/mark_read.py"
from almasix.orbit.notifications import get_notifier

store = get_notifier().store
store.mark_read(notification_id, user=user)
store.mark_all_read(user=user)
```

Notification actions can set `.mark_as_read()` / `.mark_as_unread()` for toast/database footers. The detail modal can restore unread with **Mark unread**.

![Orbit Database notifications mark read (light)](/examples/light/notifications/database-notifications/mark-read.png)

![Orbit Database notifications mark read (dark)](/examples/dark/notifications/database-notifications/mark-read.png)

## Alternatives (tests and offline)

Unit tests can keep the default in-memory store. Apps without the Almasix ORM table can use `.sqlite_notifications("orbit-notifications.sqlite")` (stdlib SQLite, separate `orbit_notifications` schema). Prefer `.database_notifications_using_almasix()` for real applications.

Related: [Overview](/notifications/overview/), [Broadcast notifications](/notifications/broadcast-notifications/).
