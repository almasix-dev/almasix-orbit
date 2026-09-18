"""Album model — music catalog."""

from __future__ import annotations

from almasix.orm import Model


class Album(Model):
    fillable = ("title", "year", "artist_id", "status")

    def artist(self):
        from app.models.artist import Artist

        return self.belongs_to(Artist)
