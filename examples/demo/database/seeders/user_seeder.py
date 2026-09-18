"""Seed demo admin user."""

from __future__ import annotations

from almasix.hashing import Hash
from almasix.orm import Seeder

from app.models.user import User


class UserSeeder(Seeder):
    async def run(self) -> None:
        if await User.where("email", "demo@orbit.test").first():
            return
        await User.create(
            {
                "name": "Demo Admin",
                "email": "demo@orbit.test",
                "password": Hash.make("secret"),
            }
        )
