"""Track model — soft-deletable catalog track."""

from __future__ import annotations

from almasix.orm import Model, SoftDeletes


class Track(SoftDeletes, Model):
    fillable = (
        "album_id",
        "title",
        "track_number",
        "duration_sec",
        "isrc",
        "status",
        "play_count",
        "explicit",
    )
    casts = {
        "track_number": "int",
        "duration_sec": "int",
        "play_count": "int",
        "explicit": "bool",
    }

    def album(self):
        from app.models.album import Album

        return self.belongs_to(Album)
