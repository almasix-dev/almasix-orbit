"""Database seeder entrypoint."""

from __future__ import annotations

from almasix.orm import Seeder

from database.seeders.post_seeder import PostSeeder


class DatabaseSeeder(Seeder):
    async def run(self) -> None:
        await self.call([PostSeeder])
