"""Tests for almasix.orbit.notifications (Filament 5 parity)."""

from __future__ import annotations

import pytest
from almasix.orbit.notifications import (
    Alignment,
    InMemoryDatabaseNotificationStore,
    LiveNotifier,
    Notification,
    NotificationAction,
    Notifications,
    NotificationStatus,
    Notifier,
    VerticalAlignment,
    assert_not_notified,
    assert_notified,
    get_notifier,
    notification_from_dict,
    reset_broadcast_hub,
    reset_notifications,
    reset_process_notifier,
    set_notifier,
)
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.users import OrbitUser, PanelNotification


@pytest.fixture(autouse=True)
def _clean_notifier() -> None:
    reset_process_notifier()
    reset_notifications()
    reset_broadcast_hub()
    Notifications.reset()
    yield
    reset_process_notifier()
    reset_broadcast_hub()
    Notifications.reset()


def test_notification_fluent_api_and_render() -> None:
    n = (
        Notification.make(title="Hello")
        .body_text("World")
        .success()
        .seconds(3)
        .persistent_mode()
    )
    assert n.status == NotificationStatus.SUCCESS
    assert n.duration == 3000
    assert n.persistent is True
    assert n.to_dict()["title"] == "Hello"
    assert n.icon == "heroicon-o-check-circle"
    html = n.render()
    assert "or-notification-success" in html and "World" in html
    assert 'data-persistent="true"' in html
    assert "or-notification-dismiss" in html

    assert Notification.make(title="w").warning().status == NotificationStatus.WARNING
    assert Notification.make(title="d").danger().status == NotificationStatus.DANGER
    assert Notification.make(title="i").info().status == NotificationStatus.INFO
    assert Notification.make(title="db").to_database().channel == "database"
    assert Notification.make(title="bc").to_broadcast().channel == "broadcast"
    assert Notification.make(title="t").render()  # no body

    custom = Notification.make("greeting").title("Hi")
    assert custom.get_id() == "greeting"
    assert custom.title == "Hi"
    assert Notification.make("Post saved").title == "Post saved"
    assert Notification.make(id="x", title="Y").get_id() == "x"

    timed = Notification.make(title="T").duration(5000).color("success").icon("heroicon-o-bell")
    assert timed.duration == 5000
    assert timed.color == "success"
    assert "data-duration=\"5000\"" in timed.render()


def test_notification_actions() -> None:
    action = (
        NotificationAction.make("view")
        .button()
        .label("View")
        .url("/posts/1", should_open_in_new_tab=True)
        .color("gray")
        .close()
        .mark_as_read()
    )
    html = action.render()
    assert 'href="/posts/1"' in html
    assert 'target="_blank"' in html
    assert 'data-close="true"' in html
    assert action.to_dict()["mark_as_read"] is True

    dispatch = (
        NotificationAction.make("undo")
        .dispatch("undoEditingPost", [1])
        .dispatch_self("selfEvt")
    )
    assert dispatch.to_dict()["dispatch_self"] is True
    to_comp = NotificationAction.make("x").dispatch_to("comp", "evt", [2])
    assert to_comp.to_dict()["dispatch_to"] == "comp"

    note = Notification.make(title="Saved").actions(
        [
            action,
            {"name": "close", "button": True, "close": True, "label": "Close"},
        ]
    )
    assert "or-notification-actions" in note.render()
    assert len(note.actions) == 2


def test_notifier_channels_store_and_flash() -> None:
    store = InMemoryDatabaseNotificationStore()
    notifier = Notifier(database_store=store)
    notifier.send(Notification.make(title="flash").success())
    notifier.send(Notification.make(title="db").to_database())
    notifier.send(Notification.make(title="bc").to_broadcast())
    assert len(notifier.database()) == 1
    assert len(notifier.broadcast_queue()) == 1
    assert len(store.get_for_user()) == 1
    flash_html = notifier.render_flash()
    assert "or-notifications" in flash_html and "flash" in flash_html
    assert "x-for=\"n in notifications\"" in flash_html
    assert notifier.flash() == []

    user = OrbitUser.make().name("Ada").email("ada@test")
    notifier.send_to_database(
        Notification.make(title="For Ada"),
        user=user,
        is_event_dispatched=True,
    )
    assert len(notifier.database_events()) == 1
    rows = store.get_for_user(user)
    assert len(rows) == 1
    store.mark_read(rows[0].id, user=user)
    assert store.get_for_user(user)[0].read is True
    store.mark_unread(rows[0].id, user=user)
    assert store.get_for_user(user)[0].read is False
    store.mark_all_read(user=user)
    assert store.get_for_user(user)[0].read is True
    assert rows[0].to_dict()["title"] == "For Ada"


