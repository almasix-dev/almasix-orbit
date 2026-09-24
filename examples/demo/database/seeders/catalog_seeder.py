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
    {
        "name": "Saffron Relay",
        "country": "India",
        "bio": "Neo-classical strings meeting Delhi club nights.",
        "website": "https://saffronrelay.example",
        "genres": ["classical", "electronic", "fusion"],
        "brand_color": "#eab308",
        "is_active": True,
        "platforms": ["spotify", "apple"],
    },
    {
        "name": "Frost Market",
        "country": "Sweden",
        "bio": "Nordic house and glacial pads.",
        "website": "https://frostmarket.example",
        "genres": ["house", "electronic", "ambient"],
        "brand_color": "#38bdf8",
        "is_active": True,
        "platforms": ["spotify", "bandcamp", "soundcloud"],
    },
    {
        "name": "Copper Lantern",
        "country": "Mexico",
        "bio": "Cumbia futures and desert psych.",
        "website": "https://copperlantern.example",
        "genres": ["cumbia", "psych", "latin"],
        "brand_color": "#d97706",
        "is_active": True,
        "platforms": ["spotify", "apple", "bandcamp"],
    },
    {
        "name": "Glass Harbor",
        "country": "Australia",
        "bio": "Coastal indie and dream-pop.",
        "website": "https://glassharbor.example",
        "genres": ["indie", "dream-pop"],
        "brand_color": "#22d3ee",
        "is_active": True,
        "platforms": ["spotify", "apple"],
    },
    {
        "name": "Redline Quartet",
        "country": "France",
        "bio": "Chamber jazz with modular accents.",
        "website": "https://redlinequartet.example",
        "genres": ["jazz", "experimental"],
        "brand_color": "#dc2626",
        "is_active": True,
        "platforms": ["bandcamp", "apple"],
    },
    {
        "name": "Yuzu Drift",
        "country": "South Korea",
        "bio": "City-pop nostalgia and soft club edits.",
        "website": "https://yuzudrift.example",
        "genres": ["city-pop", "dance", "electronic"],
        "brand_color": "#f472b6",
        "is_active": True,
        "platforms": ["spotify", "apple", "soundcloud"],
    },
    {
        "name": "Basin Choir",
        "country": "Nigeria",
        "bio": "Afro-soul harmonies and highlife nods.",
        "website": "https://basinchoir.example",
        "genres": ["afrobeat", "soul", "highlife"],
        "brand_color": "#16a34a",
        "is_active": True,
        "platforms": ["spotify", "apple", "bandcamp"],
    },
    {
        "name": "Pylon Echo",
        "country": "United Kingdom",
        "bio": "Post-punk basslines and tape delay.",
        "website": "https://pylonecho.example",
        "genres": ["post-punk", "rock", "indie"],
        "brand_color": "#71717a",
        "is_active": True,
        "platforms": ["spotify", "bandcamp"],
    },
    {
        "name": "Mirage Atlas",
        "country": "Morocco",
        "bio": "Gnawa rhythms under desert electronics.",
        "website": "https://mirageatlas.example",
        "genres": ["gnawa", "electronic", "world"],
        "brand_color": "#c026d3",
        "is_active": True,
        "platforms": ["spotify", "bandcamp", "soundcloud"],
    },
    {
        "name": "Paper Kite",
        "country": "Taiwan",
        "bio": "Lo-fi beds and rainy-window songs.",
        "website": "https://paperkite.example",
        "genres": ["lo-fi", "indie", "ambient"],
        "brand_color": "#a1a1aa",
        "is_active": True,
        "platforms": ["spotify", "bandcamp"],
    },
    {
        "name": "Volt Parade",
        "country": "Netherlands",
        "bio": "Festival techno with brass stabs.",
        "website": "https://voltparade.example",
        "genres": ["techno", "dance", "electronic"],
        "brand_color": "#4f46e5",
        "is_active": True,
        "platforms": ["spotify", "soundcloud", "bandcamp"],
    },
    {
        "name": "Silt & Cedar",
        "country": "New Zealand",
        "bio": "Folk storytelling from the South Island.",
        "website": "https://siltcedar.example",
        "genres": ["folk", "acoustic"],
        "brand_color": "#65a30d",
        "is_active": True,
        "platforms": ["spotify", "apple", "bandcamp"],
    },
    {
        "name": "Chrome Orchard",
        "country": "Spain",
        "bio": "Mediterranean disco and balearic edits.",
        "website": "https://chromeorchard.example",
        "genres": ["disco", "dance", "electronic"],
        "brand_color": "#ea580c",
        "is_active": True,
        "platforms": ["spotify", "apple", "soundcloud"],
    },
    {
        "name": "Quiet Voltage",
        "country": "Finland",
        "bio": "Minimal piano and glacial drones.",
        "website": "https://quietvoltage.example",
        "genres": ["ambient", "classical", "experimental"],
        "brand_color": "#94a3b8",
        "is_active": False,
        "platforms": ["bandcamp"],
    },
    {
        "name": "Harbor Neon",
        "country": "Singapore",
        "bio": "Late-night R&B and rain-slick synths.",
        "website": "https://harborneon.example",
        "genres": ["rnb", "electronic", "soul"],
        "brand_color": "#e11d48",
        "is_active": True,
        "platforms": ["spotify", "apple", "soundcloud"],
    },
    {
        "name": "Field Archive",
        "country": "United States",
        "bio": "Documentary soundscapes and spoken word.",
        "website": "https://fieldarchive.example",
        "genres": ["experimental", "ambient", "spoken-word"],
        "brand_color": "#78716c",
        "is_active": True,
        "platforms": ["bandcamp", "soundcloud"],
    },
]

