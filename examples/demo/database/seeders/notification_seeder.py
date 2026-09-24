"""Seed database notifications for the demo admin user."""

from __future__ import annotations

from almasix.orm import Seeder
from almasix.orbit.notifications import (
    AlmasixDatabaseNotificationStore,
    Notification,
    get_notifier,
)

from app.models.user import User


class NotificationSeeder(Seeder):
    async def run(self) -> None:
        user = await User.where("email", "demo@orbit.test").first()
        if user is None:
            return

        get_notifier().use_store(AlmasixDatabaseNotificationStore())

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
