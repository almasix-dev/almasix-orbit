"""Testing helpers for flash notifications."""

from __future__ import annotations

from almasix.orbit.notifications.notification import Notification, get_notifier


def assert_notified(
    *,
    title: str | None = None,
    body: str | None = None,
    status: str | None = None,
) -> Notification:
    """Assert the default notifier flash bag contains a matching notification.

    Does **not** clear the bag — inspect with :meth:`Notifier.peek_flash` / ``flash()``.
    """
    notifier = get_notifier()
    items = notifier.peek_flash()
    for note in items:
        if title is not None and note._title != title:
            continue
        if body is not None and note._body != body:
            continue
        if status is not None and str(note._status) != status and note._status.value != status:
            continue
        return note
    details = [(n._title, n._body, str(n._status)) for n in items]
    raise AssertionError(
        f"Expected notification title={title!r} body={body!r} status={status!r}; "
        f"flash bag={details!r}"
    )


def assert_not_notified(
    *,
    title: str | None = None,
    body: str | None = None,
    status: str | None = None,
) -> None:
    """Assert no flash notification matches the given fields."""
    notifier = get_notifier()
    for note in notifier.peek_flash():
        if title is not None and note._title != title:
            continue
        if body is not None and note._body != body:
            continue
        if status is not None and str(note._status) != status and note._status.value != status:
            continue
        raise AssertionError(
            f"Did not expect notification title={title!r} body={body!r} status={status!r}; "
            f"found id={note.get_id()!r}"
        )


def reset_notifications() -> None:
    """Clear the process-default notifier bags (tests)."""
    get_notifier().clear()
