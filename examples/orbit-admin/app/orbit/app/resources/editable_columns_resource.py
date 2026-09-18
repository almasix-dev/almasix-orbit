"""Editable Select / Toggle / TextInput / Checkbox columns."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import (
    CheckboxColumn,
    SelectColumn,
    Table,
    TextColumn,
    TextInputColumn,
    ToggleColumn,
)


class EditableColumnsResource(Resource):
    model = type("EditableDemo", (), {})
    slug = "editable-columns"
    navigation_label = "Editable columns"
    navigation_group = "Columns"
    navigation_icon = "heroicon-o-pencil-square"
    navigation_sort = 3

    records: ClassVar[list[dict[str, Any]]] = [
        {
            "id": 1,
            "title": "Filters polish",
            "status": "review",
            "priority": "high",
            "done": False,
            "featured": True,
        },
        {
            "id": 2,
            "title": "Summaries",
            "status": "published",
            "priority": "med",
            "done": True,
            "featured": False,
        },
    ]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title")])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns(
            [
                TextInputColumn.make("title").label("Title"),
                SelectColumn.make("status").options(
                    {"draft": "Draft", "review": "Review", "published": "Published"}
                ),
                SelectColumn.make("priority").options(
                    {"low": "Low", "med": "Med", "high": "High"}
                ),
                ToggleColumn.make("featured").label("Featured"),
                CheckboxColumn.make("done").label("Done"),
                TextColumn.make("id").label("ID"),
            ]
        )
