"""Relation managers — nested tables on resource view/edit pages."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit.forms.form import Form
from almasix.orbit.tables.table import Table


class RelationManager:
    relationship: ClassVar[str] = ""
    title: ClassVar[str | None] = None
    record_title_attribute: ClassVar[str] = "id"

    @classmethod
    def get_title(cls) -> str:
        return cls.title or cls.relationship.replace("_", " ").title()

    @classmethod
    def form(cls, form: Form) -> Form:
        return form

    @classmethod
    def table(cls, table: Table) -> Table:
        return table

    @classmethod
    def get_form(cls) -> Form:
        return cls.form(Form.make(f"{cls.relationship}_form"))

    @classmethod
    def get_table(cls) -> Table:
        return cls.table(Table.make(f"{cls.relationship}_table"))

    @classmethod
    def can_view_for_record(cls, user: Any, owner: Any) -> bool:
        return user is not None
