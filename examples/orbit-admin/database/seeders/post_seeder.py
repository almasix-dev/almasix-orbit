"""Seed demo posts for Content → Posts CRUD."""

from __future__ import annotations

from almasix.orm import Seeder

from app.models.post import Post

_SEED_POSTS = [
    {"title": "Launch Orbit", "status": "published", "amount": 1200, "body": "Ship the Orbit admin panel."},
    {"title": "Conduit hosts", "status": "draft", "amount": 120, "body": "Wire Livewire-style hosts."},
    {"title": "Mobile tables", "status": "review", "amount": 450, "body": "Stack columns on small screens."},
    {"title": "Panel branding", "status": "published", "amount": 880, "body": "Logos, colors, and chrome."},
    {"title": "Auth signup flow", "status": "published", "amount": 640, "body": "Register + login hosts."},
    {"title": "Dashboard widgets", "status": "draft", "amount": 90, "body": "Stats and charts."},
    {"title": "Filter chrome", "status": "review", "amount": 330, "body": "Defer filters and chips."},
    {"title": "Bulk actions", "status": "draft", "amount": 170, "body": "Select all + delete."},
    {"title": "Empty states", "status": "review", "amount": 210, "body": "Friendly zero-data UI."},
    {"title": "Content grid cards", "status": "draft", "amount": 140, "body": "Card layout demos."},
    {"title": "Sortable columns", "status": "published", "amount": 560, "body": "Click headers to sort."},
    {"title": "Pagination footer", "status": "published", "amount": 410, "body": "Per-page controls."},
    {"title": "Search toolbar", "status": "review", "amount": 280, "body": "Debounced table search."},
    {"title": "Relation managers", "status": "draft", "amount": 70, "body": "Nested resource tables."},
]


class PostSeeder(Seeder):
    async def run(self) -> None:
        if await Post.count() > 0:
            return
        for row in _SEED_POSTS:
            await Post.create(row)
