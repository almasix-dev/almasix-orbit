"""Sync catalog metrics for dashboard widgets (SQLite)."""

from __future__ import annotations

import json
import os
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any


def _db_path() -> Path:
    raw = os.environ.get("DB_DATABASE", "database/database.sqlite")
    path = Path(raw)
    if not path.is_absolute():
        # demo app root: examples/demo/
        path = Path(__file__).resolve().parents[3] / path
    return path


def _connect() -> sqlite3.Connection | None:
    path = _db_path()
    if not path.exists():
        return None
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def catalog_counts() -> dict[str, int]:
    conn = _connect()
    if conn is None:
        return {
            "artists": 0,
            "albums": 0,
            "tracks": 0,
            "plays": 0,
            "released": 0,
            "draft": 0,
            "featured": 0,
            "trashed": 0,
        }
    try:
        cur = conn.cursor()
        artists = cur.execute("SELECT COUNT(*) FROM artists").fetchone()[0]
        albums = cur.execute("SELECT COUNT(*) FROM albums").fetchone()[0]
        released = cur.execute(
            "SELECT COUNT(*) FROM albums WHERE status = 'released'"
        ).fetchone()[0]
        draft = cur.execute(
            "SELECT COUNT(*) FROM albums WHERE status = 'draft'"
        ).fetchone()[0]
        featured = cur.execute(
            "SELECT COUNT(*) FROM albums WHERE featured = 1"
        ).fetchone()[0]
        tracks = cur.execute(
            "SELECT COUNT(*) FROM tracks WHERE deleted_at IS NULL"
        ).fetchone()[0]
        trashed = cur.execute(
            "SELECT COUNT(*) FROM tracks WHERE deleted_at IS NOT NULL"
        ).fetchone()[0]
        plays = cur.execute(
            "SELECT COALESCE(SUM(play_count), 0) FROM tracks WHERE deleted_at IS NULL"
        ).fetchone()[0]
        return {
            "artists": int(artists),
            "albums": int(albums),
            "tracks": int(tracks),
            "plays": int(plays),
            "released": int(released),
            "draft": int(draft),
            "featured": int(featured),
            "trashed": int(trashed),
        }
    except sqlite3.Error:
        return {
            "artists": 0,
            "albums": 0,
            "tracks": 0,
            "plays": 0,
            "released": 0,
            "draft": 0,
            "featured": 0,
            "trashed": 0,
        }
    finally:
        conn.close()


def albums_by_year() -> tuple[list[str], list[int]]:
    conn = _connect()
    if conn is None:
        return [], []
    try:
        rows = conn.execute(
            "SELECT year, COUNT(*) AS c FROM albums WHERE year IS NOT NULL "
            "GROUP BY year ORDER BY year"
        ).fetchall()
        labels = [str(r["year"]) for r in rows]
        data = [int(r["c"]) for r in rows]
        return labels, data
    except sqlite3.Error:
        return [], []
    finally:
        conn.close()


def albums_by_status() -> tuple[list[str], list[int]]:
    conn = _connect()
    if conn is None:
        return [], []
    try:
        rows = conn.execute(
            "SELECT status, COUNT(*) AS c FROM albums "
            "WHERE status IS NOT NULL AND status != '' "
            "GROUP BY status ORDER BY c DESC"
        ).fetchall()
        labels = [str(r["status"]).title() for r in rows]
        data = [int(r["c"]) for r in rows]
        return labels, data
    except sqlite3.Error:
        return [], []
    finally:
        conn.close()


def top_tracks_by_plays(limit: int = 8) -> tuple[list[str], list[int]]:
    conn = _connect()
    if conn is None:
        return [], []
    try:
        rows = conn.execute(
            "SELECT title, play_count FROM tracks WHERE deleted_at IS NULL "
            "ORDER BY play_count DESC LIMIT ?",
            (limit,),
        ).fetchall()
        labels = [str(r["title"])[:24] for r in rows]
        data = [int(r["play_count"]) for r in rows]
        return labels, data
    except sqlite3.Error:
        return [], []
    finally:
        conn.close()


def top_artists_by_plays(limit: int = 8) -> tuple[list[str], list[int]]:
    conn = _connect()
    if conn is None:
        return [], []
    try:
        rows = conn.execute(
            """
            SELECT ar.name AS artist, COALESCE(SUM(t.play_count), 0) AS plays
            FROM artists ar
            LEFT JOIN albums a ON a.artist_id = ar.id
            LEFT JOIN tracks t ON t.album_id = a.id AND t.deleted_at IS NULL
            GROUP BY ar.id
            ORDER BY plays DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        labels = [str(r["artist"])[:22] for r in rows]
        data = [int(r["plays"]) for r in rows]
        return labels, data
    except sqlite3.Error:
        return [], []
    finally:
        conn.close()


def recent_albums(limit: int = 5) -> list[dict[str, Any]]:
    conn = _connect()
    if conn is None:
        return []
    try:
        rows = conn.execute(
            """
            SELECT a.title, a.status, a.year, ar.name AS artist
            FROM albums a
            LEFT JOIN artists ar ON ar.id = a.artist_id
            ORDER BY a.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            {
                "title": r["title"],
                "status": r["status"],
                "year": r["year"],
                "artist": r["artist"] or "—",
            }
            for r in rows
        ]
    except sqlite3.Error:
        return []
    finally:
        conn.close()


