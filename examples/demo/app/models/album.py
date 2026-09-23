"""Album model — music catalog."""

from __future__ import annotations

from almasix.orm import Model


class Album(Model):
    fillable = (
        "title",
        "year",
        "artist_id",
        "status",
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
    )
    casts = {
        "credits": "array",
        "markets": "array",
        "meta": "array",
        "featured": "bool",
        "price_cents": "int",
        "rating": "int",
        "year": "int",
    }

    def artist(self):
        from app.models.artist import Artist

        return self.belongs_to(Artist)

    def tracks(self):
        from app.models.track import Track

        return self.has_many(Track)
