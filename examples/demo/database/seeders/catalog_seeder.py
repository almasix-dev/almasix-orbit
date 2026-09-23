"""Seed artists, albums, and tracks for the Orbit Records demo."""

from __future__ import annotations

from almasix.orm import Seeder

from app.models.album import Album
from app.models.artist import Artist
from app.models.track import Track

_ARTISTS = [
    {
        "name": "Nova Echo",
        "country": "Kenya",
        "bio": "Afro-electronic producer from Nairobi.",
        "website": "https://novaecho.example",
        "genres": ["afrobeat", "electronic", "ambient"],
        "brand_color": "#0ea5e9",
        "is_active": True,
        "platforms": ["spotify", "apple", "bandcamp"],
    },
    {
        "name": "Cedar & Ash",
        "country": "Canada",
        "bio": "Indie folk duo with close harmonies.",
        "website": "https://cedarash.example",
        "genres": ["folk", "indie", "acoustic"],
        "brand_color": "#84cc16",
        "is_active": True,
        "platforms": ["spotify", "apple"],
    },
    {
        "name": "Lumen Circuit",
        "country": "Germany",
        "bio": "Synthwave and ambient architect.",
        "website": "https://lumencircuit.example",
        "genres": ["synthwave", "ambient", "electronic"],
        "brand_color": "#a855f7",
        "is_active": True,
        "platforms": ["spotify", "bandcamp", "soundcloud"],
    },
    {
        "name": "Mara Tide",
        "country": "Portugal",
        "bio": "Coastal jazz and downtempo.",
        "website": "https://maratide.example",
        "genres": ["jazz", "downtempo"],
        "brand_color": "#14b8a6",
        "is_active": True,
        "platforms": ["spotify", "apple", "soundcloud"],
    },
    {
        "name": "Static Bloom",
        "country": "Japan",
        "bio": "Post-rock textures and field recordings.",
        "website": "https://staticbloom.example",
        "genres": ["post-rock", "experimental"],
        "brand_color": "#f97316",
        "is_active": True,
        "platforms": ["bandcamp"],
    },
    {
        "name": "Kito Pulse",
        "country": "Brazil",
        "bio": "Club-ready tropical bass.",
        "website": "https://kitopulse.example",
        "genres": ["bass", "tropical", "dance"],
        "brand_color": "#ef4444",
        "is_active": True,
        "platforms": ["spotify", "apple", "soundcloud"],
    },
    {
        "name": "Hollow Lantern",
        "country": "Ireland",
        "bio": "Story-driven indie rock.",
        "website": "https://hollowlantern.example",
        "genres": ["indie", "rock"],
        "brand_color": "#64748b",
        "is_active": False,
        "platforms": ["spotify"],
    },
    {
        "name": "Orbit Choir",
        "country": "United States",
        "bio": "House choir for the Orbit catalog demos.",
        "website": "https://orbitchoir.example",
        "genres": ["choral", "ambient"],
        "brand_color": "#2563eb",
        "is_active": True,
        "platforms": ["spotify", "apple", "bandcamp", "soundcloud"],
    },
]

