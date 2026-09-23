"""Sync catalog metrics for dashboard widgets (SQLite)."""

from __future__ import annotations

import os
import sqlite3
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
        return {"artists": 0, "albums": 0, "tracks": 0, "plays": 0, "released": 0}
    try:
        cur = conn.cursor()
        artists = cur.execute("SELECT COUNT(*) FROM artists").fetchone()[0]
        albums = cur.execute("SELECT COUNT(*) FROM albums").fetchone()[0]
        released = cur.execute(
            "SELECT COUNT(*) FROM albums WHERE status = 'released'"
        ).fetchone()[0]
        tracks = cur.execute(
            "SELECT COUNT(*) FROM tracks WHERE deleted_at IS NULL"
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
        }
    except sqlite3.Error:
        return {"artists": 0, "albums": 0, "tracks": 0, "plays": 0, "released": 0}
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


def sparkline_from_plays() -> list[int]:
    """Synthetic sparkline derived from play totals so charts look alive."""
    plays = catalog_counts()["plays"]
    if plays <= 0:
        return [0, 0, 0, 0, 0, 0]
    base = max(plays // 6, 1)
    return [int(base * f) for f in (0.55, 0.62, 0.7, 0.78, 0.9, 1.0)]
