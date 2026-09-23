"""Tracks resource — soft-deletable catalog tracks."""

from __future__ import annotations

from typing import Any

from almasix.orbit import Resource
from almasix.orbit.forms import Form, Select, TextInput, Toggle
from almasix.orbit.infolists import IconEntry, Infolist, TextEntry
from almasix.orbit.schemas import Section
from almasix.orbit.tables import (
    BadgeColumn,
    BooleanColumn,
    Table,
    TernaryFilter,
    TextColumn,
    TrashedFilter,
)

from app.models.album import Album
from app.models.track import Track


def _format_duration(value: Any) -> str:
    try:
        secs = int(value or 0)
    except (TypeError, ValueError):
        return "—"
    return f"{secs // 60}:{secs % 60:02d}"


def _album_label(value: Any) -> str:
    if value in (None, ""):
        return "—"
    try:
        from almasix.orbit.forms.select_relationship import load_relationship_options

        opts = load_relationship_options(
            model=Album,
            title_attribute="title",
            keys=[value],
            limit=1,
        )
        return opts.get(str(value), str(value))
    except Exception:
        return str(value)


class TrackResource(Resource):
    model = Track
    navigation_label = "Tracks"
    navigation_group = "Catalog"
    navigation_icon = "heroicon-o-musical-note"
    navigation_sort = 3
    record_title_attribute = "title"
    soft_deletes = True
    global_search_attributes = ("title", "isrc")
    global_search_result_details = ("status",)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("title").required().max_length(200),
                Select.make("album_id")
                .label("Album")
                .relationship("album", "title")
                .searchable()
                .required(),
                TextInput.make("track_number").numeric().label("Track #"),
                TextInput.make("duration_sec").numeric().label("Duration (sec)"),
                TextInput.make("isrc").label("ISRC").max_length(15),
                Select.make("status")
                .options({"draft": "Draft", "released": "Released"})
                .required(),
                TextInput.make("play_count").numeric().label("Play count").default(0),
                Toggle.make("explicit").label("Explicit lyrics"),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.columns(
                [
                    TextColumn.make("track_number").label("#").sortable(),
                    TextColumn.make("title").searchable().sortable(),
                    TextColumn.make("album_id")
                    .label("Album")
                    .format_state_using(_album_label)
                    .sortable(),
                    TextColumn.make("duration_sec")
                    .label("Length")
                    .format_state_using(_format_duration)
                    .toggleable(),
                BadgeColumn.make("status").color(
                    lambda state, **_: {
                        "released": "success",
                        "draft": "gray",
                    }.get(str(state), "gray")
                ),
                    TextColumn.make("play_count").label("Plays").sortable().align_end(),
                    BooleanColumn.make("explicit").label("Explicit").toggleable(),
                    TextColumn.make("isrc").toggleable(is_toggled_hidden_by_default=True),
                ]
            )
            .filters(
                [
                    TrashedFilter.make(),
                    TernaryFilter.make("explicit")
                    .label("Explicit")
                    .true_label("Explicit only")
                    .false_label("Clean only"),
                ]
            )
            .defer_filters()
            .stacked_on_mobile()
        )

    @classmethod
    def infolist(cls, infolist: Infolist) -> Infolist:
        return infolist.columns(2).schema(
            [
                Section.make("track")
                .heading("Track")
                .schema(
                    [
                        TextEntry.make("title").label("Title").weight("bold").size("lg"),
                        TextEntry.make("track_number").label("Track #"),
                        TextEntry.make("duration_sec")
                        .label("Length")
                        .format_state_using(_format_duration),
                        TextEntry.make("isrc").label("ISRC").font_family("monospace"),
                        TextEntry.make("status").label("Status").badge(),
                        TextEntry.make("play_count").label("Plays").numeric(),
                        IconEntry.make("explicit").label("Explicit").boolean(),
                    ]
                ),
            ]
        )
