"""Columns overview showcase — shared Column APIs (Filament columns/overview)."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.actions import CreateAction, EditAction
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import Table, TextColumn


class ColumnsOverviewResource(Resource):
    """Focused sample for tables/columns/overview shared helpers."""

    navigation_label = "Columns overview"
    navigation_group = "Columns"
    navigation_icon = "heroicon-o-view-columns"
    navigation_sort = 1
    records_mutable = True

    records: ClassVar[list[dict[str, Any]]] = [
        {
            "id": 1,
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@example.com",
            "nickname": None,
            "website": "https://almasix.com",
        },
        {
            "id": 2,
            "first_name": "Grace",
            "last_name": "Hopper",
            "email": "grace@example.com",
            "nickname": "Amazing Grace",
            "website": "https://docs.almasix.com",
        },
        {
            "id": 3,
            "first_name": "Katherine",
            "last_name": "Johnson",
            "email": "katherine@example.com",
            "nickname": "",
            "website": None,
        },
        {
            "id": 4,
            "first_name": "Margaret",
            "last_name": "Hamilton",
            "email": "margaret@example.com",
            "nickname": None,
            "website": "https://orbit.almasix.com",
        },
    ]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("first_name").required(),
                TextInput.make("last_name").required(),
                TextInput.make("email"),
                TextInput.make("nickname"),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.heading("Columns overview")
            .description(
                "Shared Column APIs: state, placeholder, multi-key sort/search, "
                "tooltips, width/grow, toggle + reorder."
            )
            .reorderable_columns()
            .columns(
                [
                    TextColumn.make("full_name")
                    .label("Full name")
                    .state(
                        lambda record: f"{record.get('first_name', '')} {record.get('last_name', '')}".strip()
                    )
                    .sortable(["last_name", "first_name"])
                    .searchable(["first_name", "last_name", "email"])
                    .wrap_header()
                    .grow()
                    .header_tooltip("Sorted by last name, then first name")
                    .tooltip(lambda record, **_: f"ID {record.get('id')}"),
                    TextColumn.make("nickname")
                    .placeholder("No nickname")
                    .default("—")
                    .toggleable()
                    .width(140),
                    TextColumn.make("email")
                    .searchable()
                    .sortable()
                    .url(lambda record, **_: f"mailto:{record.get('email')}")
                    .toggleable(),
                    TextColumn.make("website")
                    .label("Site")
                    .placeholder("—")
                    .url(lambda record, state, **_: state or "#")
                    .open_url_in_new_tab()
                    .toggleable(is_toggled_hidden_by_default=True)
                    .vertically_align_center()
                    .extra_cell_attributes({"data-col": "website"}),
                    TextColumn.make("hidden_note")
                    .state("secret")
                    .hidden(),
                ]
            )
            .header_actions([CreateAction.make()])
            .record_actions([EditAction.make()])
            .paginated([5, 10])
            .default_sort("full_name")
        )
