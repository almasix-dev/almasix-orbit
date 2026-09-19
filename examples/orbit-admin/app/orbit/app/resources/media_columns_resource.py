"""Icon / Image / Color column gallery — Filament-parity IconColumn, ImageColumn, ColorColumn."""

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
            "verified": True,
            "icon": "heroicon-o-check",
            "avatar": "https://api.dicebear.com/9.x/shapes/svg?seed=ada",
            "avatars": [
                "https://api.dicebear.com/9.x/shapes/svg?seed=a",
                "https://api.dicebear.com/9.x/shapes/svg?seed=b",
                "https://api.dicebear.com/9.x/shapes/svg?seed=c",
                "https://api.dicebear.com/9.x/shapes/svg?seed=d",
            ],
            "color": "#f1511b",
        },
        {
            "id": 2,
            "name": "Grace",
            "active": False,
            "verified": False,
            "icon": "heroicon-o-plus",
            "avatar": "https://api.dicebear.com/9.x/shapes/svg?seed=grace",
            "avatars": [
                "https://api.dicebear.com/9.x/shapes/svg?seed=e",
                "https://api.dicebear.com/9.x/shapes/svg?seed=f",
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
                ImageColumn.make("avatar")
                .circular()
                .size(36)
                .ring(2)
                .alt(lambda record=None, **_: f"{record.get('name', '')}'s avatar")
                .extra_img_attributes({"loading": "lazy"}),
                ImageColumn.make("avatars")
                .stacked()
                .limit(3)
                .circular()
                .size(28)
                .overlap("0.6rem"),
                IconColumn.make("icon").color("primary"),
                BooleanColumn.make("active").label("On").true_color("success").false_color("gray"),
                IconColumn.make("verified")
                .boolean()
                .true_icon("heroicon-o-check")
                .false_icon("heroicon-o-x-mark")
                .true_color("info")
                .false_color("danger"),
                ColorColumn.make("color").copyable().copy_message("Color copied"),
            ]
        )
