"""Modal tasks — Create/Edit open as dialog forms (not full pages)."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.actions import CreateAction, DeleteAction, EditAction
from almasix.orbit.forms import Form, Select, TextInput
from almasix.orbit.tables import Table, TextColumn


_TASK_FORM = [
    TextInput.make("title").label("Title").required(),
    Select.make("status")
    .label("Status")
    .options({"todo": "To do", "doing": "Doing", "done": "Done"})
    .required(),
]


class ModalTasksResource(Resource):
    model = type("ModalTask", (), {})
    slug = "modal-tasks"
    navigation_label = "Modal forms"
    navigation_group = "Columns"
    navigation_icon = "heroicon-o-window"
    navigation_sort = 21

    records: ClassVar[list[dict[str, Any]]] = [
        {"id": 1, "title": "Wire confirm dialog", "status": "done"},
        {"id": 2, "title": "Ship modal create", "status": "doing"},
        {"id": 3, "title": "Polish edit form", "status": "todo"},
    ]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(list(_TASK_FORM))

    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.columns(
                [
                    TextColumn.make("title").searchable(),
                    TextColumn.make("status").badge(),
                ]
            )
            .header_actions(
                [
                    CreateAction.make()
                    .modal()
                    .modal_heading("New task")
                    .form(list(_TASK_FORM))
                ]
            )
            .actions(
                [
                    EditAction.make()
                    .modal()
                    .modal_heading("Edit task")
                    .form(list(_TASK_FORM)),
                    DeleteAction.make(),
                ]
            )
            .actions_as_dropdown(False)
            .bulk_actions([])
            .record_url(lambda record=None, **_: "")
        )