# (artist_index, title, year, status, released_at, published_at, price_cents,
#  format, rating, featured, markets)
_ALBUMS = [
    (0, "Night Markets", 2024, "released", "2024-03-12", "2024-03-12 09:00:00", 1299, "digital", 88, True, ["US", "EU", "KE"]),
    (0, "Dust & Neon", 2025, "draft", None, None, 1499, "streaming", 72, False, ["KE", "EU"]),
    (0, "Bazaar Echoes", 2022, "released", "2022-11-01", "2022-11-01 12:00:00", 999, "vinyl", 91, True, ["US", "KE"]),
    (1, "River Stones", 2023, "released", "2023-06-20", "2023-06-20 10:00:00", 1199, "cd", 85, False, ["US", "CA", "EU"]),
    (1, "Cabin Songs", 2022, "released", "2022-02-14", "2022-02-14 08:00:00", 1099, "digital", 80, False, ["CA", "US"]),
    (1, "Frost Line", 2025, "draft", None, None, 1399, "vinyl", 60, False, ["CA"]),
    (2, "Gridline", 2021, "released", "2021-09-09", "2021-09-09 18:00:00", 1599, "digital", 94, True, ["EU", "JP", "US"]),
    (2, "Afterglow Protocol", 2025, "draft", None, None, 1699, "streaming", 70, False, ["EU"]),
    (3, "Salt Air", 2023, "released", "2023-08-01", "2023-08-01 11:00:00", 1249, "cd", 83, False, ["EU", "US"]),
    (3, "Blue Hour EP", 2024, "released", "2024-01-18", "2024-01-18 07:30:00", 799, "digital", 77, False, ["EU", "PT"]),
    (4, "Concrete Gardens", 2020, "released", "2020-05-05", "2020-05-05 15:00:00", 1499, "vinyl", 89, True, ["JP", "US"]),
    (4, "Tape Loops Vol. 1", 2024, "released", "2024-10-10", "2024-10-10 10:00:00", 999, "digital", 76, False, ["JP"]),
    (5, "Carnival Voltage", 2023, "released", "2023-12-01", "2023-12-01 22:00:00", 1349, "streaming", 86, True, ["BR", "US", "EU"]),
    (6, "Lantern Drafts", 2019, "released", "2019-04-04", "2019-04-04 09:00:00", 899, "cd", 68, False, ["EU", "US"]),
    (7, "Orbit Hymns", 2025, "released", "2025-01-15", "2025-01-15 06:00:00", 0, "streaming", 95, True, ["US", "EU", "KE", "JP"]),
]

_TRACK_TITLES = [
    "Opening Signal",
    "Midnight Vendor",
    "Neon Canopy",
    "Dust Circuit",
    "River Bend",
    "Cabin Light",
    "Grid Pulse",
    "Afterglow",
    "Salt Spray",
    "Blue Hour",
    "Concrete Bloom",
    "Tape Hiss",
    "Carnival Run",
    "Lantern Walk",
    "Choir Lift",
    "Market Rain",
    "Static Field",
    "Tide Marker",
    "Bass Parade",
    "Orbit Theme",
]


class CatalogSeeder(Seeder):
    async def run(self) -> None:
        if await Artist.count() > 0:
            return

        artists: list[Artist] = []
        for row in _ARTISTS:
            artists.append(await Artist.create(row))

        albums: list[Album] = []
        for spec in _ALBUMS:
            (
                artist_idx,
                title,
                year,
                status,
                released_at,
                published_at,
                price_cents,
                fmt,
                rating,
                featured,
                markets,
            ) = spec
            albums.append(
                await Album.create(
                    {
                        "title": title,
                        "year": year,
                        "artist_id": artists[artist_idx].id,
                        "status": status,
                        "released_at": released_at,
                        "published_at": published_at,
                        "price_cents": price_cents,
                        "currency": "USD",
                        "format": fmt,
                        "rating": rating,
                        "featured": featured,
                        "liner_notes": (
                            f"<p><strong>{title}</strong> liner notes for the "
                            "Orbit Records catalog demo.</p>"
                        ),
                        "credits": {
                            "producer": artists[artist_idx].name,
                            "mix": "Orbit Studio",
                            "master": "Almasix Mastering",
                        },
                        "markets": markets,
                        "meta": {"catalog_code": f"OR-{year}-{artist_idx + 1:02d}"},
                    }
                )
            )

        track_i = 0
        for album in albums:
            # 3–5 tracks per album → ~45–75 total across 15 albums
            count = 3 + (int(album.id or 0) % 3)
            for n in range(1, count + 1):
                title = _TRACK_TITLES[track_i % len(_TRACK_TITLES)]
                track_i += 1
                play = 500 + (track_i * 137) % 50000
                await Track.create(
                    {
                        "album_id": album.id,
                        "title": f"{title} {n}" if count > 3 else title,
                        "track_number": n,
                        "duration_sec": 120 + (track_i * 17) % 280,
                        "isrc": f"QZORM{2020 + (track_i % 6)}{track_i:05d}",
                        "status": album.status if album.status == "released" else "draft",
                        "play_count": play if album.status == "released" else play // 10,
                        "explicit": track_i % 7 == 0,
                    }
                )
