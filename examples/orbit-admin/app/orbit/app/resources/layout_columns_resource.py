"""Layout Split / Stack / Panel / Grid / View + ColumnGroup + Tags."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import (
    ColumnGroup,
    Grid,
    Panel,
    Split,
    Stack,
    Table,
    TagsColumn,
    TextColumn,
    View,
    ViewColumn,
)


class LayoutColumnsResource(Resource):
    model = type("LayoutDemo", (), {})
    slug = "layout-columns"
    navigation_label = "Layout columns"
    navigation_group = "Columns"
    navigation_icon = "heroicon-o-view-columns"
    navigation_sort = 4

    records: ClassVar[list[dict[str, Any]]] = [
        {
            "id": 1,
            "title": "Orbit shell",
            "subtitle": "Sidebar + topbar",
            "tags": ["shell", "nav", "chrome", "topbar"],
            "meta_a": "A",
            "meta_b": "B",
            "note": "Custom view cell",
            "progress": 80,
        },
        {
            "id": 2,
            "title": "Table chrome",
            "subtitle": "Filters + columns",
            "tags": "tables;ux",
            "meta_a": "X",
            "meta_b": "Y",
            "note": "Another view",
            "progress": 45,
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
                Split.make(
                    [
                        Stack.make(
                            [
                                TextColumn.make("title").weight("semibold"),
                                TextColumn.make("subtitle").color("gray"),
                            ]
                        ),
                        TagsColumn.make("tags").separator(";").limit(3).color("primary"),
                    ]
                ).label("Content"),
                ColumnGroup.make(
                    "Meta",
                    [
                        TextColumn.make("meta_a").label("A"),
                        TextColumn.make("meta_b").label("B"),
                    ],
                ).align_end().wrap_header(),
                Panel.make([TextColumn.make("note")]).label("Panel"),
                Grid.make(
                    [
                        TextColumn.make("meta_a").label("G1"),
                        TextColumn.make("meta_b").label("G2"),
                    ]
                )
                .columns(2)
                .label("Grid"),
                View.make([TextColumn.make("subtitle")])
                .content('<div class="or-layout-view-demo">{children}</div>')
                .label("Layout view"),
                ViewColumn.make("progress")
                .content(lambda state=None, **_: f'<em class="or-view-column">{int(state or 0)}%</em>')
                .url(lambda record=None, **_: f"/projects/{record.get('id')}")
                .open_url_in_new_tab()
                .label("Progress"),
            ]
        )
