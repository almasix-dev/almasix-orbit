---
title: Broadcast notifications
description: Live toasts — broadcast hub, /orbit-live polling, LiveNotifier, and orbit:broadcast.
---

## Introduction

**Broadcast notifications** deliver a toast in real time without waiting for a full page render. Use them when a background job finishes, an order ships, or any server-side event should pop a toast while the admin stays on the current page.

Orbit provides:

1. A fluent `.broadcast(...)` channel on `Notification`
2. A `BroadcastHub` that records payloads in-process (`MemoryBroadcastHub`) or fans them to a callback (`CallbackBroadcastHub`)
3. Panel `.live_broadcasts()` which mounts **GET** `{panel}/orbit-live` and binds the hub
4. Alpine `orbitLiveNotifications`, which polls that URL and dispatches the browser event `orbit:broadcast`

```python title="app/orbit/notifications/broadcast.py"
from almasix.orbit import Panel
from almasix.orbit.notifications import Notification

Panel.make("admin").path("admin").live_broadcasts(polling="2s")

Notification.make()
    .title("Deploy finished")
    .success()
    .body("v1.4.2 is live on production.")
    .broadcast(user)
```

![Orbit Broadcast notifications (light)](/examples/light/notifications/broadcast-notifications.png)

![Orbit Broadcast notifications (dark)](/examples/dark/notifications/broadcast-notifications.png)

## Sending broadcast notifications

`.broadcast(user=None)` sets the channel, enqueues on the notifier’s broadcast bag, and **publishes** to the process broadcast hub (the one `.live_broadcasts()` registered, or `Notifier.use_hub(...)`). `.to_broadcast()` only marks the channel for a later `.send()`.

```python title="app/orbit/notifications/broadcast_send.py"
from almasix.orbit.notifications import LiveNotifier, MemoryBroadcastHub, Notification, set_notifier

hub = MemoryBroadcastHub()
live = LiveNotifier().channel("orders").use_hub(hub)
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

Markup is `<div class="or-live-notifier" data-channels="…" data-orbit-live-url="…" x-data="orbitLiveNotifications">` around the usual toast host. The panel shell does this automatically when `.live_broadcasts()` is on.

![Orbit Broadcast live host (light)](/examples/light/notifications/broadcast-notifications/live-host.png)

![Orbit Broadcast live host (dark)](/examples/dark/notifications/broadcast-notifications/live-host.png)

## Broadcast hub

`MemoryBroadcastHub` keeps an in-process log. `CallbackBroadcastHub` wraps another hub (memory by default) and calls your function on every publish — use that to forward events to Redis, a queue, or a websocket server.

```python title="app/orbit/notifications/hub.py"
from almasix.orbit.notifications import CallbackBroadcastHub, MemoryBroadcastHub

hub = CallbackBroadcastHub(lambda event: print(event["title"]))
# or: MemoryBroadcastHub()
```

![Orbit Broadcast hub (light)](/examples/light/notifications/broadcast-notifications/hub.png)

![Orbit Broadcast hub (dark)](/examples/dark/notifications/broadcast-notifications/hub.png)

## Live endpoint

`.live_broadcasts()` registers **GET** `{panel}/orbit-live?since={cursor}`. The JSON payload is `{ "events": [...], "cursor": N }`. The Alpine host polls that URL (default **2s**) and turns each event into `orbit:broadcast`.

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit import Panel

Panel.make("admin")
    .path("admin")
    .live_broadcasts(polling="2s")
```

![Orbit Broadcast live endpoint (light)](/examples/light/notifications/broadcast-notifications/live-endpoint.png)

![Orbit Broadcast live endpoint (dark)](/examples/dark/notifications/broadcast-notifications/live-endpoint.png)

You can still dispatch `orbit:broadcast` yourself from any other transport:

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

That re-dispatches `orbit:notify` for the toast host — same shape as `OrbitNotification.send()`. Optional `channel` is filtered against `data-channels` when set.

## Panel setup notes

1. Keep the panel toast host enabled (`.notifications()` is on by default).
2. Call `.live_broadcasts()` so the shell wraps the toast host and mounts `/orbit-live`.
3. Send with `.broadcast()` from actions, jobs, or services.
4. For database rows that should appear immediately, prefer `.send_to_database(...)` plus the bell endpoint — see [Database notifications](/notifications/database-notifications/).

Related: [Overview](/notifications/overview/), [Database notifications](/notifications/database-notifications/).
