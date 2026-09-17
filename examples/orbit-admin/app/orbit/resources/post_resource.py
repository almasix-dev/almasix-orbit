"""Posts resource."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.forms import Form, Select, TextInput, Textarea
from almasix.orbit.panels.pages import Tab
from almasix.orbit.tables import Average, Count, SelectFilter, Sum, Table, TextColumn


class PostResource(Resource):
    model = type("Post", (), {})
    navigation_label = "Posts"
    navigation_group = "Content"
    navigation_icon = "heroicon-o-pencil-square"
    navigation_sort = 1

    records: ClassVar[list[dict[str, Any]]] = [
        {"id": 1, "title": "Launch Orbit", "status": "published", "amount": 1200},
        {"id": 2, "title": "Conduit hosts", "status": "draft", "amount": 120},
        {"id": 3, "title": "Mobile tables", "status": "review", "amount": 450},
        {"id": 4, "title": "Panel branding", "status": "published", "amount": 880},
        {"id": 5, "title": "Auth signup flow", "status": "published", "amount": 640},
        {"id": 6, "title": "Dashboard widgets", "status": "draft", "amount": 90},
        {"id": 7, "title": "Filter chrome", "status": "review", "amount": 330},
        {"id": 8, "title": "Bulk actions", "status": "draft", "amount": 170},
        {"id": 9, "title": "Empty states", "status": "review", "amount": 210},
        {"id": 10, "title": "Content grid cards", "status": "draft", "amount": 140},
        {"id": 11, "title": "Sortable columns", "status": "published", "amount": 560},
        {"id": 12, "title": "Pagination footer", "status": "published", "amount": 410},
        {"id": 13, "title": "Search toolbar", "status": "review", "amount": 280},
        {"id": 14, "title": "Relation managers", "status": "draft", "amount": 70},
    ]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def get_tabs(cls) -> list[Tab]:
        def count_status(status: str) -> int:
            return sum(1 for r in cls.get_records() if r.get("status") == status)

        return [
            Tab("all").label("All").badge(lambda: len(cls.get_records())),
            Tab("published")
            .label("Published")
            .badge(lambda: count_status("published"))
            .badge_color("success")
            .modify_query_using(
                lambda rows: [r for r in rows if r.get("status") == "published"]
            ),
            Tab("draft")
            .label("Draft")
            .badge(lambda: count_status("draft"))
            .modify_query_using(
                lambda rows: [r for r in rows if r.get("status") == "draft"]
            ),
        ]

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
        return (
            table.columns(
                [
                    TextColumn.make("title").searchable().sortable(),
                    TextColumn.make("status").badge().sortable().toggleable(),
                    TextColumn.make("amount")
                    .label("Amount")
                    .money("USD")
                    .sortable()
                    .align_end()
                    .toggleable()
                    .summarize(
                        Sum.make(),
                        Average.make(),
                        Count.make(),
                    ),
                ]
            )
            .filters(
                [
                    SelectFilter.make("status")
                    .label("Status")
                    .options(
                        {
                            "draft": "Draft",
                            "review": "Review",
                            "published": "Published",
                        }
                    ),
                ]
            )
            .defer_filters()
            .stacked_on_mobile()
        )
