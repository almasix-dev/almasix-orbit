"""Table widget wrapping an Orbit Table."""

from __future__ import annotations

from typing import Any, Self

from almasix.orbit.tables.table import Table
from almasix.orbit.widgets.widget import Widget


class TableWidget(Widget):
    """Embed a configured :class:`~almasix.orbit.tables.table.Table` on a dashboard."""

    def __init__(self, name: str | None = "table_widget") -> None:
        super().__init__(name)
        self._table: Table | None = None

    def table(self, table: Table) -> Self:
        self._table = table
        return self

    def get_table(self) -> Table | None:
        return self._table

    def render_body(self, state: Any = None, **ctx: Any) -> str:
        if self._table is None:
            return ""
        return self._table.render(state, **ctx)
