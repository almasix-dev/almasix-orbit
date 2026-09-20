"""Relation managers — nested tables of related records on resource pages."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit.actions.action import CreateAction, DeleteAction
from almasix.orbit.forms.form import Form
from almasix.orbit.support.html import e
from almasix.orbit.tables.table import Table


class RelationManager:
    """A table of records that belong to the record on the page.

    Set :attr:`relationship` to the attribute (or dict key) that holds the related
    records on the owner. Point :attr:`related_model` at an ORM model to load them
    from the database instead, matched on :attr:`foreign_key`.
    """

    relationship: ClassVar[str] = ""
    title: ClassVar[str | None] = None
    description: ClassVar[str | None] = None
    record_title_attribute: ClassVar[str] = "id"
    #: ORM model holding the related rows (optional — seed lists work too).
    related_model: ClassVar[type[Any] | None] = None
    #: Column on the related model pointing back at the owner.
    foreign_key: ClassVar[str | None] = None
    #: Where the manager renders: ``view``, ``edit``, or ``both``.
    render_on: ClassVar[str] = "both"
    #: When True the table gains create / delete chrome (owner must be mutable).
    is_mutable: ClassVar[bool] = True

    @classmethod
    def get_title(cls) -> str:
        return cls.title or cls.relationship.replace("_", " ").title()

    @classmethod
    def get_description(cls) -> str | None:
        return cls.description

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
        table = cls.table(Table.make(f"{cls.relationship}_table"))
        if cls.is_mutable:
            if not table._actions:
                table.actions([DeleteAction.make(cls.action_name("delete"))])
            if not table._header_actions:
                table.header_actions(
                    [
                        CreateAction.make(cls.action_name("create")).label(
                            f"New {cls.get_record_label()}"
                        )
                    ]
                )
        return table

    @classmethod
    def get_record_label(cls) -> str:
        singular = cls.get_title().rstrip("s").lower() or "record"
        return singular

    @classmethod
    def get_foreign_key(cls, owner_resource: type[Any] | None = None) -> str:
        """Column on the related record pointing back at the owner."""
        if cls.foreign_key:
            return cls.foreign_key
        if owner_resource is not None:
            slug = str(owner_resource.get_slug())
            return f"{_singular(slug)}_id"
        return "owner_id"

    @classmethod
    def action_name(cls, action: str) -> str:
        """Namespaced action name so the page host can route it back here."""
        return f"relation.{cls.relationship}.{action}"

    @classmethod
    def get_records(cls, owner: Any) -> list[Any]:
        """Related records held on the owner (attribute or dict key)."""
        if owner is None:
            return []
        value = owner.get(cls.relationship) if isinstance(owner, dict) else getattr(
            owner, cls.relationship, None
        )
        if value is None:
            return []
        if isinstance(value, (list, tuple)):
            return list(value)
        return [value]

    @classmethod
    def can_view_for_record(cls, user: Any, owner: Any) -> bool:
        return user is not None

    @classmethod
    def render(cls, owner: Any, *, records: list[Any] | None = None, **ctx: Any) -> str:
        """Titled section wrapping the relation table."""
        rows = cls.get_records(owner) if records is None else list(records)
        table = cls.get_table()
        table.records(rows)
        description = cls.get_description()
        description_html = (
            f'<p class="or-relation-description">{e(description)}</p>' if description else ""
        )
        header_actions = "".join(a.render(**ctx) for a in table._header_actions)
        return (
            f'<section class="or-relation-manager" data-relation="{e(cls.relationship)}">'
            f'<header class="or-relation-header">'
            f'<div><h2 class="or-relation-title">{e(cls.get_title())}</h2>{description_html}</div>'
            f'<div class="or-page-actions">{header_actions}</div>'
            f"</header>"
            f"{table.render(skip_header_actions=True, **ctx)}"
            f"</section>"
        )


def _singular(value: str) -> str:
    from almasix.orbit.panels.resource import _singularize

    return _singularize(value)
