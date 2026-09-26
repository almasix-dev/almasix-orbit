"""Infolists overview showcase — Filament 5 entry parity on a ViewRecord page."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.actions import EditAction, ViewAction
from almasix.orbit.forms import Form, TextInput, Textarea
from almasix.orbit.infolists import (
    CodeEntry,
    ColorEntry,
    IconEntry,
    ImageEntry,
    Infolist,
    KeyValueEntry,
    RepeatableEntry,
    TextEntry,
    ViewEntry,
)
from almasix.orbit.schemas import Section
from almasix.orbit.tables import Table, TextColumn


class InfolistsOverviewResource(Resource):
    """Focused sample for infolists docs — open a record to see the ViewRecord infolist."""

    model = type("InfolistSample", (), {})
    slug = "infolists-overview"
    navigation_label = "Infolists overview"
    navigation_group = "Infolists"
    navigation_icon = "heroicon-o-queue-list"
    navigation_sort = 0
    record_title_attribute = "title"
    infolist_content_max_width = 'screen-2xl'

    records: ClassVar[list[dict[str, Any]]] = [
        {
            "id": 1,
            "title": "Launch Orbit",
            "slug": "launch-orbit",
            "status": "published",
            "email": "ada@orbit.test",
            "website": "https://orbit.almasix.com",
            "body": "Ship **badges**, copyable slugs, and prose on the show page.",
            "published_at": "2024-06-15T12:30:00",
            "price": 1999,
            "active": True,
            "featured": False,
            "accent": "#f1511b",
            "photo": "https://api.dicebear.com/9.x/shapes/svg?seed=orbit",
            "photos": [
                "https://api.dicebear.com/9.x/shapes/svg?seed=orbit",
                "https://api.dicebear.com/9.x/shapes/svg?seed=ada",
                "https://api.dicebear.com/9.x/shapes/svg?seed=grace",
            ],
            "tags": ["tables", "forms", "infolists"],
            "meta": {"locale": "en", "timezone": "UTC"},
            "payload": {"version": 1, "enabled": True},
            "source": "def greet(name):\n    return f'Hello, {name}!'",
            "items": [
                {"name": "Tables", "status": "ready"},
                {"name": "Forms", "status": "ready"},
                {"name": "Infolists", "status": "shipping"},
            ],
            "author": {"name": "Ada Lovelace"},
        },
        {
            "id": 2,
            "title": "Conduit hosts",
            "slug": "conduit-hosts",
            "status": "draft",
            "email": "grace@orbit.test",
            "website": "https://almasix.com",
            "body": "View pages hydrate the same Conduit shell as edit.",
            "published_at": "2024-08-01T09:00:00",
            "price": 0,
            "active": True,
            "featured": True,
            "accent": "#3b82f6",
            "photo": "https://api.dicebear.com/9.x/shapes/svg?seed=grace",
            "photos": [
                "https://api.dicebear.com/9.x/shapes/svg?seed=grace",
                "https://api.dicebear.com/9.x/shapes/svg?seed=ada",
            ],
            "tags": ["conduit", "hosts"],
            "meta": {"locale": "en", "timezone": "Africa/Nairobi"},
            "payload": {"version": 2},
            "source": "print('hello')",
            "items": [{"name": "Hosts", "status": "ready"}],
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
                TextInput.make("slug").required(),
                TextInput.make("status"),
                Textarea.make("body").rows(4),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.heading("Infolist samples")
            .description("Open a record to view the Filament-parity Infolist.")
            .columns(
                [
                    TextColumn.make("title").searchable(),
                    TextColumn.make("status").badge(),
                    TextColumn.make("author.name").label("Author"),
                ]
            )
            .record_actions([ViewAction.make(), EditAction.make()])
            .record_url(lambda record: InfolistsOverviewResource.page_url("view", record))
        )

    @classmethod
    def infolist(cls, infolist: Infolist) -> Infolist:
        return (infolist.columns(2)
        .schema(
            [
                Section.make("basics")
                .heading("Basics")
                .schema(
                    [
                        TextEntry.make("title").label("Title").weight("bold").size("lg"),
                        TextEntry.make("status").label("Status").badge().color(
                            lambda state, **_: {
                                "published": "success",
                                "draft": "warning",
                            }.get(str(state), "gray")
                        ),
                        TextEntry.make("slug").label("Slug").copyable().font_family("monospace"),
                        TextEntry.make("author.name").label("Author"),
                        TextEntry.make("email")
                        .label("Email")
                        .icon("heroicon-o-envelope")
                        .icon_color("primary")
                        .copyable(),
                        TextEntry.make("website")
                        .label("Website")
                        .url(lambda state, **_: str(state))
                        .open_url_in_new_tab()
                        .color("primary"),
                    ]
                ),
                Section.make("media")
                .heading("Media & flags")
                .schema(
                    [
                        ImageEntry.make("photo").label("Cover").circular().size(56).alt("Cover"),
                        ImageEntry.make("photos")
                        .label("Team")
                        .stacked()
                        .circular()
                        .limit(2)
                        .size(36),
                        IconEntry.make("active").label("Active").boolean(),
                        IconEntry.make("featured").label("Featured").boolean(),
                        ColorEntry.make("accent").label("Accent").copyable(),
                    ]
                ),
                Section.make("formatted")
                .heading("Formatted values")
                .schema(
                    [
                        TextEntry.make("published_at")
                        .label("Published")
                        .date_time("%b %d, %Y %H:%M"),
                        TextEntry.make("price").label("Price").money("USD", divide_by=100),
                        TextEntry.make("tags").label("Tags").separator(", ").badge().color("gray"),
                        TextEntry.make("body").label("Body").prose().markdown(),
                        ViewEntry.make("summary")
                        .label("Summary")
                        .content(
                            lambda record=None, **_: (
                                f'<strong>{len((record or {}).get("items", []))}</strong> modules'
                            )
                        ),
                    ]
                ),
                Section.make("structured")
                .heading("Structured")
                .schema(
                    [
                        KeyValueEntry.make("meta")
                        .label("Meta")
                        .key_label("Property")
                        .value_label("Content"),
                        CodeEntry.make("source").label("Source").grammar("python").copyable(),
                        CodeEntry.make("payload").label("Payload"),
                        RepeatableEntry.make("items")
                        .label("Modules")
                        .columns(2)
                        .schema(
                            [
                                TextEntry.make("name").label("Name"),
                                TextEntry.make("status").label("Status").badge().color("info"),
                            ]
                        ),
                    ]
                ),
            ]
        ))
