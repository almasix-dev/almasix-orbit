"""Posts resource."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.forms import Form, Select, TextInput, Textarea
from almasix.orbit.tables import Table, TextColumn


class PostResource(Resource):
    model = type("Post", (), {})
    navigation_label = "Posts"
    navigation_group = "Content"
    navigation_icon = "heroicon-o-pencil-square"
    navigation_sort = 1

    records: ClassVar[list[dict[str, Any]]] = [
        {"id": 1, "title": "Launch Orbit", "status": "published"},
        {"id": 2, "title": "Conduit hosts", "status": "draft"},
        {"id": 3, "title": "Mobile tables", "status": "review"},
        {"id": 4, "title": "Panel branding", "status": "published"},
        {"id": 5, "title": "Auth signup flow", "status": "published"},
        {"id": 6, "title": "Dashboard widgets", "status": "draft"},
        {"id": 7, "title": "Filter chrome", "status": "review"},
        {"id": 8, "title": "Bulk actions", "status": "draft"},
        {"id": 9, "title": "Empty states", "status": "review"},
        {"id": 10, "title": "Content grid cards", "status": "draft"},
        {"id": 11, "title": "Sortable columns", "status": "published"},
        {"id": 12, "title": "Pagination footer", "status": "published"},
        {"id": 13, "title": "Search toolbar", "status": "review"},
        {"id": 14, "title": "Relation managers", "status": "draft"},
    ]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("title").required().max_length(200),
                Select.make("status")
                .options({"draft": "Draft", "review": "Review", "published": "Published"})
                .required(),
                Textarea.make("body").rows(6),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns(
            [
                TextColumn.make("title").searchable().sortable(),
                TextColumn.make("status").badge(),
            ]
        ).stacked_on_mobile()
