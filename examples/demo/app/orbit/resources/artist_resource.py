"""Artists resource — ORM-backed CRUD."""

from __future__ import annotations

from almasix.orbit import Resource
from almasix.orbit.forms import Form, TextInput, Textarea
from almasix.orbit.tables import Table, TextColumn

from app.models.artist import Artist


class ArtistResource(Resource):
    model = Artist
    navigation_label = "Artists"
    navigation_group = "Catalog"
    navigation_icon = "heroicon-o-user-group"
    navigation_sort = 1
    record_title_attribute = "name"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("name").required().max_length(200),
                TextInput.make("country").max_length(100),
                Textarea.make("bio").rows(4),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns(
            [
                TextColumn.make("name").searchable().sortable(),
                TextColumn.make("country").sortable().toggleable(),
                TextColumn.make("bio").limit(60).toggleable(),
            ]
        ).stacked_on_mobile()
