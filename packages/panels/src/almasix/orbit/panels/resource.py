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
from almasix.orbit.forms.components import Field
from almasix.orbit.forms.form import Form
from almasix.orbit.infolists.components import TextEntry
from almasix.orbit.infolists.infolist import Infolist
from almasix.orbit.support.component import Component
from almasix.orbit.tables.table import Table


class Resource:
    """Declarative CRUD resource. Subclass and set ``model`` + configure form/table."""

    model: ClassVar[type[Any] | None] = None
    slug: ClassVar[str | None] = None
    navigation_icon: ClassVar[str] = "heroicon-o-users"
    navigation_label: ClassVar[str | None] = None
    navigation_group: ClassVar[str | None] = None
    navigation_subgroup: ClassVar[str | None] = None
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
    def get_pages(cls) -> dict[str, str]:
        slug = cls.get_slug()
        return {
            "index": f"/{slug}",
            "create": f"/{slug}/create",
            "edit": f"/{slug}/{{id}}/edit",
            "view": f"/{slug}/{{id}}",
        }

    @classmethod
    def page_url(cls, page: str, record: Any = None) -> str:
        template = cls.get_pages().get(page, "")
        record_id = ""
        if record is not None:
            if isinstance(record, dict):
                record_id = str(record.get("id", ""))
            else:
                record_id = str(getattr(record, "id", ""))
        return template.replace("{id}", record_id)

    @classmethod
    def get_table(cls) -> Table:
        table = cls.table(Table.make("table"))
        if not table._actions:
            table.actions(
                [
                    ViewAction.make().url(
                        lambda record=None, **_: cls.page_url("view", record)
                    ),
                    EditAction.make().url(
                        lambda record=None, **_: cls.page_url("edit", record)
                    ),
                    DeleteAction.make(),
                ]
            )
        if not table._bulk_actions:
            table.bulk_actions([DeleteBulkAction.make()])
        if not table._header_actions:
            table.header_actions(
                [CreateAction.make().url(lambda **_: cls.page_url("create"))]
            )
        return table

    @classmethod
    def get_infolist(cls) -> Infolist:
        infolist = cls.infolist(Infolist.make("infolist"))
        if infolist.get_components():
            return infolist
        # Fallback: readonly projection of the form schema
        form = cls.get_form().readonly()
        entries: list[Component] = []
        for field in _iter_fields(form.get_components()):
            name = field.get_name()
            if not name:
                continue
            entry = TextEntry.make(name).label(field.get_label())
            entries.append(entry)
        return Infolist.make("infolist").schema(entries)

    @classmethod
    def get_relations(cls) -> list[type[Any]]:
        return []


def _iter_fields(components: list[Component]) -> list[Field]:
    fields: list[Field] = []
    for component in components:
        if isinstance(component, Field):
            fields.append(component)
            continue
        tabs = getattr(component, "_tabs", None)
        if isinstance(tabs, list) and tabs:
            for _label, comps in tabs:
                fields.extend(_iter_fields(list(comps)))
            continue
        steps = getattr(component, "_steps", None)
        if isinstance(steps, list) and steps:
            for _label, comps in steps:
                fields.extend(_iter_fields(list(comps)))
            continue
        children = getattr(component, "get_components", None)
        if callable(children):
            fields.extend(_iter_fields(children()))
            continue
        child_components = getattr(component, "get_child_components", None)
        if callable(child_components):
            fields.extend(_iter_fields(child_components()))
            continue
        schema = getattr(component, "get_schema", None)
        if callable(schema):
            fields.extend(_iter_fields(schema()))
            continue
        nested = getattr(component, "_schema", None)
        if isinstance(nested, list) and nested:
            fields.extend(_iter_fields(nested))
    return fields


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
