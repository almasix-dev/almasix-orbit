"""Text column gallery."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import Table, TextColumn


class TextColumnsResource(Resource):
    model = type("TextDemo", (), {})
    slug = "text-columns"
    navigation_label = "Text columns"
    navigation_group = "Columns"
    navigation_icon = "heroicon-o-bars-3"
    navigation_sort = 1

    records: ClassVar[list[dict[str, Any]]] = [
        {
            "id": 1,
            "name": "Orbit",
            "status": "published",
            "amount": 1200,
            "published_at": "2026-03-01",
            "blurb": "Ship **admin** UIs *fast*.",
            "notes": "Copy me",
        },
        {
            "id": 2,
            "name": "Conduit",
            "status": "draft",
            "amount": 340,
            "published_at": "2026-04-12",
            "blurb": "Live morph without the SPA tax.",
            "notes": "Hello",
        },
    ]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("name")])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns(
            [
                TextColumn.make("name")
                .searchable()
                .weight("bold")
                .icon("heroicon-o-check")
                .description(lambda record=None, **_: (record or {}).get("status", "")),
                TextColumn.make("status").badge(),
                TextColumn.make("amount").money("USD").align_end(),
                TextColumn.make("published_at").date("%b %d, %Y"),
                TextColumn.make("blurb").markdown().wrap(),
                TextColumn.make("notes").copyable(),
            ]
        )
