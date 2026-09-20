"""Posts resource — ORM-backed CRUD (create / edit / delete against SQLite)."""

from __future__ import annotations

from typing import Any

from almasix.orbit import Resource
from almasix.orbit.forms import (
    FileUpload,
    Form,
    KeyValue,
    ModalTableSelect,
    RichEditor,
    Select,
    TextInput,
)
from almasix.orbit.panels.pages import Tab
from almasix.orbit.tables import Average, Count, Filter, FilterGroup, SelectFilter, Sum, Table, TextColumn

from app.models.post import Post
from app.orbit.app.relations.comments_relation_manager import CommentsRelationManager
from app.orbit.app.resources.author_resource import AuthorResource


class PostResource(Resource):
    model = Post
    navigation_label = "Posts"
    navigation_group = "Content"
    navigation_icon = "heroicon-o-pencil-square"
    navigation_sort = 1
    record_title_attribute = "title"
    model_label = "Post"
    global_search_attributes = ("title", "body")
    global_search_result_details = ("status",)

    @classmethod
    def get_relations(cls) -> list[type[Any]]:
        return [CommentsRelationManager]

    @classmethod
    def get_tabs(cls) -> list[Tab]:
        def count_status(status: str, records: list[Any] | None = None, **_: Any) -> int:
            rows = records or []
            return sum(1 for r in rows if (r.get("status") if isinstance(r, dict) else getattr(r, "status", None)) == status)

        return [
            Tab("all").label("All").badge(lambda records=None, **_: len(records or [])),
            Tab("published")
            .label("Published")
            .badge(lambda records=None, **kw: count_status("published", records, **kw))
            .badge_color("success")
            .modify_query_using(
                lambda rows: [
                    r
                    for r in rows
                    if (r.get("status") if isinstance(r, dict) else getattr(r, "status", None))
                    == "published"
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
                Select.make("status")
                .options({"draft": "Draft", "review": "Review", "published": "Published"})
                .required(),
                TextInput.make("amount").numeric().label("Amount"),
                ModalTableSelect.make("author_id")
                .label("Author")
                .records(AuthorResource.get_records)
                .title_attribute("name")
                .browse_label("Browse authors")
                .modal_heading("Pick an author")
                .helper_text("Opens the authors table in a modal."),
                FileUpload.make("cover")
                .label("Cover image")
                .image()
                .directory("post-covers")
                .max_size(2048)
                .image_preview()
                .openable()
                .downloadable(),
                RichEditor.make("body")
                .toolbar_buttons(
                    ["bold", "italic", "h2", "bulletList", "orderedList", "link", "undo"]
                )
                .placeholder("Write the post…")
                .merge_tags(["author_name", "site_name"])
                .min_height("16rem"),
                KeyValue.make("meta")
                .label("Metadata")
                .key_label("Attribute")
                .value_label("Value")
                .key_placeholder("e.g. reading_time")
                .value_placeholder("e.g. 4 min")
                .add_action_label("Add attribute"),
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
                    FilterGroup.make("visibility")
                    .label("Visibility")
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
                            Filter.make("has_body")
                            .label("Has body")
                            .toggle()
                            .query(
                                lambda q, value: [
                                    r
                                    for r in q
                                    if (
                                        r.get("body")
                                        if isinstance(r, dict)
                                        else getattr(r, "body", None)
                                    )
                                ]
                            ),
                        ]
                    ),
                ]
            )
            .defer_filters()
            .persist_filters_in_session()
            .stacked_on_mobile()
        )
