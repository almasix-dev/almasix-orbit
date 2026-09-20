"""Actions overview showcase — Filament 5 trigger / modal / preset parity."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.actions import (
    Action,
    ActionGroup,
    CreateAction,
    DeleteAction,
    EditAction,
    ViewAction,
)
from almasix.orbit.forms import Form, Select, TextInput, Textarea
from almasix.orbit.tables import Table, TextColumn


_NOTE_FORM = [
    TextInput.make("title").label("Title").required(),
    Select.make("status")
    .label("Status")
    .options({"draft": "Draft", "published": "Published", "archived": "Archived"})
    .required(),
    Textarea.make("body").label("Body").rows(3),
]


class ActionsOverviewResource(Resource):
    """Focused sample for actions docs — header triggers, modals, groups, presets."""

    model = type("ActionSample", (), {})
    slug = "actions-overview"
    navigation_label = "Actions overview"
    navigation_group = "Actions"
    navigation_icon = "heroicon-o-check"
    navigation_sort = 0
    record_title_attribute = "title"

    records: ClassVar[list[dict[str, Any]]] = [
        {
            "id": 1,
            "title": "Wire confirm dialog",
            "status": "published",
            "body": "Danger actions confirm by default.",
        },
        {
            "id": 2,
            "title": "Ship modal create",
            "status": "draft",
            "body": "CreateAction with create_another.",
        },
        {
            "id": 3,
            "title": "Group row actions",
            "status": "archived",
            "body": "ActionGroup dropdown on the row.",
        },
    ]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(list(_NOTE_FORM))

    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.heading("Action samples")
            .description(
                "Header triggers, confirmation + form modals, ActionGroup, and CRUD presets."
            )
            .columns(
                [
                    TextColumn.make("title").searchable(),
                    TextColumn.make("status").badge(),
                ]
            )
            .header_actions(
                [
                    CreateAction.make()
                    .modal()
                    .modal_heading("New sample")
                    .modal_description("Create a row with the shared form schema.")
                    .form(list(_NOTE_FORM))
                    .create_another()
                    .success_notification("Created"),
                    Action.make("docs")
                    .label("Docs")
                    .link()
                    .icon("heroicon-o-document-text")
                    .url("https://orbit.almasix.com/actions/overview/")
                    .open_url_in_new_tab(),
                    Action.make("inbox")
                    .label("Inbox")
                    .icon("heroicon-o-bell")
                    .badge(2)
                    .badge_color("danger")
                    .color("gray")
                    .outlined()
                    .tooltip("2 pending reviews")
                    .action(lambda **_: None),
                    ActionGroup.make(
                        [
                            Action.make("export_csv")
                            .label("Export CSV")
                            .icon("heroicon-o-arrow-down-tray")
                            .color("gray")
                            .action(lambda **_: None),
                            Action.make("import_csv")
                            .label("Import CSV")
                            .icon("heroicon-o-arrow-up-tray")
                            .color("gray")
                            .modal()
                            .modal_heading("Import CSV")
                            .form([TextInput.make("path").label("File path")])
                            .action(lambda **_: None),
                        ]
                    )
                    .label("More")
                    .icon("heroicon-o-ellipsis-vertical")
                    .color("gray"),
                ]
            )
            .actions(
                [
                    ViewAction.make()
                    .modal()
                    .modal_heading("View sample")
                    .form(list(_NOTE_FORM)),
                    EditAction.make()
                    .modal()
                    .modal_heading("Edit sample")
                    .form(list(_NOTE_FORM))
                    .success_notification("Saved"),
                    ActionGroup.make(
                        [
                            Action.make("archive")
                            .label("Archive")
                            .icon("heroicon-o-funnel")
                            .color("warning")
                            .requires_confirmation()
                            .modal_heading("Archive?")
                            .modal_description("Hide this sample from the default list.")
                            .action(lambda **_: None),
                            DeleteAction.make(),
                        ]
                    )
                    .label("More")
                    .icon("heroicon-o-ellipsis-vertical")
                    .icon_button()
                    .color("gray"),
                ]
            )
            .actions_as_dropdown(False)
            .bulk_actions([])
            .record_url(lambda record=None, **_: "")
        )
