"""SQLite store, broadcast hub, and panel live/database notification endpoints."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

import pytest
from almasix.orbit.notifications import (
    CallbackBroadcastHub,
    InMemoryDatabaseNotificationStore,
    LiveNotifier,
    MemoryBroadcastHub,
    Notification,
    Notifier,
    SqliteNotificationStore,
    get_broadcast_hub,
    get_notifier,
    reset_broadcast_hub,
    reset_notifications,
    reset_process_notifier,
    set_broadcast_hub,
)
from almasix.orbit.notifications.store import _decode_json
from almasix.orbit.panels.notification_routes import (
    handle_database_notifications,
    handle_live_broadcasts,
    panel_live_url,
    panel_notifications_url,
    read_json_body,
)
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.users import OrbitUser, PanelNotification


@pytest.fixture(autouse=True)
def _clean_notifier() -> None:
    reset_process_notifier()
    reset_notifications()
    reset_broadcast_hub()
    yield
    reset_process_notifier()
    reset_broadcast_hub()


def run(coro: Any) -> Any:
    return asyncio.run(coro) if asyncio.iscoroutine(coro) else coro


class _ExplodingStore:
    def save(self, payload: dict[str, Any], *, user: Any = None) -> None:
        raise RuntimeError("save failed")

    def mark_read(self, notification_id: str, *, user: Any = None) -> None:
        raise RuntimeError("read failed")

    def mark_unread(self, notification_id: str, *, user: Any = None) -> None:
        raise RuntimeError("unread failed")

    def mark_all_read(self, *, user: Any = None) -> None:
        raise RuntimeError("all failed")

    def get_for_user(self, user: Any = None) -> list[Any]:
        raise RuntimeError("get failed")


def test_decode_json_branches() -> None:
    assert _decode_json(None, []) == []
    assert _decode_json("", {}) == {}
    assert _decode_json(12, []) == []
    assert _decode_json("not-json", []) == []
    assert _decode_json("[1]", []) == [1]
    assert _decode_json("{}", []) == []
    assert _decode_json('{"a":1}', {}) == {"a": 1}
    assert _decode_json("[1]", {}) == {}
    assert _decode_json("1", 0) == 1


def test_sqlite_store_round_trip_and_user_scoping(tmp_path: Any) -> None:
    path = str(tmp_path / "notes.sqlite")
    store = SqliteNotificationStore(path)
    ada = OrbitUser.make().name("Ada").email("ada@test")
    store.save(
        {
            "id": "welcome",
            "title": "Hello",
            "body": "World",
            "status": "success",
            "icon": "heroicon-o-bell",
            "icon_color": "success",
            "color": "success",
            "actions": [{"name": "ok"}],
            "data": {"k": "v"},
            "read": False,
        },
        user=ada,
    )
    store.save({"title": "Broken", "actions": "nope", "data": ["x"]})
    rows = store.get_for_user(ada)
    assert len(rows) == 1
    assert rows[0].title == "Hello"
    assert rows[0].actions[0]["name"] == "ok"
    store.mark_read("welcome", user=ada)
    assert store.get_for_user(ada)[0].read is True
    store.mark_unread("welcome", user=ada)
    assert store.get_for_user(ada)[0].read is False
    store.mark_read("welcome", user=OrbitUser.make().email("other@test"))
    assert store.get_for_user(ada)[0].read is False
    store.mark_all_read(user=ada)
    assert store.get_for_user(ada)[0].read is True
    store.mark_unread("welcome")
    store.mark_read("welcome")
    store.mark_all_read()
    assert store.get_for_user()[0].read is True
    store.clear()
    assert store.get_for_user() == []
    store.close()


def test_sqlite_store_decodes_corrupt_json() -> None:
    store = SqliteNotificationStore(":memory:")
    store.save({"id": "x", "title": "T", "actions": [1], "data": {"a": 1}})
    store._conn.execute(
        "UPDATE orbit_notifications SET actions = ?, data = ? WHERE id = ?",
        ("{", "[1]", "x"),
    )
    store._conn.commit()
    row = store.get_for_user()[0]
    assert row.actions == []
    assert row.data == {}
    store._conn.execute(
        "INSERT OR REPLACE INTO orbit_notifications "
        "(id, title, body, status, icon, icon_color, color, actions, read, user_key, data) "
        "VALUES ('blank', '', NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL)"
    )
    store._conn.commit()
    blank = next(r for r in store.get_for_user() if r.id == "blank")
    assert blank.title == "Notification"
    assert blank.status == "info"
    store.close()


def test_memory_and_callback_hubs() -> None:
    hub = MemoryBroadcastHub()
    seen: list[dict[str, Any]] = []

    def boom(_event: dict[str, Any]) -> None:
        raise RuntimeError("sub")

    unsub = hub.subscribe(seen.append)
    hub.subscribe(boom)
    hub.publish({"title": "A"})
    hub.publish({"title": "B"})
    assert [e["title"] for e in hub.since(0)] == ["A", "B"]
    assert hub.since(1)[0]["title"] == "B"
    assert hub.since(-3)[0]["title"] == "A"
    assert hub.since("bad")[0]["title"] == "A"  # type: ignore[arg-type]
    unsub()
    unsub()
    pulled = hub.pull()
    assert len(pulled) == 2
    assert hub.since(0) == []

    outer: list[dict[str, Any]] = []
    wrapped = CallbackBroadcastHub(outer.append, inner=hub)
    wrapped.publish({"title": "C"})
    assert wrapped.since(0)[0]["title"] == "C"
    boom_hub = CallbackBroadcastHub(boom)
    boom_hub.publish({"title": "D"})
    assert boom_hub.pull()[0]["title"] == "D"
    off = boom_hub.subscribe(outer.append)
    off()
    set_broadcast_hub(hub)
    assert get_broadcast_hub() is hub
    reset_broadcast_hub()
    assert get_broadcast_hub() is None


def test_notifier_publishes_to_hub() -> None:
    hub = MemoryBroadcastHub()
    notifier = Notifier().use_hub(hub)
    note = Notification.make(title="Live").success()
    notifier.broadcast_send(note, user=OrbitUser.default())
    assert hub.since(0)[0]["title"] == "Live"
    assert hub.since(0)[0]["user_key"]

    class BoomHub:
        def publish(self, event: dict[str, Any]) -> None:
            raise RuntimeError("nope")

    Notifier().use_hub(BoomHub()).broadcast_send(Notification.make(title="X"))

    set_broadcast_hub(hub)
    Notification.make(title="Global").broadcast()
    assert any(e["title"] == "Global" for e in hub.since(0))

    import almasix.orbit.notifications.notification as notif_mod

    def _raise() -> None:
        raise RuntimeError("hub missing")

    notif_mod.get_broadcast_hub = _raise  # type: ignore[method-assign]
    try:
        Notifier().broadcast_send(Notification.make(title="NoHub"))
    finally:
        notif_mod.get_broadcast_hub = get_broadcast_hub  # type: ignore[method-assign]


def test_live_notifier_render_attrs() -> None:
    html = (
        LiveNotifier()
        .channel("orders")
        .use_hub(MemoryBroadcastHub())
        .live_url("/admin/orbit-live")
        .polling(2000)
        .render_live()
    )
    assert 'data-orbit-live-url="/admin/orbit-live"' in html
    assert 'data-polling="2000"' in html
    assert 'data-channels="orders"' in html
    bare = LiveNotifier().live_url(None).polling(None).render_live()
    assert "data-orbit-live-url" not in bare


def test_panel_sqlite_and_live_broadcasts(tmp_path: Any) -> None:
    path = str(tmp_path / "panel.sqlite")
    panel = (
        Panel.make("admin")
        .path("admin")
        .database_notifications(
            [PanelNotification.make("Seed").id("seed-1").body("Hi")]
        )
        .sqlite_notifications(path)
        .live_broadcasts(polling="2s")
    )
    assert panel.database_notifications_enabled()
    assert panel.live_broadcasts_enabled()
    assert panel.notifications_url() == "/admin/orbit-notifications"
    assert panel.live_url() == "/admin/orbit-live"
    store = panel.get_notification_store()
    assert isinstance(store, SqliteNotificationStore)
    assert any(row.id == "seed-1" for row in store.get_for_user())
    panel.notification({"id": "extra", "title": "Extra"})
    assert any(row.id == "extra" for row in store.get_for_user())

    user = OrbitUser.default()
    shell = panel.render_shell("<p>x</p>", user=user)
    assert "data-orbit-notifications-url=" in shell
    assert "or-live-notifier" in shell
    assert 'data-orbit-live-url="/admin/orbit-live"' in shell

    panel.live_broadcasts(False)
    assert panel.live_broadcasts_enabled() is False
    hub = MemoryBroadcastHub()
    panel.live_broadcasts(hub, polling=0)
    assert panel.get_broadcast_hub() is hub
    assert panel._live_polling_ms() is None

    quiet = Panel.make("quiet").path("/").sqlite_notifications(":memory:")
    assert quiet.database_notifications_enabled()
    assert panel_live_url(quiet) == "/orbit-live"
    assert panel_notifications_url(None) == "/orbit-notifications"


def test_panel_store_exception_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    exploding = _ExplodingStore()
    panel = Panel.make("x").path("x").database_notifications([{"title": "A", "id": "a"}])
    panel.database_notifications_store(exploding)
    panel.notification({"title": "B", "id": "b"})
    html = panel.render_shell("<p>x</p>", user=OrbitUser.default())
    assert "or-notify-btn" in html

    Panel.make("z").path("z").database_notifications_store(None)
    empty = SimpleNamespace(
        save=lambda payload, user=None: None,
        get_for_user=lambda user=None: [],
    )
    Panel.make("e").path("e").database_notifications([{"title": "Seed"}]).database_notifications_store(
        empty
    ).render_shell("<p>x</p>", user=OrbitUser.default())
    kept = Panel.make("keep").path("k").live_broadcasts()
    first = kept.get_broadcast_hub()
    kept.live_broadcasts(True)
    assert kept.get_broadcast_hub() is first

    def _boom() -> None:
        raise RuntimeError("notifier")

    monkeypatch.setattr("almasix.orbit.notifications.get_notifier", _boom)
    Panel.make("y").path("y").database_notifications_store(InMemoryDatabaseNotificationStore())


def test_handle_live_and_database_payloads() -> None:
    panel = Panel.make("p").path("admin").database_notifications([{"title": "Seed", "id": "s"}])
    empty = handle_live_broadcasts(panel, since="nope")
    assert empty["events"] == [] and empty["cursor"] == 0
    assert handle_live_broadcasts(panel, since=-4)["cursor"] == 0

    class BadHub:
        def since(self, cursor: int = 0) -> list[dict[str, Any]]:
            raise RuntimeError("since")

    panel._broadcast_hub = BadHub()
    assert handle_live_broadcasts(panel, since=1)["events"] == []

    class NoSince:
        pass

    panel._broadcast_hub = NoSince()
    assert handle_live_broadcasts(panel, since=0)["events"] == []

    class BoomPanel:
        def get_broadcast_hub(self) -> None:
            raise RuntimeError("hub")

        _broadcast_hub = None

    assert handle_live_broadcasts(BoomPanel(), since=0)["events"] == []

    class BareLive:
        _broadcast_hub = None

    assert handle_live_broadcasts(BareLive(), since=0)["events"] == []

    hub = MemoryBroadcastHub()
    hub.publish({"title": "Ping"})
    live = Panel.make("live").path("admin").live_broadcasts(hub)
    payload = handle_live_broadcasts(live, since=0)
    assert payload["events"][0]["title"] == "Ping"

    seeds = handle_database_notifications(panel)
    assert seeds["notifications"][0]["title"] == "Seed"

    store = InMemoryDatabaseNotificationStore()
    store.save({"id": "n1", "title": "Stored"})
    panel.database_notifications_store(store)
    listed = handle_database_notifications(panel, method="GET")
    assert listed["notifications"][0]["id"] == "n1"
    handle_database_notifications(
        panel, method="POST", payload={"id": "n1", "read": True}
    )
    assert store.get_for_user()[0].read is True
    handle_database_notifications(
        panel, method="POST", payload={"id": "n1", "read": False}
    )
    assert store.get_for_user()[0].read is False
    handle_database_notifications(panel, method="POST", payload={"all": True})
    assert store.get_for_user()[0].read is True
    assert handle_database_notifications(panel, method="POST", payload={})["ok"] is True

    class BareDb:
        _database_notification_store = None
        _database_notifications = [{"title": "Bare"}]

    assert handle_database_notifications(BareDb())["notifications"][0]["title"] == "Bare"

    class BoomGet:
        def get_notification_store(self) -> None:
            raise RuntimeError("store")

        _database_notification_store = None
        _database_notifications = [{"title": "Fallback"}]

    assert handle_database_notifications(BoomGet())["notifications"][0]["title"] == "Fallback"

    exploding = _ExplodingStore()
    panel.database_notifications_store(exploding)
    assert handle_database_notifications(
        panel, method="POST", payload={"all": True}
    )["ok"] is True
    assert handle_database_notifications(
        panel, method="POST", payload={"id": "n1"}
    )["ok"] is True


def test_read_json_body_shapes() -> None:
    assert run(read_json_body(None)) == {}
    assert run(read_json_body(SimpleNamespace(json=lambda: {"a": 1}))) == {"a": 1}
    assert run(read_json_body(SimpleNamespace(json=lambda: ["no"]))) == {}

    async def _async_json() -> dict[str, int]:
        return {"b": 2}

    assert run(read_json_body(SimpleNamespace(json=_async_json))) == {"b": 2}

    def _raise() -> dict[str, Any]:
        raise RuntimeError("json")

    assert run(read_json_body(SimpleNamespace(json=_raise))) == {}
    assert run(read_json_body(SimpleNamespace(body=b'{"c":3}'))) == {"c": 3}
    assert run(read_json_body(SimpleNamespace(body='{"d":4}'))) == {"d": 4}
    assert run(read_json_body(SimpleNamespace(body=b"{"))) == {}
    assert run(read_json_body(SimpleNamespace(body=b"[1]"))) == {}
    assert run(read_json_body(SimpleNamespace(body=b""))) == {}
    assert run(read_json_body(SimpleNamespace())) == {}


def test_mount_panel_registers_notification_routes() -> None:
    from almasix.orbit.panels.routing import mount_panel
    from almasix.routing.router import Router

    panel = (
        Panel.make("admin")
        .path("admin")
        .middleware([], replace=True)
        .database_notifications(True)
        .live_broadcasts()
    )
    router = Router()
    mount_panel(router, panel)
    uris = [str(r.uri or "") for r in router.routes]
    assert any(u.endswith("orbit-notifications") for u in uris)
    assert any(u.endswith("orbit-live") for u in uris)

    db_route = next(r for r in router.routes if str(r.uri or "").endswith("orbit-notifications"))
    live_route = next(r for r in router.routes if str(r.uri or "").endswith("orbit-live"))

    class _Req:
        def __init__(self, *, method: str = "GET", since: str = "0", payload: dict | None = None) -> None:
            self.method = method
            self.query_params = {"since": since}
            self._payload = payload or {}

        def json(self) -> dict:
            return self._payload

    get_body = run(db_route.action(_Req()))
    content = getattr(get_body, "body", getattr(get_body, "content", get_body))
    raw = content.encode() if isinstance(content, str) else bytes(content)
    assert b"notifications" in raw

    post_body = run(db_route.action(_Req(method="POST", payload={"all": True})))
    post_raw = getattr(post_body, "body", getattr(post_body, "content", post_body))
    post_bytes = post_raw.encode() if isinstance(post_raw, str) else bytes(post_raw)
    assert b"ok" in post_bytes

    panel.get_broadcast_hub().publish({"title": "FromRoute"})
    live_body = run(live_route.action(_Req(since="0")))
    live_raw = getattr(live_body, "body", getattr(live_body, "content", live_body))
    live_bytes = live_raw.encode() if isinstance(live_raw, str) else bytes(live_raw)
    assert b"FromRoute" in live_bytes

    get_notifier().use_store(panel.get_notification_store() or InMemoryDatabaseNotificationStore())
