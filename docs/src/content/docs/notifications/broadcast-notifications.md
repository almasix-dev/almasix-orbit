---
title: Broadcast notifications
description: Live / broadcast toasts — LiveNotifier, channels, and the orbit:broadcast client event.
---

## Introduction

**Broadcast notifications** deliver a toast in real time without waiting for a full page render. Use them when a background job finishes, an order ships, or any server-side event should pop a toast while the admin stays on the current page.

Orbit provides:

1. A fluent `.broadcast(...)` channel on `Notification`
2. A `LiveNotifier` adapter that records channel names for the client
3. An Alpine `orbitLiveNotifications` host that listens for the browser event `orbit:broadcast`

Wire your own transport (websockets, SSE, or a push service) to dispatch that event — Orbit stays transport-agnostic.

```python title="app/orbit/notifications/broadcast.py"
from almasix.orbit.notifications import Notification

Notification.make()
    .title("Deploy finished")
    .success()
    .body("v1.4.2 is live on production.")
    .broadcast(user)
```

![Orbit Broadcast notifications (light)](/examples/light/notifications/broadcast-notifications.png)

![Orbit Broadcast notifications (dark)](/examples/dark/notifications/broadcast-notifications.png)

## Sending broadcast notifications

`.broadcast(user=None)` sets the channel and enqueues on the notifier’s broadcast bag. `.to_broadcast()` only marks the channel for a later `.send()`.

```python title="app/orbit/notifications/broadcast_send.py"
from almasix.orbit.notifications import LiveNotifier, Notification, set_notifier

live = LiveNotifier().channel("App.Models.User.1")
set_notifier(live)

Notification.make()
    .title("Processing complete")
    .success()
    .broadcast(user)
```

![Orbit Broadcast send (light)](/examples/light/notifications/broadcast-notifications/send.png)

![Orbit Broadcast send (dark)](/examples/dark/notifications/broadcast-notifications/send.png)

Inspect queued items with `notifier.broadcast_queue()` in tests.

## Live notifier host

`LiveNotifier.render_live()` wraps the toast host and records channel names for the client:

```python title="app/orbit/notifications/live_host.py"
from almasix.orbit.notifications import LiveNotifier

html = (
    LiveNotifier()
    .channel("orders")
    .channel("App.Models.User.1")
    .render_live()
)
```

Markup is `<div class="or-live-notifier" data-channels="…" x-data="orbitLiveNotifications">` around the usual toast host.

![Orbit Broadcast live host (light)](/examples/light/notifications/broadcast-notifications/live-host.png)

![Orbit Broadcast live host (dark)](/examples/dark/notifications/broadcast-notifications/live-host.png)

## Client bridge

From your websocket or SSE callback, dispatch a `CustomEvent`. Optional `channel` is filtered against `data-channels` when set.

```js title="resources/js/broadcast-bridge.js"
window.dispatchEvent(
  new CustomEvent("orbit:broadcast", {
    detail: {
      channel: "orders",
      title: "Order shipped",
      body: "#1042 left the warehouse.",
      status: "success",
    },
  }),
);
```

That re-dispatches `orbit:notify` for the toast host — same shape as `OrbitNotification.send()`.

## Panel setup notes

1. Keep the panel toast host enabled (`.notifications()` is on by default).
2. Optionally mount `LiveNotifier.render_live()` via a render hook if you need channel filtering.
3. Point your broadcast driver at `orbit:broadcast` (or call `new OrbitNotification()…send()` from the client).
4. For database rows that should appear immediately, prefer `.send_to_database(..., is_event_dispatched=True)` and refresh the bell — see [Database notifications](/notifications/database-notifications/).

Related: [Overview](/notifications/overview/), [Database notifications](/notifications/database-notifications/).
