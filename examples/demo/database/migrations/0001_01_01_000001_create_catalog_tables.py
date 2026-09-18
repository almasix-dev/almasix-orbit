"""Create artists and albums tables."""

from __future__ import annotations

from almasix.orm import Blueprint, Migration, Schema


class CreateCatalogTables(Migration):
    async def up(self) -> None:
        await Schema.create("artists", self.artists)
        await Schema.create("albums", self.albums)

    async def down(self) -> None:
        await Schema.drop_if_exists("albums")
        await Schema.drop_if_exists("artists")

    def artists(self, table: Blueprint) -> None:
        table.id()
        table.string("name")
        table.text("bio").nullable()
        table.string("country").nullable()
        table.timestamps()

    def albums(self, table: Blueprint) -> None:
        table.id()
        table.string("title")
        table.integer("year").nullable()
        table.foreign_id("artist_id").constrained("artists").cascade_on_delete()
        table.string("status").default("draft")
        table.timestamps()