def test_default_notifier_send_and_testing_helpers() -> None:
    Notification.make(title="Saved").success().send()
    assert_notified(title="Saved", status="success")
    assert_not_notified(title="Missing")
    with pytest.raises(AssertionError):
        assert_notified(title="Nope")
    with pytest.raises(AssertionError):
        assert_not_notified(title="Saved")

    Notification.make(title="DB").send_to_database()
    assert get_notifier().database()[0].title == "DB"
    Notification.make(title="BC").broadcast()
    assert get_notifier().broadcast_queue()[0].title == "BC"

    local = Notifier()
    token = set_notifier(local)
    Notification.make(title="Ctx").send()
    assert local.peek_flash()[0].title == "Ctx"
    set_notifier(None)
    del token


def test_live_notifier_and_alignment() -> None:
    live = LiveNotifier().channel("orders").channel("users")
    assert live.get_channels() == ["orders", "users"]
    live.send(Notification.make(title="Order shipped").success())
    html = live.render_live()
    assert "or-live-notifier" in html
    assert 'data-channels="orders,users"' in html
    assert "Order shipped" in html

    Notifications.alignment(Alignment.START)
    Notifications.vertical_alignment(VerticalAlignment.END)
    assert "or-notifications-align-start" in Notifications.host_classes()
    assert "or-notifications-valign-end" in Notifications.host_classes()
    host = Notifier().render_toast_host(include_flash=False)
    assert "or-notifications-align-start" in host


def test_notification_from_dict() -> None:
    note = notification_from_dict(
        {
            "id": "n1",
            "title": "Hi",
            "body": "There",
            "status": "warning",
            "icon": "heroicon-o-bell",
            "duration": 1000,
            "persistent": True,
            "actions": [{"name": "ok", "button": True}],
            "channel": "database",
            "read": True,
        }
    )
    assert note.get_id() == "n1"
    assert note.status == NotificationStatus.WARNING
    assert note.read is True


def test_panel_database_notifications_and_toast_host() -> None:
    panel = (
        Panel.make("admin")
        .path("admin")
        .notifications()
        .database_notifications(True)
        .database_notifications_polling("15s")
        .notification(PanelNotification.make("Ping").body("Pong").status("success"))
    )
    assert panel._polling_ms() == 15000
    shell = panel.render_shell("<p>x</p>", user=OrbitUser.default())
    assert "or-notifications" in shell
    assert "orbitNotifications" in shell
    assert "or-notify-btn" in shell
    assert "orbitDatabaseNotifications" in shell
    assert "Mark all as read" in shell
    assert "Ping" in shell or "data-notifications=" in shell

    side = (
        Panel.make("side")
        .path("side")
        .database_notifications(True, position="sidebar")
        .database_notifications_polling(None)
    )
    assert side._polling_ms() is None
    html = side.render_shell("<p>x</p>", user=OrbitUser.default())
    assert "or-sidebar-notifications" in html

    off = Panel.make("off").path("off").notifications(False).database_notifications(True)
    assert "or-notify-btn" not in off.render_shell("<p>x</p>")
    assert "orbitNotifications" not in off.render_shell("<p>x</p>")

    seeded = Panel.make("s").path("s").database_notifications(
        [{"title": "N", "body": "B"}, PanelNotification.make("T")]
    )
    assert seeded._database_notifications_enabled is True
    assert len(seeded._database_notifications) == 2

    # Polling parser branches
    p = Panel.make("poll").path("poll").database_notifications(True)
    p.database_notifications_polling(0)
    assert p._polling_ms() is None
    p.database_notifications_polling("250ms")
    assert p._polling_ms() == 250
    p.database_notifications_polling("badms")
    assert p._polling_ms() is None
    p.database_notifications_polling("bads")
    assert p._polling_ms() is None
    p.database_notifications_polling("4000")
    assert p._polling_ms() == 4000
    p.database_notifications_polling("nope")
    assert p._polling_ms() is None
    p.database_notifications_polling("none")
    assert p._polling_ms() is None
    p.database_notifications_position("TOPBAR")
    assert p._database_notifications_position == "topbar"

    # Topbar disabled → bell falls back to sidebar
    no_top = (
        Panel.make("nt")
        .path("nt")
        .topbar(False)
        .database_notifications(True)
    )
    assert "or-sidebar-notifications" in no_top.render_shell("<p>x</p>")

    rich = (
        PanelNotification.make("R")
        .body("B")
        .status("danger")
        .icon("heroicon-o-bell")
        .id("nid")
        .read()
    )
    assert rich.to_dict()["read"] is True
    assert rich.to_dict()["id"] == "nid"
    assert rich.to_dict()["icon"] == "heroicon-o-bell"


