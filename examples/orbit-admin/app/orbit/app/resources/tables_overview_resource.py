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
            "title": "Launch Orbit",
            "status": "published",
            "sort": 1,
            "author": {"name": "Ada Lovelace"},
        },
        {
            "id": 2,
            "title": "Conduit hosts",
            "status": "draft",
            "sort": 2,
            "author": {"name": "Grace Hopper"},
        },
        {
            "id": 3,
            "title": "Mobile tables",
            "status": "reviewing",
            "sort": 3,
            "author": {"name": "Katherine Johnson"},
        },
        {
            "id": 4,
            "title": "Panel chrome",
            "status": "published",
            "sort": 4,
            "author": {"name": "Ada Lovelace"},
        },
        {
            "id": 5,
            "title": "Form fields",
            "status": "published",
            "sort": 5,
            "author": {"name": "Margaret Hamilton"},
        },
        {
            "id": 6,
            "title": "Action modals",
            "status": "draft",
            "sort": 6,
            "author": {"name": "Grace Hopper"},
        },
        {
            "id": 7,
            "title": "Global search",
            "status": "reviewing",
            "sort": 7,
            "author": {"name": "Dorothy Vaughan"},
        },
        {
            "id": 8,
            "title": "Theme tokens",
            "status": "published",
            "sort": 8,
            "author": {"name": "Katherine Johnson"},
        },
        {
            "id": 9,
            "title": "Empty states",
            "status": "draft",
            "sort": 9,
            "author": {"name": "Ada Lovelace"},
        },
        {
            "id": 10,
            "title": "Bulk delete",
            "status": "published",
            "sort": 10,
            "author": {"name": "Margaret Hamilton"},
        },
        {
            "id": 11,
            "title": "Query builder",
            "status": "reviewing",
            "sort": 11,
            "author": {"name": "Dorothy Vaughan"},
        },
        {
            "id": 12,
            "title": "Infolist entries",
            "status": "published",
            "sort": 12,
            "author": {"name": "Grace Hopper"},
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
