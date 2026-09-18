"""Seed artists and albums for the music catalog demo."""

from __future__ import annotations

from almasix.orm import Seeder

from app.models.album import Album
from app.models.artist import Artist

_ARTISTS = [
    {"name": "Nova Echo", "country": "Kenya", "bio": "Afro-electronic producer from Nairobi."},
    {"name": "Cedar & Ash", "country": "Canada", "bio": "Indie folk duo."},
    {"name": "Lumen Circuit", "country": "Germany", "bio": "Synthwave and ambient."},
]


class CatalogSeeder(Seeder):
    async def run(self) -> None:
        if await Artist.count() > 0:
            return
        artists: list[Artist] = []
        for row in _ARTISTS:
            artists.append(await Artist.create(row))

        albums = [
            {
                "title": "Night Markets",
                "year": 2024,
                "artist_id": artists[0].id,
                "status": "released",
            },
            {
                "title": "Dust & Neon",
                "year": 2025,
                "artist_id": artists[0].id,
                "status": "draft",
            },
            {
                "title": "River Stones",
                "year": 2023,
                "artist_id": artists[1].id,
                "status": "released",
            },
            {
                "title": "Cabin Songs",
                "year": 2022,
                "artist_id": artists[1].id,
                "status": "released",
            },
            {
                "title": "Gridline",
                "year": 2021,
                "artist_id": artists[2].id,
                "status": "released",
            },
            {
                "title": "Afterglow Protocol",
                "year": 2025,
                "artist_id": artists[2].id,
                "status": "draft",
            },
        ]
        for row in albums:
            await Album.create(row)
