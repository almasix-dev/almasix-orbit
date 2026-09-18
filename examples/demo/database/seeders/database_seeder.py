"""Database seeder entrypoint."""

from __future__ import annotations

from almasix.orm import Seeder

from database.seeders.catalog_seeder import CatalogSeeder
from database.seeders.user_seeder import UserSeeder


class DatabaseSeeder(Seeder):
    async def run(self) -> None:
        await self.call([UserSeeder, CatalogSeeder])
