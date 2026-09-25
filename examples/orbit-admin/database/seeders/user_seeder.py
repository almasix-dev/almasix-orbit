"""Seed demo users so kitchen-sink Manager / Owner can query a real table."""

from __future__ import annotations

from almasix.hashing import Hash
from almasix.orm import Seeder

from app.models.user import User

_USERS = [
    {"name": "Ada Lovelace", "email": "ada@orbit.test"},
    {"name": "Alan Turing", "email": "alan@orbit.test"},
    {"name": "Grace Hopper", "email": "grace@orbit.test"},
]


class UserSeeder(Seeder):
    async def run(self) -> None:
        if await User.count() > 0:
            return
        password = Hash.make("secret")
        for row in _USERS:
            await User.create({**row, "password": password})
