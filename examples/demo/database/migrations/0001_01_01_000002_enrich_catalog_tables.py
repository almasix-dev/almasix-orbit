"""Enrich artists/albums and add tracks for the Orbit Records demo."""

from __future__ import annotations

from almasix.orm import Blueprint, Migration, Schema


class EnrichCatalogTables(Migration):
    async def up(self) -> None:
        await Schema.table("artists", self.enrich_artists)
        await Schema.table("albums", self.enrich_albums)
        await Schema.create("tracks", self.tracks)

    async def down(self) -> None:
        await Schema.drop_if_exists("tracks")
        await Schema.table("albums", self.drop_album_columns)
        await Schema.table("artists", self.drop_artist_columns)

    def enrich_artists(self, table: Blueprint) -> None:
        table.string("website").nullable()
        table.string("avatar").nullable()
        table.text("genres").nullable()
        table.string("brand_color").nullable()
        table.boolean("is_active").default(True)
        table.json("platforms").nullable()

    def drop_artist_columns(self, table: Blueprint) -> None:
        for col in (
            "website",
            "avatar",
            "genres",
            "brand_color",
            "is_active",
            "platforms",
        ):
            table.drop_column(col)

    def enrich_albums(self, table: Blueprint) -> None:
        table.date("released_at").nullable()
        table.date_time("published_at").nullable()
        table.string("cover").nullable()
        table.integer("price_cents").nullable()
        table.string("currency").default("USD")
        table.string("format").nullable()
        table.integer("rating").nullable()
        table.boolean("featured").default(False)
        table.text("liner_notes").nullable()
        table.json("credits").nullable()
        table.json("markets").nullable()
        table.json("meta").nullable()

    def drop_album_columns(self, table: Blueprint) -> None:
        for col in (
            "released_at",
            "published_at",
            "cover",
            "price_cents",
            "currency",
            "format",
            "rating",
            "featured",
            "liner_notes",
            "credits",
            "markets",
            "meta",
        ):
            table.drop_column(col)

    def tracks(self, table: Blueprint) -> None:
        table.id()
        table.foreign_id("album_id").constrained("albums").cascade_on_delete()
        table.string("title")
        table.integer("track_number").nullable()
        table.integer("duration_sec").nullable()
        table.string("isrc").nullable()
        table.string("status").default("draft")
        table.integer("play_count").default(0)
        table.boolean("explicit").default(False)
        table.soft_deletes()
        table.timestamps()
