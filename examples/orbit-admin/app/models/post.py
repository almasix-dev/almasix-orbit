"""Post model — database-backed CRUD demo for Orbit panels."""

from __future__ import annotations

from almasix.orm import Model


class Post(Model):
    fillable = ("title", "status", "body", "amount", "cover", "meta", "author_id")
