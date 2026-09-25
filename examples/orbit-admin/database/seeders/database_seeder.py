"""Database seeder entrypoint."""

from __future__ import annotations

from almasix.orm import Seeder

from database.seeders.comment_seeder import CommentSeeder
from database.seeders.kitchen_sink_seeder import KitchenSinkSeeder
from database.seeders.post_seeder import PostSeeder
from database.seeders.team_seeder import TeamSeeder
from database.seeders.user_seeder import UserSeeder


class DatabaseSeeder(Seeder):
    async def run(self) -> None:
        await self.call(
            [UserSeeder, TeamSeeder, PostSeeder, CommentSeeder, KitchenSinkSeeder]
        )