def test_action_and_store_edge_branches() -> None:
    btn = NotificationAction.make("ok").button().mark_as_unread()
    assert "<button" in btn.render()
    assert btn.get_label() == "Ok"
    assert btn.get_name() == "ok"
    assert 'data-mark-as-unread="true"' in btn.render()
    colored = NotificationAction.make("c").color("gray")
    assert "or-notification-action-gray" in colored.render()
    only_tab = NotificationAction.make("link").url("/a").open_url_in_new_tab()
    assert 'target="_blank"' in only_tab.render()
    dispatched = NotificationAction.make("d").dispatch("undo").close().mark_as_read()
    dhtml = dispatched.render()
    assert 'data-dispatch="undo"' in dhtml
    assert 'data-close="true"' in dhtml
    assert 'data-mark-as-read="true"' in dhtml

    store = InMemoryDatabaseNotificationStore()
    store.save({"title": "X"}, user=object())
    assert store.get_for_user()[0].user_key is not None

    note = Notification.make()
    with pytest.raises(AttributeError):
        _ = note.not_a_real_attr
    # Alias present but private missing → AttributeError
    del note.__dict__["_channel"]
    with pytest.raises(AttributeError):
        _ = note.channel
    note.foo = "bar"  # type: ignore[attr-defined]
    assert note.foo == "bar"  # type: ignore[attr-defined]
    note.set_id("custom")
    assert note.get_id() == "custom"
    both = Notification.make("gid", title="T")
    assert both.get_id() == "gid" and both.title == "T"

    n = Notification.make(title="A").icon_color("gray").color("primary").status("info")
    assert n.icon_color == "gray"
    n2 = Notification.make(title="B").actions(
        [
            {
                "name": "x",
                "label": "X",
                "button": True,
                "url": "/x",
                "open_url_in_new_tab": True,
                "dispatch": "evt",
                "dispatch_payload": [1],
                "close": True,
                "color": "gray",
                "mark_as_read": True,
                "mark_as_unread": True,
            }
        ]
    )
    assert n2.actions[0].to_dict()["url"] == "/x"

    notifier = Notifier()
    assert notifier.store is not None
    notifier.use_store(store)
    notifier.send(Notification.make(title="via-db").to_database())
    notifier.broadcast_send(Notification.make(title="via-bc"), user=OrbitUser.default())
    assert len(notifier.database()) == 1
    assert len(notifier.broadcast_queue()) == 1
    notifier.clear()

    class BareStore:
        def __init__(self) -> None:
            self.rows: list = []

        def save(self, payload, *, user=None):
            from almasix.orbit.notifications.store import StoredNotification

            row = StoredNotification(id="1", title=str(payload.get("title") or "t"))
            self.rows.append(row)
            return row

        def mark_read(self, notification_id, *, user=None) -> None:
            return None

        def mark_unread(self, notification_id, *, user=None) -> None:
            return None

        def mark_all_read(self, *, user=None) -> None:
            return None

        def get_for_user(self, user=None):
            return list(self.rows)

    bare = Notifier(database_store=BareStore())  # type: ignore[arg-type]
    bare.send(Notification.make(title="z").success())
    bare.clear()  # store has no clear()
    assert bare.peek_flash() == []

    reset_notifications()
    Notification.make(title="Same").body("A").info().send()
    Notification.make(title="Same").body("B").success().send()
    Notification.make(title="Same").body("B").warning().send()
    assert_notified(title="Same", body="B", status="warning")
    assert_not_notified(title="Same", body="B", status="danger")
    assert_not_notified(title="Same", body="missing")

    # Fresh process notifier when global is cleared
    import almasix.orbit.notifications.notification as notif_mod

    set_notifier(None)
    notif_mod._process_notifier = None
    fresh = get_notifier()
    assert fresh is not None
    assert Notification.make().channel == "flash"

    # URL action without new-tab (branch) then with new-tab
    plain = NotificationAction.make("p").url("/plain")
    assert 'target="_blank"' not in plain.render()
    tabbed = NotificationAction.make("t").url("/t").open_url_in_new_tab(True)
    html = tabbed.render()
    assert 'target="_blank"' in html and "noopener" in html

    hydrated = notification_from_dict(
        {
            "title": "Only",
            "body": "Txt",
            "icon": "heroicon-o-bell",
            "icon_color": "success",
            "color": "success",
            "status": "success",
            "actions": [{"name": "a"}],
        }
    )
    assert hydrated.title == "Only"
    assert hydrated.body == "Txt"
    empty = notification_from_dict({})
    assert empty.get_id()
    rebuilt = notification_from_dict(
        {
            "id": "z1",
            "title": "Z",
            "actions": [{"name": "again", "button": True}],
            "duration": 100,
            "persistent": True,
            "read": True,
            "channel": "flash",
        }
    )
    assert rebuilt.duration == 100
    assert rebuilt.persistent is True
