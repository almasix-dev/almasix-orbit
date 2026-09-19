"""Tables overview showcase — Filament 5 overview parity APIs."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.actions import CreateAction, DeleteBulkAction, EditAction
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import PaginationMode, Table, TextColumn


class TablesOverviewResource(Resource):
    """Focused sample for tables/overview (heading, dots, pagination, reorder, …)."""

    navigation_label = "Tables overview"
    navigation_group = "Columns"
    navigation_icon = "heroicon-o-table-cells"
    navigation_sort = 0
    records_mutable = True

    records: ClassVar[list[dict[str, Any]]] = [
        {
            "id": 1,
            "title": "Orbit ships",
            "status": "published",
            "sort": 1,
            "author": {"name": "Ada Lovelace"},
        },
        {
            "id": 2,
            "title": "Draft notes",
            "status": "draft",
            "sort": 2,
            "author": {"name": "Grace Hopper"},
        },
        {
            "id": 3,
            "title": "Review queue",
            "status": "reviewing",
            "sort": 3,
            "author": {"name": "Katherine Johnson"},
        },
    ]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("title").required(),
                TextInput.make("status"),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.heading("Posts")
            .description("Tables overview — searchable columns, pagination, reorder.")
            .columns(
                [
                    TextColumn.make("title").searchable().sortable(),
                ]
            )
            .push_columns(
                [
                    TextColumn.make("author.name").label("Author").sortable(),
                    TextColumn.make("status").badge().sortable(),
                ]
            )
            .default_sort("sort")
            .paginated([5, 10, 25, "all"])
            .default_pagination_page_option(10)
            .extreme_pagination_links()
            .pagination_mode(PaginationMode.DEFAULT)
            .query_string_identifier("overview")
            .record_actions([EditAction.make()])
            .toolbar_actions([DeleteBulkAction.make()])
            .header_actions([CreateAction.make()])
            .record_url(lambda record: f"/tables-overview/{record['id']}")
            .record_classes(
                lambda record: {
                    "draft": "or-row-draft",
                    "reviewing": "or-row-reviewing",
                    "published": "or-row-published",
                }.get(str(record.get("status") or ""), None)
            )
            .reorderable("sort")
            .empty_state_heading("No posts yet")
            .empty_state_description("Create a post to exercise the overview table.")
            .empty_state_icon("heroicon-o-document-text")
            .empty_state_actions([CreateAction.make()])
            .striped()
        )
