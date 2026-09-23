"""Tracks relation manager — nested on Album view/edit pages."""

from __future__ import annotations

from typing import Any

from almasix.orbit import RelationManager
from almasix.orbit.forms import Form, Select, TextInput, Toggle
from almasix.orbit.tables import BadgeColumn, BooleanColumn, Table, TextColumn

from app.models.track import Track


def _format_duration(value: Any) -> str:
    try:
        secs = int(value or 0)
    except (TypeError, ValueError):
        return "—"
    return f"{secs // 60}:{secs % 60:02d}"


class TracksRelationManager(RelationManager):
    relationship = "tracks"
    title = "Tracks"
    description = "Tracklist for this album."
    record_title_attribute = "title"
    related_model = Track
    foreign_key = "album_id"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("title").required().max_length(200),
                TextInput.make("track_number").numeric().label("Track #"),
                TextInput.make("duration_sec").numeric().label("Duration (sec)"),
                TextInput.make("isrc").label("ISRC").max_length(15),
                Select.make("status")
                .options({"draft": "Draft", "released": "Released"})
                .default("draft"),
                Toggle.make("explicit").label("Explicit"),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns(
            [
                TextColumn.make("track_number").label("#").sortable(),
                TextColumn.make("title").searchable().sortable(),
                TextColumn.make("duration_sec")
                .label("Length")
                .format_state_using(_format_duration),
                BadgeColumn.make("status").color(
                    lambda state, **_: {
                        "released": "success",
                        "draft": "gray",
                    }.get(str(state), "gray")
                ),
                TextColumn.make("play_count").label("Plays").sortable().align_end(),
                BooleanColumn.make("explicit").label("E"),
            ]
        )
