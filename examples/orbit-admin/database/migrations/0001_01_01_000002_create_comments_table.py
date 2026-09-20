"""Create the comments table used by the Posts relation manager demo."""

from __future__ import annotations

from almasix.orm import Blueprint, Migration, Schema


class CreateCommentsTable(Migration):
    """Comments belong to a post — rendered by CommentsRelationManager."""

    async def up(self) -> None:
        await Schema.create("comments", self.comments)

    async def down(self) -> None:
        await Schema.drop_if_exists("comments")

    def comments(self, table: Blueprint) -> None:
        table.id()
        table.integer("post_id")
        table.string("author")
        table.text("body")
        table.string("status").default("visible")
        table.timestamps()
