"""Albums resource — flagship Orbit Records catalog resource."""

from __future__ import annotations

from typing import Any

from almasix.orbit import Resource
from almasix.orbit.actions import ExportAction, ImportAction
from almasix.orbit.forms import (
    Checkbox,
    DatePicker,
    DateTimePicker,
    FileUpload,
    Form,
    KeyValue,
    ModalTableSelect,
    MoneyInput,
    MultiSelect,
    Placeholder,
    Radio,
    RichEditor,
    Slider,
    TextInput,
    ToggleButtons,
)
from almasix.orbit.infolists import (
    IconEntry,
    ImageEntry,
    Infolist,
    KeyValueEntry,
    TextEntry,
)
from almasix.orbit.panels.pages import Tab
from almasix.orbit.query_builder import (
    BooleanConstraint,
    NumberConstraint,
    QueryBuilder,
    SelectConstraint,
    TextConstraint,
)
from almasix.orbit.schemas import Callout, Fieldset, Section, Tabs, Wizard
from almasix.orbit.tables import (
    Average,
    Count,
    Filter,
    FilterGroup,
    ImageColumn,
    QueryBuilderFilter,
    SelectFilter,
    Sum,
    Table,
    TextColumn,
)

from app.models.album import Album
from app.orbit.demo.relations.tracks_relation_manager import TracksRelationManager
from app.orbit.demo.resources.artist_resource import ArtistResource

_FORMATS = {
    "digital": "Digital",
    "streaming": "Streaming",
    "cd": "CD",
    "vinyl": "Vinyl",
}

_MARKETS = {
    "US": "United States",
    "CA": "Canada",
    "EU": "Europe",
    "KE": "Kenya",
    "PT": "Portugal",
    "JP": "Japan",
    "BR": "Brazil",
}


