"""Artist model — music catalog."""

from __future__ import annotations

from almasix.orm import Model


class Artist(Model):
    fillable = ("name", "bio", "country")
