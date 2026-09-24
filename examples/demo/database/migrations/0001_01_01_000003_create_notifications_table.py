"""Create the notifications table — the database notification channel's inbox.

Generated via ``smith notifications:table`` (Almasix). Orbit's panel bell uses
this same table through ``.database_notifications_using_almasix()``.
"""

from __future__ import annotations

from almasix.orm import Blueprint, Migration, Schema


class CreateNotificationsTable(Migration):
    """CreateNotificationsTable."""

    async def up(self) -> None:
        await Schema.create_if_not_exists("notifications", self.notifications)

    async def down(self) -> None:
        await Schema.drop_if_exists("notifications")

    def notifications(self, table: Blueprint) -> None:
        table.uuid("id").primary()
        table.string("type")
        table.string("notifiable_type")
        table.string("notifiable_id")
        table.text("data")
        table.timestamp("read_at").nullable()
        table.timestamps()
        table.index(["notifiable_type", "notifiable_id"])
