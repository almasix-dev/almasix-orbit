"""Text column gallery — Filament-parity TextColumn helpers."""

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
            "role": "admin kit",
            "status": "published",
            "amount": 1200,
            "published_at": "2026-03-01",
            "last_seen_at": "2026-09-18T09:40:00",
            "score": 98.5,
            "blurb": "Ship **admin** UIs *fast*.",
            "notes": "Copy me",
            "reference": "ORB-1001",
            "tags": "docs,ui,tables",
        },
        {
            "id": 2,
            "name": "Conduit",
            "role": "live morph",
            "status": "draft",
            "amount": 340,
            "published_at": "2026-04-12",
            "last_seen_at": "2026-09-10T14:05:00",
            "score": 76.25,
            "blurb": "Live morph without the SPA tax.",
            "notes": "Hello",
            "reference": "ORB-1002",
            "tags": "conduit,live",
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
                .icon_color("primary")
                .description(lambda record=None, **_: (record or {}).get("role", "")),
                TextColumn.make("status")
                .badge()
                .icon_position("after")
                .icon("heroicon-o-chevron-down")
                .color(
                    lambda state=None, **_: {"published": "success", "draft": "gray"}.get(
                        state, "gray"
                    )
                ),
                TextColumn.make("amount").money("USD").align_end(),
                TextColumn.make("published_at").date("%b %d, %Y"),
                TextColumn.make("last_seen_at").since(),
                TextColumn.make("score").numeric(decimal_places=1).align_end(),
                TextColumn.make("tags").separator(",").badge().color("info"),
                TextColumn.make("blurb").markdown().wrap().line_clamp(2),
                TextColumn.make("reference").copyable().copy_message("Reference copied").font_family(
                    "mono"
                ),
                TextColumn.make("notes").words(3).size("sm"),
            ]
        )
