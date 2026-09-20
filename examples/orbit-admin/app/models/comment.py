"""Comment model — related records for the Posts relation manager demo."""

from __future__ import annotations

from almasix.orm import Model


class Comment(Model):
    fillable = ("post_id", "author", "body", "status")
