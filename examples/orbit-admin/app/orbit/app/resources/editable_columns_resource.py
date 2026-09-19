"""Editable Select / Toggle / TextInput / Checkbox columns — Filament-parity editable APIs."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import (
    CheckboxColumn,
    SelectColumn,
    Table,
    TextColumn,
    TextInputColumn,
    ToggleColumn,
)


def _log_status_change(record: Any = None, state: Any = None, old: Any = None, **_: Any) -> None:
    if isinstance(record, dict):
        record["history"] = f"{old} → {state}"


class EditableColumnsResource(Resource):
    model = type("EditableDemo", (), {})
    slug = "editable-columns"
    navigation_label = "Editable columns"
    navigation_group = "Columns"
    navigation_icon = "heroicon-o-pencil-square"
    navigation_sort = 3
    records_mutable = True

    records: ClassVar[list[dict[str, Any]]] = [
        {
            "id": 1,
            "title": "Filters polish",
            "status": "review",
            "priority": "high",
            "price": "42.00",
            "done": False,
            "featured": True,
            "locked": False,
            "history": "—",
        },
        {
            "id": 2,
            "title": "Summaries",
            "status": "published",
            "priority": "med",
            "price": "19.99",
            "done": True,
            "featured": False,
            "locked": True,
            "history": "—",
        },
    ]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title")])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns(
            [
                TextInputColumn.make("title").label("Title"),
                TextInputColumn.make("price")
                .label("Price")
                .type("number")
                .input_mode("decimal")
                .step("0.01")
                .prefix("$"),
                SelectColumn.make("status")
                .options({"draft": "Draft", "review": "Review", "published": "Published"})
                .selectable_placeholder(False)
                .before_state_updated(_log_status_change),
                SelectColumn.make("priority")
                .options({"low": "Low", "med": "Med", "high": "High"})
                .disable_option_when(
                    lambda value=None, record=None, **_: value == "high"
                    and (record or {}).get("locked")
                ),
                ToggleColumn.make("featured").label("Featured"),
                CheckboxColumn.make("done")
                .label("Done")
                .disabled(lambda record=None, **_: (record or {}).get("locked")),
                TextColumn.make("history").label("History").placeholder("—"),
            ]
        )
