"""Create the posts table for Orbit CRUD demos."""

from __future__ import annotations

from almasix.orm import Blueprint, Migration, Schema


class CreatePostsTable(Migration):
    """Posts used by Content → Posts (ORM-backed resource)."""

    async def up(self) -> None:
        await Schema.create("posts", self.posts)

    async def down(self) -> None:
        await Schema.drop_if_exists("posts")

    def posts(self, table: Blueprint) -> None:
        table.id()
        table.string("title")
        table.string("status").default("draft")
        table.text("body").nullable()
        table.integer("amount").default(0)
        table.timestamps()
