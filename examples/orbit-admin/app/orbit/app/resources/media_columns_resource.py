"""Icon / Image / Color column gallery."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import BooleanColumn, ColorColumn, IconColumn, ImageColumn, Table, TextColumn


class MediaColumnsResource(Resource):
    model = type("MediaDemo", (), {})
    slug = "media-columns"
    navigation_label = "Media columns"
    navigation_group = "Columns"
    navigation_icon = "heroicon-o-view-columns"
    navigation_sort = 2

    records: ClassVar[list[dict[str, Any]]] = [
        {
            "id": 1,
            "name": "Ada",
            "active": True,
            "icon": "heroicon-o-check",
            "avatar": "https://api.dicebear.com/9.x/shapes/svg?seed=ada",
            "avatars": [
                "https://api.dicebear.com/9.x/shapes/svg?seed=a",
                "https://api.dicebear.com/9.x/shapes/svg?seed=b",
                "https://api.dicebear.com/9.x/shapes/svg?seed=c",
            ],
            "color": "#f1511b",
        },
        {
            "id": 2,
            "name": "Grace",
            "active": False,
            "icon": "heroicon-o-plus",
            "avatar": "https://api.dicebear.com/9.x/shapes/svg?seed=grace",
            "avatars": [
                "https://api.dicebear.com/9.x/shapes/svg?seed=d",
                "https://api.dicebear.com/9.x/shapes/svg?seed=e",
            ],
            "color": "#286291",
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
                TextColumn.make("name"),
                ImageColumn.make("avatar").circular().size(36),
                ImageColumn.make("avatars").stacked().limit(2).circular().size(28),
                IconColumn.make("icon"),
                BooleanColumn.make("active").label("On"),
                ColorColumn.make("color").copyable(),
            ]
        )
