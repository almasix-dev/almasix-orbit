"""Seed one kitchen-sink profile so the form opens against a real row."""

from __future__ import annotations

from almasix.orm import Seeder

from app.models.kitchen_sink import KitchenSink
from app.models.team import Team
from app.models.user import User


class KitchenSinkSeeder(Seeder):
    async def run(self) -> None:
        if await KitchenSink.count() > 0:
            return
        manager = await User.query().where("email", "ada@orbit.test").first()
        if manager is None:
            manager = await User.query().first()
        team = await Team.query().where("name", "Platform").first()
        await KitchenSink.create(
            {
                "name": "Ada Lovelace",
                "email": "ada@orbit.test",
                "role": "admin",
                "bio": "First programmer.",
                "plan": "pro",
                "features": ["api"],
                "tags": ["math", "poetry"],
                "amount": 42.5,
                "color": "#3366ff",
                "active": True,
                "priority": "high",
                "joined": "2024-01-15",
                "owner": {
                    "type": "team" if team is not None else "user",
                    "id": str(getattr(team, "id", None) or getattr(manager, "id", "") or ""),
                },
                "manager_id": getattr(manager, "id", None),
                "links": [{"url": "https://orbit.almasix.com"}],
                "meta": {"team": "core"},
                "blocks": [{"type": "hero", "heading": "Welcome"}],
                "body": "<p>Kitchen sink stored in SQLite.</p>",
                "terms": True,
            }
        )
