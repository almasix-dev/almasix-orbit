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
    Tab,
    Tabs,
    Wizard,
    WizardStep,
)
from almasix.orbit.tables import TextColumn, Table

from app.models.kitchen_sink import KitchenSink
from app.models.team import Team
from app.models.user import User


def _owner_options(type: str = "", search: str = "") -> dict[str, str]:
    """Record options for MorphToSelect — live rows from users or teams."""
    from almasix.orbit.forms.select_relationship import load_relationship_options

    model = {"user": User, "team": Team}.get(str(type or ""))
    if model is None:
        return {}
    return load_relationship_options(
        model=model,
        title_attribute="name",
        search=search or None,
        search_columns=["name"],
        limit=50,
    )


class KitchenSinkResource(Resource):
    model = KitchenSink
    navigation_label = "Kitchen sink"
    navigation_group = "Demos"
    slug = "kitchen-sink"
    record_title_attribute = "name"
    table_content_max_width = "screen-2xl"
    form_content_max_width = "screen-lg"
    infolist_content_max_width = "screen-lg"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                Callout.make()
                .success()
                .label("Kitchen sink")
                .description(
                    "Every field family on one form, saved to the kitchen_sinks table. "
                    "Manager and Owner load from users and teams."
                ),
                Wizard.make("onboard")
                .skippable(False)
                .vertical(False)
                .steps(
                    WizardStep.make("profile")
                    .label("Profile")
                    .description("Name, email, and role.")
                    .icon("heroicon-o-user-group")
                    .schema(
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
                        ]
                    ),
                    WizardStep.make("preferences")
                    .label("Preferences")
                    .icon("heroicon-o-cog-6-tooth")
                    .schema(
                        [
                            Tabs.make("prefs")
                            .tabs(
                                Tab.make("plan")
                                .label("Plan")
                                .schema(
                                    [
                                        Radio.make("plan")
                                        .options({"free": "Free", "pro": "Pro"})
                                        .descriptions({"pro": "Priority support"})
                                        .options_columns(2)
                                        .label("Plan"),
                                        MoneyInput.make("amount").currency("USD").label("Budget"),
                                        ColorPicker.make("color").label("Accent"),
                                    ]
                                ),
                                Tab.make("extras")
                                .label("Extras")
                                .icon("heroicon-o-rectangle-stack")
                                .badge(2)
                                .schema(
                                    [
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
                                    ]
                                ),
                            ),
                        ]
                    ),
                    WizardStep.make("content")
                    .label("Content")
                    .icon("heroicon-o-document-text")
                    .completed_icon("heroicon-o-check")
                    .schema(
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
                                    .hours24(),
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
                                    .image()
                                    .disk("public")
                                    .directory("kitchen-avatars")
                                    .image_editor()
                                    .image_editor_aspect_ratios(["1:1"])
                                    .label("Avatar"),
                                    MorphToSelect.make("owner")
                                    .label("Owner (MorphTo)")
                                    .searchable()
                                    .title_attribute("name")
                                    .types(
                                        [
                                            {
                                                "type": "user",
                                                "label": "User",
                                                "model": User,
                                                "title_attribute": "name",
                                            },
                                            {
                                                "type": "team",
                                                "label": "Team",
                                                "model": Team,
                                                "title_attribute": "name",
                                            },
                                        ]
                                    )
                                    .options_using(_owner_options),
                                    Select.make("manager_id")
                                    .label("Manager (Many2One)")
                                    .searchable()
                                    .preload()
                                    .placeholder("Select manager…")
                                    .relationship(
                                        "manager",
                                        "name",
                                        model=User,
                                        search_columns=["name", "email"],
                                    ),
                                ]
                            ),
                            Split.make()
                            .from_("md")
                            .schema(
                                [
                                    Fieldset.make()
                                    .label("Online presence")
                                    .schema(
                                        [
                                            Repeater.make("links")
                                            .schema(
                                                [TextInput.make("url").label("URL").url()]
                                            )
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
