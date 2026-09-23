"""Create ``orbit_notifications`` in the app SQLite database.

Orbit's SqliteNotificationStore also runs CREATE IF NOT EXISTS; this migration
makes the bell table a first-class part of the demo schema (same file as users
and the catalog).
"""

from __future__ import annotations

from almasix.orm import Blueprint, Migration, Schema


class CreateOrbitNotificationsTable(Migration):
    async def up(self) -> None:
        # Store may have created the table via CREATE IF NOT EXISTS on an older DB.
        await Schema.create_if_not_exists("orbit_notifications", self.orbit_notifications)

    async def down(self) -> None:
        await Schema.drop_if_exists("orbit_notifications")

    def orbit_notifications(self, table: Blueprint) -> None:
        table.string("id").primary()
        table.string("title")
        table.text("body").nullable()
        table.string("status").nullable()
        table.string("icon").nullable()
        table.string("icon_color").nullable()
        table.string("color").nullable()
        table.text("actions").nullable()
        table.integer("read").default(0)
        table.string("user_key").nullable().index()
        table.text("data").nullable()
        table.string("created_at").nullable()
