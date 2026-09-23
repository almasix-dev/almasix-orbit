"""Seed database notifications for the demo admin user."""

from __future__ import annotations

from almasix.orm import Seeder
from almasix.orbit.notifications import Notification, SqliteNotificationStore, get_notifier

from app.models.user import User


def _notification_db_path() -> str:
    from almasix.config import env

    return str(env("DB_DATABASE", "database/database.sqlite") or "database/database.sqlite")


class NotificationSeeder(Seeder):
    async def run(self) -> None:
        user = await User.where("email", "demo@orbit.test").first()
        if user is None:
            return

        store = SqliteNotificationStore(_notification_db_path())
        get_notifier().use_store(store)

        seeds = [
            (
                "seed-welcome",
                "Welcome to Orbit Records",
                "Explore Artists, Albums, Tracks, and Insights — edits notify this bell.",
                "success",
            ),
            (
                "seed-release",
                "New release window",
                "Draft albums are ready for review in the catalog.",
                "info",
            ),
            (
                "seed-tip",
                "Tip: save an artist or album",
                "Creating or updating catalog records sends a live database notification here.",
                "warning",
            ),
        ]
        for nid, title, body, status in seeds:
            (
                Notification.make(id=nid)
                .title(title)
                .body(body)
                .status(status)
                .send_to_database(user)
            )
