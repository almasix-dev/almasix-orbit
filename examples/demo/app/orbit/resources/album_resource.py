"""Albums resource — ORM-backed CRUD with artist relationship Select."""

from __future__ import annotations

from typing import Any

from almasix.orbit import Resource
from almasix.orbit.forms import Form, Select, TextInput
from almasix.orbit.panels.pages import Tab
from almasix.orbit.tables import SelectFilter, Table, TextColumn

from app.models.album import Album
from app.models.artist import Artist


class AlbumResource(Resource):
    model = Album
    navigation_label = "Albums"
    navigation_group = "Catalog"
    navigation_icon = "heroicon-o-rectangle-stack"
    navigation_sort = 2
    record_title_attribute = "title"

    @classmethod
    def get_tabs(cls) -> list[Tab]:
        def count_status(status: str, records: list[Any] | None = None, **_: Any) -> int:
            rows = records or []
            return sum(
                1
                for r in rows
                if (r.get("status") if isinstance(r, dict) else getattr(r, "status", None))
                == status
            )

        return [
            Tab("all").label("All").badge(lambda records=None, **_: len(records or [])),
            Tab("released")
            .label("Released")
            .badge(lambda records=None, **kw: count_status("released", records, **kw))
            .badge_color("success")
            .modify_query_using(
                lambda rows: [
                    r
                    for r in rows
                    if (r.get("status") if isinstance(r, dict) else getattr(r, "status", None))
                    == "released"
                ]
            ),
            Tab("draft")
            .label("Draft")
            .badge(lambda records=None, **kw: count_status("draft", records, **kw))
            .modify_query_using(
                lambda rows: [
                    r
                    for r in rows
                    if (r.get("status") if isinstance(r, dict) else getattr(r, "status", None))
                    == "draft"
                ]
            ),
        ]

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("title").required().max_length(200),
                Select.make("artist_id")
                .label("Artist")
                .relationship("artist", "name")
                .searchable()
                .required(),
                TextInput.make("year").numeric().label("Year"),
                Select.make("status")
                .options({"draft": "Draft", "released": "Released"})
                .required(),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        def artist_label(value: Any) -> str:
            if value in (None, ""):
                return "—"
            try:
                from almasix.orbit.forms.select_relationship import load_relationship_options

                opts = load_relationship_options(
                    model=Artist,
                    title_attribute="name",
                    keys=[value],
                    limit=1,
                )
                return opts.get(str(value), str(value))
            except Exception:
                return str(value)

        return (
            table.columns(
                [
                    TextColumn.make("title").searchable().sortable(),
                    TextColumn.make("artist_id")
                    .label("Artist")
                    .format_state_using(artist_label)
                    .sortable(),
                    TextColumn.make("year").sortable().toggleable(),
                    TextColumn.make("status").badge().sortable().toggleable(),
                ]
            )
            .filters(
                [
                    SelectFilter.make("status")
                    .label("Status")
                    .options({"draft": "Draft", "released": "Released"}),
                ]
            )
            .defer_filters()
            .stacked_on_mobile()
        )