class AlbumResource(Resource):
    model = Album
    navigation_label = "Albums"
    navigation_group = "Catalog"
    navigation_icon = "heroicon-o-rectangle-stack"
    navigation_sort = 2
    record_title_attribute = "title"
    global_search_attributes = ("title",)
    global_search_result_details = ("status", "year")

    @classmethod
    def get_relations(cls) -> list[type[Any]]:
        return [TracksRelationManager]

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
                Callout.make()
                .info()
                .label("Release wizard")
                .description(
                    "Step through details, artwork, and liner notes. "
                    "Tracks are managed from the album relation manager after save."
                ),
                Wizard.make("release")
                .skippable()
                .steps(
                    (
                        "Details",
                        [
                            Section.make("basics")
                            .heading("Basics")
                            .schema(
                                [
                                    TextInput.make("title").required().max_length(200),
                                    ModalTableSelect.make("artist_id")
                                    .label("Artist")
                                    .records(ArtistResource.get_records)
                                    .title_attribute("name")
                                    .browse_label("Browse artists")
                                    .modal_heading("Pick an artist")
                                    .helper_text("Opens the artists table in a modal."),
                                    TextInput.make("year").numeric().label("Year"),
                                    ToggleButtons.make("status")
                                    .options(
                                        {"draft": "Draft", "released": "Released"}
                                    )
                                    .required(),
                                    Placeholder.make("hint").content(
                                        "Use Released when the album is public in the catalog."
                                    ),
                                ]
                            ),
                            Fieldset.make()
                            .label("Schedule")
                            .schema(
                                [
                                    DatePicker.make("released_at").label("Release date"),
                                    DateTimePicker.make("published_at").label(
                                        "Published at"
                                    ),
                                ]
                            ),
                        ],
                    ),
                    (
                        "Artwork & pricing",
                        [
                            Tabs.make("commerce")
                            .tabs(
                                (
                                    "Media",
                                    [
                                        FileUpload.make("cover")
                                        .label("Cover art")
                                        .image()
                                        .directory("album-covers")
                                        .max_size(4096)
                                        .panel_layout()
                                        .image_preview_height(180)
                                        .image_editor()
                                        .image_editor_aspect_ratios(["1:1", "16:9"])
                                        .openable()
                                        .downloadable(),
                                        Radio.make("format")
                                        .options(_FORMATS)
                                        .options_columns(2)
                                        .label("Format"),
                                        Slider.make("rating")
                                        .label("Internal rating")
                                        .min_value(0)
                                        .max_value(100)
                                        .pips(),
                                        Checkbox.make("featured").label(
                                            "Featured on Insights"
                                        ),
                                    ],
                                ),
                                (
                                    "Commerce",
                                    [
                                        MoneyInput.make("price_cents")
                                        .currency("USD")
                                        .label("Price (cents)")
                                        .step("1")
                                        .helper_text(
                                            "Stored as integer cents (e.g. 1299 = $12.99)."
                                        ),
                                        TextInput.make("currency")
                                        .label("Currency")
                                        .default("USD")
                                        .max_length(3),
                                        MultiSelect.make("markets")
                                        .label("Markets")
                                        .options(_MARKETS)
                                        .searchable(),
                                    ],
                                ),
                            ),
                        ],
                    ),
                    (
                        "Notes",
                        [
                            RichEditor.make("liner_notes")
                            .label("Liner notes")
                            .toolbar_buttons(
                                [
                                    "bold",
                                    "italic",
                                    "h2",
                                    "bulletList",
                                    "orderedList",
                                    "link",
                                    "undo",
                                ]
                            )
                            .placeholder("Write the liner notes…")
                            .min_height("12rem"),
                            KeyValue.make("credits")
                            .label("Credits")
                            .key_label("Role")
                            .value_label("Name")
                            .add_action_label("Add credit"),
                            KeyValue.make("meta")
                            .label("Metadata")
                            .key_label("Attribute")
                            .value_label("Value")
                            .add_action_label("Add attribute"),
                        ],
                    ),
                ),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.columns(
                [
                    ImageColumn.make("cover").label("").square().size(40),
                    TextColumn.make("title").searchable().sortable(),
                    TextColumn.make("year").sortable().toggleable(),
                    TextColumn.make("status").badge().sortable(),
                    TextColumn.make("format").toggleable(),
                    TextColumn.make("price_cents")
                    .label("Price")
                    .money("USD", divide_by=100)
                    .sortable()
                    .align_end()
                    .summarize(
                        Sum.make().money("USD", divide_by=100).label("Total"),
                        Average.make().money("USD", divide_by=100),
                        Count.make(),
                    ),
                    TextColumn.make("rating").label("Rating").sortable().toggleable(),
                    TextColumn.make("featured")
                    .label("Featured")
                    .badge()
                    .toggleable(is_toggled_hidden_by_default=True),
                ]
            )
            .filters(
                [
                    FilterGroup.make("catalog")
                    .label("Catalog")
                    .filters(
                        [
                            SelectFilter.make("status")
                            .label("Status")
                            .options(
                                {"draft": "Draft", "released": "Released"}
                            ),
                            SelectFilter.make("format")
                            .label("Format")
                            .options(_FORMATS),
                            Filter.make("featured")
                            .label("Featured only")
                            .toggle()
                            .query(
                                lambda q, value: [
                                    r
                                    for r in q
                                    if (
                                        r.get("featured")
                                        if isinstance(r, dict)
                                        else getattr(r, "featured", False)
                                    )
                                ]
                            ),
                        ]
                    ),
                    QueryBuilderFilter.make("query")
                    .label("Rules")
                    .builder(
                        QueryBuilder.make()
                        .constraints(
                            [
                                TextConstraint.make("title").label("Title"),
                                SelectConstraint.make("status")
                                .label("Status")
                                .options(
                                    {"draft": "Draft", "released": "Released"}
                                ),
                                NumberConstraint.make("year").label("Year"),
                                NumberConstraint.make("price_cents").label(
                                    "Price (cents)"
                                ),
                                BooleanConstraint.make("featured").label("Featured"),
                            ]
                        )
                    ),
                ]
            )
            .defer_filters()
            .persist_filters_in_session()
            .stacked_on_mobile()
            .header_actions(
                [
                    ImportAction.make()
                    .column_map(
                        {
                            "Title": "title",
                            "Status": "status",
                            "Year": "year",
                            "Price": "price_cents",
                        }
                    )
                    .chunk_size(100),
                    ExportAction.make()
                    .formats(["csv", "json"])
                    .columns(["title", "status", "year", "price_cents", "format"])
                    .filename("albums"),
                ]
            )
        )

    @classmethod
    def infolist(cls, infolist: Infolist) -> Infolist:
        return infolist.columns(2).schema(
            [
                Section.make("release")
                .heading("Release")
                .schema(
                    [
                        ImageEntry.make("cover").label("Cover").size(72),
                        TextEntry.make("title").label("Title").weight("bold").size("lg"),
                        TextEntry.make("status").label("Status").badge().color(
                            lambda state, **_: {
                                "released": "success",
                                "draft": "warning",
                            }.get(str(state), "gray")
                        ),
                        TextEntry.make("year").label("Year"),
                        TextEntry.make("format").label("Format"),
                        TextEntry.make("price_cents")
                        .label("Price")
                        .money("USD", divide_by=100),
                        TextEntry.make("released_at").label("Released").date("%b %d, %Y"),
                        TextEntry.make("published_at")
                        .label("Published")
                        .date_time("%b %d, %Y %H:%M"),
                        IconEntry.make("featured").label("Featured").boolean(),
                        TextEntry.make("rating").label("Rating"),
                    ]
                ),
                Section.make("copy")
                .heading("Copy & credits")
                .schema(
                    [
                        TextEntry.make("liner_notes")
                        .label("Liner notes")
                        .html()
                        .column_span(2),
                        KeyValueEntry.make("credits")
                        .label("Credits")
                        .key_label("Role")
                        .value_label("Name"),
                        KeyValueEntry.make("meta")
                        .label("Metadata")
                        .key_label("Attribute")
                        .value_label("Value"),
                        TextEntry.make("markets").label("Markets").badge().separator(", "),
                    ]
                ),
            ]
        )
