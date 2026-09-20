"""Cluster member — Fonts (Settings Hub)."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import Table, TextColumn
from app.orbit.app.clusters.settings_hub_cluster import SettingsHubCluster


class NavFontsResource(Resource):
    model = type("NavFont", (), {})
    slug = "fonts"
    cluster = SettingsHubCluster
    navigation_label = "Fonts"
    navigation_icon = "heroicon-o-language"
    navigation_sort = 2
    record_title_attribute = "name"

    records: ClassVar[list[dict[str, Any]]] = [
        {"id": 1, "name": "Outfit", "role": "UI"},
        {"id": 2, "name": "JetBrains Mono", "role": "Code"},
    ]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("name").required(),
                TextInput.make("role").label("Role"),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.heading("Fonts")
            .description("Second cluster member under Settings Hub.")
            .columns([TextColumn.make("name"), TextColumn.make("role").label("Role")])
            .records(cls.get_records())
            .paginated(False)
        )
