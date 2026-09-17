"""Grouped posts — demonstrates default_group + collapsible headers."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.forms import Form, Select, TextInput
from almasix.orbit.tables import Group, Table, TextColumn


class GroupedPostsResource(Resource):
    model = type("GroupedPost", (), {})
    slug = "grouped-posts"
    navigation_label = "Grouped rows"
    navigation_group = "Columns"
    navigation_icon = "heroicon-o-bars-3"
    navigation_sort = 20

    records: ClassVar[list[dict[str, Any]]] = [
        {"id": 1, "title": "Launch Orbit", "status": "published"},
        {"id": 2, "title": "Conduit hosts", "status": "draft"},
        {"id": 3, "title": "Mobile tables", "status": "review"},
        {"id": 4, "title": "Panel branding", "status": "published"},
        {"id": 5, "title": "Auth signup", "status": "published"},
        {"id": 6, "title": "Dashboard widgets", "status": "draft"},
        {"id": 7, "title": "Filter chrome", "status": "review"},
        {"id": 8, "title": "Bulk actions", "status": "draft"},
    ]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("title").required(),
                Select.make("status")
                .options({"draft": "Draft", "review": "Review", "published": "Published"})
                .required(),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.columns(
                [
                    TextColumn.make("title").searchable().sortable(),
                    TextColumn.make("status").badge().sortable(),
                ]
            )
            .default_group(Group.make("status").label("Status").collapsible())
            .collapsed_groups_by_default(False)
        )