_FORMATS = ("digital", "streaming", "vinyl", "cd")
_MARKETS = (
    ["US", "EU"],
    ["US", "CA", "EU"],
    ["KE", "EU"],
    ["JP", "US"],
    ["BR", "US", "EU"],
    ["EU", "PT"],
    ["IN", "EU", "US"],
    ["AU", "US"],
    ["KR", "JP", "US"],
    ["NG", "KE", "US"],
    ["MX", "US", "EU"],
    ["SG", "JP", "AU"],
)

_ALBUM_TITLES = [
    "Night Markets",
    "Dust & Neon",
    "Bazaar Echoes",
    "River Stones",
    "Cabin Songs",
    "Frost Line",
    "Gridline",
    "Afterglow Protocol",
    "Salt Air",
    "Blue Hour EP",
    "Concrete Gardens",
    "Tape Loops Vol. 1",
    "Carnival Voltage",
    "Lantern Drafts",
    "Orbit Hymns",
    "Monsoon Circuits",
    "Aurora Ledger",
    "Desert Mirror",
    "Glass Tide",
    "Redline Sessions",
    "Yuzu Nights",
    "Basin Light",
    "Pylon Static",
    "Atlas Drift",
    "Paper Rain",
    "Volt Garden",
    "Cedar Hours",
    "Orchard Signal",
    "Quiet Grid",
    "Harbor Glass",
    "Field Notes",
    "Echo Bazaar",
    "Soft Voltage",
    "Tide Archive",
    "Neon Basin",
    "Copper Hymns",
    "Silt Songs",
    "Parade Loops",
    "Relay Bloom",
    "Market Choir",
    "Lantern Atlas",
    "Coastal Protocol",
    "Studio Dust",
    "Midnight Relay",
    "Orbit Drafts",
    "Signal Gardens",
    "Ash Protocol",
    "Bloom Voltage",
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
    "Monsoon Gate",
    "Aurora Soft",
    "Desert Wire",
    "Glass Current",
    "Redline Soft",
    "Yuzu Drift",
    "Basin Rise",
    "Pylon Hum",
    "Atlas Fade",
    "Paper Fold",
    "Volt Bloom",
    "Cedar Smoke",
    "Orchard Step",
    "Quiet Spark",
    "Harbor Glow",
    "Field Soft",
    "Relay Click",
    "Parade Soft",
    "Silt Drift",
    "Chrome Wave",
]


def _album_specs() -> list[tuple[int, str, int, str, str | None, str | None, int, str, int, bool, list[str]]]:
    """Build ~56 albums across artists with varied years, formats, and statuses."""
    specs: list[
        tuple[int, str, int, str, str | None, str | None, int, str, int, bool, list[str]]
    ] = []
    title_i = 0
    for artist_idx in range(len(_ARTISTS)):
        # Most artists get 2 albums; every third gets 3 → ~56 max, trim to ~48 via loop.
        count = 3 if artist_idx % 3 == 0 else 2
        for n in range(count):
            title = _ALBUM_TITLES[title_i % len(_ALBUM_TITLES)]
            if n > 0:
                title = f"{title} {n + 1}" if title_i >= len(_ALBUM_TITLES) else title
            title_i += 1
            year = 2018 + ((artist_idx * 3 + n * 2) % 8)
            # ~18% drafts, rest released
            status = "draft" if (artist_idx + n) % 6 == 5 else "released"
            released_at = None if status == "draft" else f"{year}-{1 + (n * 3) % 12:02d}-{10 + n:02d}"
            published_at = None if status == "draft" else f"{released_at} {8 + n:02d}:00:00"
            price = 0 if (artist_idx + n) % 11 == 0 else 799 + ((artist_idx * 50 + n * 100) % 900)
            fmt = _FORMATS[(artist_idx + n) % len(_FORMATS)]
            rating = 55 + ((artist_idx * 7 + n * 11) % 41)
            featured = status == "released" and (artist_idx + n) % 4 == 0
            markets = list(_MARKETS[(artist_idx + n) % len(_MARKETS)])
            specs.append(
                (
                    artist_idx,
                    title,
                    year,
                    status,
                    released_at,
                    published_at,
                    price,
                    fmt,
                    rating,
                    featured,
                    markets,
                )
            )
    return specs


class CatalogSeeder(Seeder):
    async def run(self) -> None:
        if await Artist.count() > 0:
            return

        artists: list[Artist] = []
        for row in _ARTISTS:
            artists.append(await Artist.create(row))

        albums: list[Album] = []
        for spec in _album_specs():
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
        soft_delete_ids: list[int] = []
        for album in albums:
            # 4–6 tracks per album → ~220–280 across ~56 albums
            count = 4 + (int(album.id or 0) % 3)
            for n in range(1, count + 1):
                title = _TRACK_TITLES[track_i % len(_TRACK_TITLES)]
                track_i += 1
                play = 200 + (track_i * 137) % 80000
                if album.status != "released":
                    play = play // 12
                track = await Track.create(
                    {
                        "album_id": album.id,
                        "title": f"{title} {n}" if count > 4 else title,
                        "track_number": n,
                        "duration_sec": 110 + (track_i * 17) % 300,
                        "isrc": f"QZORM{2018 + (track_i % 8)}{track_i:05d}",
                        "status": album.status if album.status == "released" else "draft",
                        "play_count": play,
                        "explicit": track_i % 9 == 0,
                    }
                )
                # Soft-delete a handful so trashed filters and metrics stay honest.
                if track_i in {17, 41, 88, 133, 201} and track.id is not None:
                    soft_delete_ids.append(int(track.id))

        for tid in soft_delete_ids:
            row = await Track.find(tid)
            if row is not None:
                await row.delete()
