"""Notifications showcase — toast triggers, database bell seeds, broadcast demo."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.actions import Action
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.notifications import Notification
from almasix.orbit.tables import Table, TextColumn


class NotificationsOverviewResource(Resource):
    """Focused sample for notifications docs — flash toasts + live broadcast button."""

    model = type("NotifySample", (), {})
    slug = "notifications-overview"
    navigation_label = "Toast showcase"
    navigation_group = "Notifications"
    navigation_icon = "heroicon-o-bell"
    active_navigation_icon = "heroicon-s-bell"
    navigation_sort = 0
    record_title_attribute = "title"

    records: ClassVar[list[dict[str, Any]]] = [
        {
            "id": 1,
            "title": "Flash success",
            "note": "Header Success toast uses .success_notification.",
        },
        {
            "id": 2,
            "title": "Flash danger",
            "note": "Header Danger toast uses OrbitNotification JS client.",
        },
        {
            "id": 3,
            "title": "Broadcast bridge",
            "note": "Live button publishes to the panel broadcast hub.",
        },
    ]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("title").label("Title").required(),
                TextInput.make("note").label("Note"),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.heading("Notification samples")
            .description(
                "Fire success / danger toasts from the header. "
                "Check the bell for seeded database notifications. "
                "Live demo publishes through the panel broadcast hub "
                "(`Notification.broadcast()` + `/orbit-live` polling)."
            )
            .columns(
                [
                    TextColumn.make("title").searchable(),
                    TextColumn.make("note").label("Note"),
                ]
            )
            .header_actions(
                [
                    Action.make("toast_success")
                    .label("Success toast")
                    .icon("heroicon-o-check-circle")
                    .color("success")
                    .success_notification("Changes to the post have been saved.")
                    .success_notification_title("Saved successfully")
                    .action(lambda **_: None),
                    Action.make("toast_danger")
                    .label("Danger toast")
                    .icon("heroicon-o-x-circle")
                    .color("danger")
                    .extra_attributes(
                        {
                            "x-on:click": (
                                "new OrbitNotification()"
                                ".title('Could not save the post.')"
                                ".danger()"
                                ".body('Check the form and try again.')"
                                ".send()"
                            ),
                        }
                    )
                    .action(lambda **_: None),
                    Action.make("broadcast_demo")
                    .label("Live broadcast")
                    .icon("heroicon-o-signal")
                    .color("info")
                    .extra_attributes(
                        {
                            "x-on:click": (
                                "$dispatch('orbit:notify', {"
                                "title: 'Deploy finished', "
                                "body: 'v1.4.2 is live on production.', "
                                "status: 'success'"
                                "})"
                            ),
                        }
                    )
                    .action(
                        lambda **_: Notification.make()
                        .title("Deploy finished")
                        .success()
                        .body("v1.4.2 is live on production.")
                        .broadcast()
                    ),
                ]
            )
            .records(cls.get_records())
            .paginated(False)
        )
