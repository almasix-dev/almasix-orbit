"""Seed teams for the kitchen-sink morph Owner field."""

from __future__ import annotations

from almasix.orm import Seeder

from app.models.team import Team


class TeamSeeder(Seeder):
    async def run(self) -> None:
        if await Team.count() > 0:
            return
        await Team.create({"name": "Platform"})
        await Team.create({"name": "Research"})
