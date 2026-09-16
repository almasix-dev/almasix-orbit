"""Tests for almasix.orbit.notifications."""

from __future__ import annotations

from almasix.orbit.notifications.notification import Notification, NotificationStatus, Notifier


def test_notification_channels_and_render() -> None:
    n = (
        Notification.make("Hello")
        .body_text("World")
        .success()
        .seconds(3)
        .persistent_mode()
    )
    assert n.status == NotificationStatus.SUCCESS
    assert n.duration == 3000
    assert n.persistent is True
    assert n.to_dict()["title"] == "Hello"
    html = n.render()
    assert "or-notification-success" in html and "World" in html

    assert Notification.make("w").warning().status == NotificationStatus.WARNING
    assert Notification.make("d").danger().status == NotificationStatus.DANGER
    assert Notification.make("i").info().status == NotificationStatus.INFO
    assert Notification.make("db").send_to_database().channel == "database"
    assert Notification.make("bc").broadcast().channel == "broadcast"
    assert Notification.make("t").render()  # no body


def test_notifier() -> None:
    notifier = Notifier()
    notifier.send(Notification.make("flash").success())
    notifier.send(Notification.make("db").send_to_database())
    notifier.send(Notification.make("bc").broadcast())
    assert len(notifier.database()) == 1
    assert len(notifier.broadcast_queue()) == 1
    flash_html = notifier.render_flash()
    assert "or-notifications" in flash_html and "flash" in flash_html
    assert notifier.flash() == []
