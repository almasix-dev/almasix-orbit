"""Artists resource — rich form / table / infolist for the catalog."""

from __future__ import annotations

from typing import Any

from almasix.orbit import Resource
from almasix.orbit.forms import (
    CheckboxList,
    ColorPicker,
    FileUpload,
    Form,
    Select,
    TagsInput,
    Textarea,
    TextInput,
    Toggle,
)
from almasix.orbit.infolists import (
    ColorEntry,
    IconEntry,
    ImageEntry,
    Infolist,
    TextEntry,
)
from almasix.orbit.schemas import Grid, Section
from almasix.orbit.tables import (
    BooleanColumn,
    ColorColumn,
    ImageColumn,
    Table,
    TagsColumn,
    TextColumn,
)

from app.models.artist import Artist
from app.orbit.demo.catalog_metrics import artist_picker_rows
from app.orbit.demo.relations.albums_relation_manager import AlbumsRelationManager

_COUNTRIES = {
    "Kenya": "Kenya",
    "Canada": "Canada",
    "Germany": "Germany",
    "Portugal": "Portugal",
    "Japan": "Japan",
    "Brazil": "Brazil",
    "Ireland": "Ireland",
    "United States": "United States",
}

_PLATFORMS = {
    "spotify": "Spotify",
    "apple": "Apple Music",
    "bandcamp": "Bandcamp",
    "soundcloud": "SoundCloud",
}


class ArtistResource(Resource):
    model = Artist
    navigation_label = "Artists"
    navigation_group = "Catalog"
    navigation_icon = "heroicon-o-user-group"
    navigation_sort = 1
    record_title_attribute = "name"
    global_search_attributes = ("name", "country")
    global_search_result_details = ("country",)

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return artist_picker_rows()

    @classmethod
    def get_relations(cls) -> list[type[Any]]:
        return [AlbumsRelationManager]

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                Section.make("profile")
                .heading("Profile")
                .schema(
                    [
                        Grid.make()
                        .columns(2)
                        .schema(
                            [
                                TextInput.make("name").required().max_length(200),
                                Select.make("country").options(_COUNTRIES).searchable(),
                                TextInput.make("website").url().label("Website"),
                                ColorPicker.make("brand_color").label("Brand color"),
                            ]
                        ),
                        Textarea.make("bio").rows(4),
                        FileUpload.make("avatar")
                        .label("Avatar")
                        .avatar()
                        .disk("public")
                        .directory("artist-avatars")
                        .max_size(2048)
                        .image_editor()
                        .image_editor_aspect_ratios(["1:1"])
                        .openable(),
                    ]
                ),
                Section.make("catalog")
                .heading("Catalog")
                .collapsible()
                .schema(
                    [
                        TagsInput.make("genres")
                        .label("Genres")
                        .suggestions(
                            [
                                "electronic",
                                "folk",
                                "synthwave",
                                "jazz",
                                "indie",
                                "ambient",
                            ]
                        ),
                        CheckboxList.make("platforms")
                        .label("Platforms")
                        .options(_PLATFORMS)
                        .bulk_toggleable()
                        .options_columns(2),
                        Toggle.make("is_active").label("Active").default(True),
                    ]
                ),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.columns(
                [
                    ImageColumn.make("avatar").label("").circular().size(36),
                    TextColumn.make("name").searchable().sortable(),
                    TextColumn.make("country").sortable().toggleable(),
                    TagsColumn.make("genres").separator(",").limit(3).color("primary"),
                    ColorColumn.make("brand_color").label("Color").copyable(),
                    BooleanColumn.make("is_active").label("Active"),
                ]
            )
            .stacked_on_mobile()
        )

    @classmethod
    def infolist(cls, infolist: Infolist) -> Infolist:
        return infolist.columns(2).schema(
            [
                Section.make("basics")
                .heading("Artist")
                .schema(
                    [
                        ImageEntry.make("avatar").label("Avatar").circular().size(56),
                        TextEntry.make("name").label("Name").weight("bold").size("lg"),
                        TextEntry.make("country").label("Country"),
                        TextEntry.make("website")
                        .label("Website")
                        .url(lambda state, **_: str(state) if state else None)
                        .open_url_in_new_tab()
                        .color("primary"),
                        TextEntry.make("bio").label("Bio").prose().column_span(2),
                    ]
                ),
                Section.make("brand")
                .heading("Brand")
                .schema(
                    [
                        ColorEntry.make("brand_color").label("Color").copyable(),
                        TextEntry.make("genres").label("Genres").badge().separator(", "),
                        IconEntry.make("is_active").label("Active").boolean(),
                    ]
                ),
            ]
        )
