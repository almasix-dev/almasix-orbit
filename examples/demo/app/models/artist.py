"""Artist model — music catalog."""

from __future__ import annotations

from almasix.orm import Model


class Artist(Model):
    fillable = (
        "name",
        "bio",
        "country",
        "website",
        "avatar",
        "genres",
        "brand_color",
        "is_active",
        "platforms",
    )
    casts = {
        "platforms": "array",
        "genres": "array",
        "is_active": "bool",
    }

    def albums(self):
        from app.models.album import Album

        return self.has_many(Album)
