"""Navigation showcase — badges, subgroups, and focused sample table."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import Table, TextColumn


class NavigationOverviewResource(Resource):
    """Focused sample for navigation docs — badge + subgroup under Navigation."""

    model = type("NavSample", (), {})
    slug = "navigation-overview"
    navigation_label = "Nav showcase"
    navigation_group = "Navigation"
    navigation_subgroup = "Samples"
    navigation_icon = "heroicon-o-bars-3"
    active_navigation_icon = "heroicon-s-bars-3"
    navigation_sort = 0
    navigation_badge = "New"
    navigation_badge_color = "success"
    navigation_badge_tooltip = "Navigation polish sample"
    record_title_attribute = "title"

    records: ClassVar[list[dict[str, Any]]] = [
        {
            "id": 1,
            "title": "Apps layout",
            "note": "Sidebar roots + topbar secondary links.",
        },
        {
            "id": 2,
            "title": "Badges",
            "note": "navigation_badge on resources and pages.",
        },
        {
            "id": 3,
            "title": "Parent items",
            "note": "Preferences nests under Account in this panel.",
        },
    ]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("title").label("Title").required(),
                TextInput.make("note").label("Note"),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.heading("Navigation samples")
            .description(
                "Badges, subgroups, custom items, user menu, and a small Settings Hub cluster."
            )
            .columns(
                [
                    TextColumn.make("title").searchable(),
                    TextColumn.make("note").label("Note"),
                ]
            )
            .records(cls.get_records())
            .paginated(False)
        )
