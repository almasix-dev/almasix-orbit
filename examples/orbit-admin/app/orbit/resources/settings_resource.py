"""Settings resource (System group)."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.forms import Form, TextInput, Toggle
from almasix.orbit.tables import Table, TextColumn


class SettingsResource(Resource):
    model = type("Setting", (), {})
    navigation_label = "Settings"
    navigation_group = "System"
    navigation_icon = "heroicon-o-cog-6-tooth"
    navigation_sort = 1

    records: ClassVar[list[dict[str, Any]]] = [
        {"id": 1, "key": "brand", "value": "Orbit"},
        {"id": 2, "key": "theme", "value": "system"},
    ]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("key").required(),
                TextInput.make("value").required(),
                Toggle.make("public"),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns(
            [
                TextColumn.make("key"),
                TextColumn.make("value"),
            ]
        )
