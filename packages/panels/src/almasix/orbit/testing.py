"""Testing helpers for Orbit resources and actions."""

from __future__ import annotations

from typing import Any

from almasix.orbit.forms.form import Form
from almasix.orbit.panels.resource import Resource
from almasix.orbit.tables.table import Table


class LiveResource:
    """Lightweight test double for asserting form/table configuration."""

    def __init__(self, resource: type[Resource]) -> None:
        self.resource = resource

    def form(self) -> Form:
        return self.resource.get_form()

    def table(self) -> Table:
        return self.resource.get_table()

    def assert_form_has_field(self, name: str) -> None:
        fields = [c.get_name() for c in self.form().get_components()]
        assert name in fields, f"Expected form field {name!r}, got {fields}"

    def assert_table_has_column(self, name: str) -> None:
        cols = [c.get_name() for c in self.table()._columns]
        assert name in cols, f"Expected column {name!r}, got {cols}"

    def fill_form(self, data: dict[str, Any]) -> dict[str, list[str]]:
        form = self.form().fill(data)
        return form.validate(data)
