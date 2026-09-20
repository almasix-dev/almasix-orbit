"""Cluster member — Colors (Settings Hub)."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import Table, TextColumn
from app.orbit.app.clusters.settings_hub_cluster import SettingsHubCluster


class NavColorsResource(Resource):
    model = type("NavColor", (), {})
    slug = "colors"
    cluster = SettingsHubCluster
    navigation_label = "Colors"
    navigation_icon = "heroicon-o-swatch"
    navigation_sort = 1
    record_title_attribute = "name"

    records: ClassVar[list[dict[str, Any]]] = [
        {"id": 1, "name": "Primary", "hex": "#f1511b"},
        {"id": 2, "name": "Success", "hex": "#22c55e"},
    ]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("name").required(),
                TextInput.make("hex").label("Hex").required(),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.heading("Colors")
            .description("Cluster member under Settings Hub.")
            .columns([TextColumn.make("name"), TextColumn.make("hex").label("Hex")])
            .records(cls.get_records())
            .paginated(False)
        )
