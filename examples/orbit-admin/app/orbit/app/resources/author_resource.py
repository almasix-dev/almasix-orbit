"""Authors resource."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import Table, TextColumn


class AuthorResource(Resource):
    model = type("Author", (), {})
    navigation_label = "Authors"
    navigation_group = "Content"
    navigation_icon = "heroicon-o-user-group"
    navigation_sort = 2
    record_title_attribute = "name"
    global_search_attributes = ("name", "email")
    global_search_result_details = ("email",)

    records: ClassVar[list[dict[str, Any]]] = [
        {"id": 1, "name": "Ada Lovelace", "email": "ada@orbit.test"},
        {"id": 2, "name": "Grace Hopper", "email": "grace@orbit.test"},
    ]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("name").required(),
                TextInput.make("email").email().required(),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns(
            [
                TextColumn.make("name").searchable(),
                TextColumn.make("email"),
            ]
        )
