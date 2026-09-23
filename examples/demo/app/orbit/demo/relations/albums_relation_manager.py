"""Albums relation manager — nested on Artist view/edit pages."""

from __future__ import annotations

from almasix.orbit import RelationManager
from almasix.orbit.forms import Form, Select, TextInput, ToggleButtons
from almasix.orbit.tables import BadgeColumn, Table, TextColumn

from app.models.album import Album


class AlbumsRelationManager(RelationManager):
    relationship = "albums"
    title = "Albums"
    description = "Releases attached to this artist."
    record_title_attribute = "title"
    related_model = Album
    foreign_key = "artist_id"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("title").required().max_length(200),
                TextInput.make("year").numeric().label("Year"),
                ToggleButtons.make("status")
                .options({"draft": "Draft", "released": "Released"})
                .default("draft"),
                Select.make("format")
                .options(
                    {
                        "digital": "Digital",
                        "streaming": "Streaming",
                        "cd": "CD",
                        "vinyl": "Vinyl",
                    }
                ),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns(
            [
                TextColumn.make("title").searchable().sortable(),
                TextColumn.make("year").sortable(),
                BadgeColumn.make("status").color(
                    lambda state, **_: {
                        "released": "success",
                        "draft": "gray",
                    }.get(str(state), "gray")
                ),
                TextColumn.make("format").toggleable(),
            ]
        )
