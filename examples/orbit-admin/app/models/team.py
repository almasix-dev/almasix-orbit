"""Team model — morph target for the kitchen-sink Owner field."""

from __future__ import annotations

from almasix.orm import Model


class Team(Model):
    fillable = ("name",)