def top_track_rows(limit: int = 8) -> list[dict[str, Any]]:
    conn = _connect()
    if conn is None:
        return []
    try:
        rows = conn.execute(
            """
            SELECT t.title, t.play_count, t.status, a.title AS album
            FROM tracks t
            LEFT JOIN albums a ON a.id = t.album_id
            WHERE t.deleted_at IS NULL
            ORDER BY t.play_count DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            {
                "title": r["title"],
                "album": r["album"] or "—",
                "status": r["status"],
                "plays": f'{int(r["play_count"]):,}',
            }
            for r in rows
        ]
    except sqlite3.Error:
        return []
    finally:
        conn.close()


def artist_picker_rows() -> list[dict[str, Any]]:
    """Sync rows for ModalTableSelect on albums."""
    conn = _connect()
    if conn is None:
        return []
    try:
        rows = conn.execute(
            "SELECT id, name, country FROM artists ORDER BY name"
        ).fetchall()
        return [
            {"id": r["id"], "name": r["name"], "country": r["country"]}
            for r in rows
        ]
    except sqlite3.Error:
        return []
    finally:
        conn.close()


def format_counts() -> list[tuple[str, int]]:
    conn = _connect()
    if conn is None:
        return []
    try:
        rows = conn.execute(
            "SELECT format, COUNT(*) AS c FROM albums "
            "WHERE format IS NOT NULL AND format != '' "
            "GROUP BY format ORDER BY c DESC"
        ).fetchall()
        return [(str(r["format"]), int(r["c"])) for r in rows]
    except sqlite3.Error:
        return []
    finally:
        conn.close()


def country_breakdown() -> list[tuple[str, int]]:
    conn = _connect()
    if conn is None:
        return []
    try:
        rows = conn.execute(
            "SELECT country, COUNT(*) AS c FROM artists "
            "WHERE country IS NOT NULL GROUP BY country ORDER BY c DESC"
        ).fetchall()
        return [(str(r["country"]), int(r["c"])) for r in rows]
    except sqlite3.Error:
        return []
    finally:
        conn.close()


def _json_list_column(column: str) -> list[str]:
    """Flatten JSON array columns (genres / platforms) into tag tokens."""
    if column not in {"genres", "platforms"}:
        raise ValueError(f"unsupported JSON list column: {column}")
    conn = _connect()
    if conn is None:
        return []
    try:
        rows = conn.execute(
            f"SELECT {column} FROM artists WHERE {column} IS NOT NULL AND {column} != ''"
        ).fetchall()
        tags: list[str] = []
        for row in rows:
            raw = row[0]
            try:
                parsed = json.loads(raw) if isinstance(raw, str) else raw
            except (TypeError, json.JSONDecodeError):
                continue
            if isinstance(parsed, list):
                tags.extend(str(t).strip() for t in parsed if str(t).strip())
        return tags
    except sqlite3.Error:
        return []
    finally:
        conn.close()


def genre_breakdown(limit: int = 8) -> tuple[list[str], list[int]]:
    counter = Counter(_json_list_column("genres"))
    top = counter.most_common(limit)
    return [name for name, _ in top], [count for _, count in top]


def platform_breakdown() -> tuple[list[str], list[int]]:
    counter = Counter(_json_list_column("platforms"))
    items = counter.most_common()
    return [name.title() for name, _ in items], [count for _, count in items]


def genre_radar_series(limit: int = 6) -> tuple[list[str], list[dict[str, Any]]]:
    """Radar axes from top genres; two series: artist tags vs album density proxy."""
    labels, genre_counts = genre_breakdown(limit)
    if not labels:
        return [], []
    # Album proxy: scale genre popularity against released album count for a second ring.
    albums = max(catalog_counts()["albums"], 1)
    album_series = [
        max(1, int(round(count * albums / max(sum(genre_counts), 1))))
        for count in genre_counts
    ]
    return labels, [
        {"label": "Artists tagged", "data": genre_counts},
        {"label": "Catalog weight", "data": album_series},
    ]


def plays_by_week(range_key: str = "30d") -> tuple[list[str], list[dict[str, Any]]]:
    """
    Deterministic weekly play series derived from live catalog totals.

    No history table — shapes a believable trend from current play_count so
    line charts and filter tabs always have data after seed / soft reset.
    """
    weeks = {"7d": 7, "30d": 8, "90d": 12}.get(range_key, 8)
    counts = catalog_counts()
    total = max(counts["plays"], 1)
    released = max(counts["released"], 1)
    draft = max(counts["draft"], 1)

    labels = [f"W{i + 1}" for i in range(weeks)]
    # Rising curve with mild oscillation so the chart isn't a flat line.
    streams = [
        int(total * (0.35 + 0.55 * (i + 1) / weeks) * (0.92 + 0.08 * ((i % 3) / 2)))
        // weeks
        for i in range(weeks)
    ]
    # Second series: draft / discovery plays stay smaller.
    discovery = [
        int(streams[i] * (0.12 + 0.05 * (draft / (released + draft))) * (1 + (i % 2) * 0.15))
        for i in range(weeks)
    ]
    return labels, [
        {"label": "Streams", "data": streams},
        {"label": "Discovery", "data": discovery},
    ]


def sparkline_from_plays() -> list[int]:
    """Sparkline from weekly stream series so Stat cards reflect catalog volume."""
    _, datasets = plays_by_week("30d")
    if not datasets:
        return [0, 0, 0, 0, 0, 0]
    series = list(datasets[0].get("data") or [])
    if len(series) >= 6:
        return [int(v) for v in series[-6:]]
    if not series:
        return [0, 0, 0, 0, 0, 0]
    pad = series[0]
    return [int(pad)] * (6 - len(series)) + [int(v) for v in series]
