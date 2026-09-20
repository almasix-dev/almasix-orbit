"""Add cover art, rich body metadata, and an author link to posts."""

from __future__ import annotations

from almasix.orm import Blueprint, Migration, Schema


class AddMediaToPosts(Migration):
    """Columns behind the FileUpload / KeyValue / ModalTableSelect demos."""

    async def up(self) -> None:
        await Schema.table("posts", self.add_columns)

    async def down(self) -> None:
        await Schema.table("posts", self.drop_columns)

    def add_columns(self, table: Blueprint) -> None:
        table.string("cover").nullable()
        table.text("meta").nullable()
        table.string("author_id").nullable()

    def drop_columns(self, table: Blueprint) -> None:
        table.drop_column("cover")
        table.drop_column("meta")
        table.drop_column("author_id")
