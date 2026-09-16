"""Resource — CRUD configuration (Filament Resource analogue)."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit.actions.action import (
    CreateAction,
    DeleteAction,
    DeleteBulkAction,
    EditAction,
    ViewAction,
)
from almasix.orbit.forms.form import Form
from almasix.orbit.infolists.infolist import Infolist
from almasix.orbit.tables.table import Table


class Resource:
    """Declarative CRUD resource. Subclass and set ``model`` + configure form/table."""

    model: ClassVar[type[Any] | None] = None
    slug: ClassVar[str | None] = None
    navigation_icon: ClassVar[str] = "heroicon-o-users"
    navigation_label: ClassVar[str | None] = None
    navigation_group: ClassVar[str | None] = None
    navigation_sort: ClassVar[int] = 0
    record_title_attribute: ClassVar[str] = "id"
    permission_prefix: ClassVar[str | None] = None

    @classmethod
    def get_slug(cls) -> str:
        if cls.slug:
            return cls.slug
        name = cls.__name__
        if name.endswith("Resource"):
            name = name[: -len("Resource")]
        return _snake(name)

    @classmethod
    def get_navigation_label(cls) -> str:
        return cls.navigation_label or cls.get_slug().replace("_", " ").title()

    @classmethod
    def get_model(cls) -> type[Any]:
        if cls.model is None:
            raise RuntimeError(f"{cls.__name__}.model is not set")
        return cls.model

    @classmethod
    def get_permission_prefix(cls) -> str:
        return cls.permission_prefix or cls.get_slug()

    @classmethod
    def can_view_any(cls, user: Any) -> bool:
        return _can(user, f"{cls.get_permission_prefix()}.view_any")

    @classmethod
    def can_view(cls, user: Any, record: Any = None) -> bool:
        return _can(user, f"{cls.get_permission_prefix()}.view", record)

    @classmethod
    def can_create(cls, user: Any) -> bool:
        return _can(user, f"{cls.get_permission_prefix()}.create")

    @classmethod
    def can_update(cls, user: Any, record: Any = None) -> bool:
        return _can(user, f"{cls.get_permission_prefix()}.update", record)

    @classmethod
    def can_delete(cls, user: Any, record: Any = None) -> bool:
        return _can(user, f"{cls.get_permission_prefix()}.delete", record)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form

    @classmethod
    def table(cls, table: Table) -> Table:
        return table

    @classmethod
    def infolist(cls, infolist: Infolist) -> Infolist:
        return infolist

    @classmethod
    def get_form(cls) -> Form:
        return cls.form(Form.make("form"))

    @classmethod
    def get_table(cls) -> Table:
        table = cls.table(Table.make("table"))
        if not table._actions:
            table.actions([ViewAction.make(), EditAction.make(), DeleteAction.make()])
        if not table._bulk_actions:
            table.bulk_actions([DeleteBulkAction.make()])
        if not table._header_actions:
            table.header_actions([CreateAction.make()])
        return table

    @classmethod
    def get_infolist(cls) -> Infolist:
        return cls.infolist(Infolist.make("infolist"))

    @classmethod
    def get_pages(cls) -> dict[str, str]:
        slug = cls.get_slug()
        return {
            "index": f"/{slug}",
            "create": f"/{slug}/create",
            "edit": f"/{slug}/{{id}}/edit",
            "view": f"/{slug}/{{id}}",
        }

    @classmethod
    def get_relations(cls) -> list[type[Any]]:
        return []


def _snake(name: str) -> str:
    out: list[str] = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0:
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


def _can(user: Any, ability: str, record: Any = None) -> bool:
    if user is None:
        return False
    for attr in ("can", "has_permission", "hasPermissionTo"):
        fn = getattr(user, attr, None)
        if callable(fn):
            try:
                if record is not None:
                    return bool(fn(ability, record))
                return bool(fn(ability))
            except TypeError:
                return bool(fn(ability))
    if getattr(user, "is_super_admin", False) or getattr(user, "is_admin", False):
        return True
    perms = getattr(user, "permissions", None)
    if isinstance(perms, (set, list, tuple)):
        return ability in perms or "*" in perms
    return False
