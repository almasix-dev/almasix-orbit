"""Kitchen-sink Forms + Schemas demo for QA of every field family."""

from __future__ import annotations

from almasix.orbit.forms import (
    Block,
    Builder,
    Checkbox,
    CheckboxList,
    ColorPicker,
    DatePicker,
    DateTimePicker,
    FileUpload,
    Form,
    KeyValue,
    MoneyInput,
    MonthPicker,
    MorphToSelect,
    Radio,
    Repeater,
    RichEditor,
    Select,
    TagsInput,
    Textarea,
    TextInput,
    TimePicker,
    Toggle,
    ToggleButtons,
    WeekPicker,
    YearPicker,
)
from almasix.orbit.panels.resource import Resource
from almasix.orbit.schemas import (
    Callout,
    Fieldset,
    Flex,
    Grid,
    Group,
    Section,
    Split,
    Tabs,
    Wizard,
)
from almasix.orbit.tables import TextColumn, Table


class KitchenSinkResource(Resource):
    model = type("KitchenSink", (), {})
    navigation_label = "Kitchen sink"
    navigation_group = "Demos"
    slug = "kitchen-sink"
    records_mutable = True
    records = [
        {
            "id": 1,
            "name": "Ada Lovelace",
            "email": "ada@orbit.test",
            "role": "admin",
            "bio": "First programmer.",
            "plan": "pro",
            "features": ["api"],
            "tags": ["math", "poetry"],
            "amount": 42.5,
            "color": "#3366ff",
            "active": True,
            "joined": "2024-01-15",
            "links": [{"url": "https://orbit.almasix.com"}],
            "meta": {"team": "core"},
            "blocks": [{"type": "hero", "heading": "Welcome"}],
        }
    ]

    @classmethod
    def get_records(cls):
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                Callout.make()
                .info()
                .label("Kitchen sink")
                .description("Filament-parity form + schema layouts in one place."),
                Wizard.make("onboard")
                .skippable()
                .vertical()
                .steps(
                    (
                        "Profile",
                        [
                            Section.make("basics")
                            .heading("Basics")
                            .collapsible()
                            .schema(
                                [
                                    Flex.make()
                                    .from_breakpoint("md")
                                    .schema(
                                        [
                                            TextInput.make("name").required().label("Name"),
                                            TextInput.make("email").email().label("Email"),
                                        ]
                                    ),
                                    Select.make("role")
                                    .options({"admin": "Admin", "editor": "Editor"})
                                    .label("Role"),
                                    Textarea.make("bio").rows(3).label("Bio"),
                                ]
                            ),
                        ],
                    ),
                    (
                        "Preferences",
                        [
                            Tabs.make("prefs")
                            .tabs(
                                (
                                    "Plan",
                                    [
                                        Radio.make("plan")
                                        .options({"free": "Free", "pro": "Pro"})
                                        .descriptions({"pro": "Priority support"})
                                        .options_columns(2)
                                        .label("Plan"),
                                        MoneyInput.make("amount").currency("USD").label("Budget"),
                                        ColorPicker.make("color").label("Accent"),
                                    ],
                                ),
                                {
                                    "label": "Extras",
                                    "icon": "heroicon-o-sparkles",
                                    "badge": 2,
                                    "schema": [
                                        CheckboxList.make("features")
                                        .options({"api": "API", "sso": "SSO"})
                                        .bulk_toggleable()
                                        .label("Features"),
                                        TagsInput.make("tags")
                                        .suggestions(["math", "poetry", "science"])
                                        .label("Tags"),
                                        Toggle.make("active").label("Active"),
                                        ToggleButtons.make("priority")
                                        .options({"low": "Low", "high": "High"})
                                        .label("Priority"),
                                    ],
                                },
                            ),
                        ],
                    ),
                    (
                        "Content",
                        [
                            Group.make()
                            .columns(2)
                            .schema(
                                [
                                    DatePicker.make("joined")
                                    .min_date("2020-01-01")
                                    .label("Joined"),
                                    DateTimePicker.make("reviewed_at")
                                    .label("Reviewed at")
                                    .seconds()
                                    .hours12(),
                                    TimePicker.make("opens_at")
                                    .label("Opens at")
                                    .hours12()
                                    .minute_step(15),
                                    WeekPicker.make("sprint_week").label("Sprint week"),
                                    MonthPicker.make("billing_month").label("Billing month"),
                                    YearPicker.make("vintage").label("Vintage"),
                                    DatePicker.make("native_day")
                                    .label("Native date")
                                    .native(True),
                                    FileUpload.make("avatar")
                                    .avatar()
                                    .disk("public")
                                    .directory("kitchen-avatars")
                                    .image_editor()
                                    .image_editor_aspect_ratios(["1:1"])
                                    .label("Avatar"),
                                    MorphToSelect.make("owner")
                                    .label("Owner")
                                    .searchable()
                                    .types(
                                        [
                                            {
                                                "type": "user",
                                                "label": "User",
                                                "options": {"1": "Ada Lovelace", "2": "Alan Turing"},
                                            },
                                            {
                                                "type": "team",
                                                "label": "Team",
                                                "options": {"10": "Platform"},
                                            },
                                        ]
                                    ),
                                ]
                            ),
                            Split.make()
                            .from_("md")
                            .schema(
                                [
                                    Fieldset.make()
                                    .label("Links")
                                    .schema(
                                        [
                                            Repeater.make("links")
                                            .schema([TextInput.make("url").label("URL")])
                                            .cloneable()
                                            .reorderable()
                                            .label("Links"),
                                        ]
                                    ),
                                    KeyValue.make("meta").label("Meta"),
                                ]
                            ),
                            Builder.make("blocks")
                            .blocks(
                                [
                                    Block.make("hero")
                                    .label("Hero")
                                    .schema([TextInput.make("heading").label("Heading")])
                                ]
                            )
                            .label("Blocks"),
                            RichEditor.make("body").label("Body"),
                            Grid.make()
                            .columns(2)
                            .schema(
                                [
                                    Checkbox.make("terms").label("Accept terms"),
                                ]
                            ),
                        ],
                    ),
                ),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns(
            [
                TextColumn.make("name").searchable().sortable(),
                TextColumn.make("email"),
                TextColumn.make("role").badge(),
            ]
        )
