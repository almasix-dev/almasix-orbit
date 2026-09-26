"""Resource — CRUD configuration (Filament Resource analogue)."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any, ClassVar

from almasix.orbit.actions.action import (
    CreateAction,
    DeleteAction,
    DeleteBulkAction,
    EditAction,
    ViewAction,
)
from almasix.orbit.actions.presets import (
    BulkActionGroup,
    ForceDeleteAction,
    RestoreAction,
)
from almasix.orbit.forms.form import Form
from almasix.orbit.forms.walk import iter_fields
from almasix.orbit.infolists.infolist import Infolist
from almasix.orbit.tables.filters import TrashedFilter, is_trashed
from almasix.orbit.tables.table import Table

# Back-compat for tests/importers that used the private helper name.
_iter_fields = iter_fields


class Resource:
    """Declarative CRUD resource. Subclass and set ``model`` + configure form/table."""

    model: ClassVar[type[Any] | None] = None
    slug: ClassVar[str | None] = None
    navigation_icon: ClassVar[str] = "heroicon-o-users"
    active_navigation_icon: ClassVar[str | None] = None
    navigation_label: ClassVar[str | None] = None
    navigation_group: ClassVar[str | None] = None
    navigation_subgroup: ClassVar[str | None] = None
    #: Alias for :attr:`navigation_subgroup` (second-level nav category).
    navigation_sub_category: ClassVar[str | None] = None
    navigation_sort: ClassVar[int] = 0
    navigation_badge: ClassVar[Any] = None
    navigation_badge_color: ClassVar[Any] = None
    navigation_badge_tooltip: ClassVar[Any] = None
    navigation_parent_item: ClassVar[str | None] = None
    should_register_navigation: ClassVar[bool] = True
    cluster: ClassVar[type[Any] | str | None] = None
    record_title_attribute: ClassVar[str] = "id"
    #: Human labels for a single record / a collection (defaults derive from the slug).
    model_label: ClassVar[str | None] = None
    plural_model_label: ClassVar[str | None] = None
    #: Record attributes matched by the panel's global search box.
    global_search_attributes: ClassVar[Sequence[str]] = ()
    #: Attributes shown underneath a global search result.
    global_search_result_details: ClassVar[Sequence[str]] = ()
    #: Most results this resource may contribute to one search.
    global_search_result_limit: ClassVar[int] = 5
    #: When True, the default table gains a trashed filter plus restore /
    #: force-delete actions, and hosts honour ``restore``.
    soft_deletes: ClassVar[bool] = False
    permission_prefix: ClassVar[str | None] = None
    content_max_width: ClassVar[str | None] = None
    #: List page. Falls back to ``content_max_width``, then the panel width.
    table_content_max_width: ClassVar[str | None] = None
    #: Create and edit pages. Falls back to ``content_max_width``, then ``screen-lg``.
    form_content_max_width: ClassVar[str | None] = None
    #: View page. Falls back to ``content_max_width``, then ``screen-lg``.
    infolist_content_max_width: ClassVar[str | None] = None
    #: ``True`` → CRUD mutates records. ``False`` → seed/demo list is read-only.
    #: ``None`` (default) → mutable when ``model`` is an Almasix ORM ``Model``.
    records_mutable: ClassVar[bool | None] = None
    #: When True (default), list/query helpers apply panel tenancy scoping.
    is_scoped_to_tenant: ClassVar[bool] = True

    @classmethod
    def scope_to_tenant(cls, condition: bool = True) -> type[Resource]:
        """Toggle whether this resource participates in tenant query scoping."""
        cls.is_scoped_to_tenant = bool(condition)
        return cls

    @classmethod
    def is_tenant_scoped(cls) -> bool:
        return bool(getattr(cls, "is_scoped_to_tenant", True))

    @classmethod
    def records_are_mutable(cls) -> bool:
        """Whether create/edit/delete should persist for this resource."""
        flag = getattr(cls, "records_mutable", None)
        if flag is True:
            return True
        if flag is False:
            return False
        return cls._uses_orm_model()

    @classmethod
    def _uses_orm_model(cls) -> bool:
        model = getattr(cls, "model", None)
        if model is None or not isinstance(model, type):
            return False
        if model.__module__ == "builtins" or model.__name__ in {"type", "object"}:
            return False
        try:
            from almasix.orm import Model

            return issubclass(model, Model) and model is not Model
        except Exception:
            return False

    @classmethod
    def get_slug(cls) -> str:
        if cls.slug:
            return cls.slug
        name = cls.__name__
        if name.endswith("Resource"):
            name = name[: -len("Resource")]
        return _pluralize(_snake(name))

    @classmethod
    def get_navigation_label(cls) -> str:
        if cls.navigation_label:
            return cls.navigation_label
        return cls.get_slug().replace("_", " ").replace("-", " ").title()

    @classmethod
    def get_model_label(cls) -> str:
        """Singular human label for one record — ``Blog post``."""
        if cls.model_label:
            return cls.model_label
        slug = cls.get_slug().replace("_", " ").replace("-", " ")
        return _singularize(slug).capitalize()

    @classmethod
    def get_plural_model_label(cls) -> str:
        """Plural human label — ``Blog posts``."""
        if cls.plural_model_label:
            return cls.plural_model_label
        return cls.get_navigation_label()

    @classmethod
    def get_record_title_attribute(cls) -> str:
        return cls.record_title_attribute or "id"

    @classmethod
    def get_record_title(cls, record: Any) -> str:
        """Title for one record — used in page headings and breadcrumbs.

        Reads :attr:`record_title_attribute`; falls back to ``Label #id`` when the
        attribute is missing or empty.
        """
        if record is None:
            return cls.get_model_label()
        value = _record_value(record, cls.get_record_title_attribute())
        if value not in (None, ""):
            return str(value)
        record_id = _record_value(record, "id")
        if record_id not in (None, ""):
            return f"{cls.get_model_label()} #{record_id}"
        return cls.get_model_label()

    @classmethod
    def get_globally_searchable_attributes(cls) -> list[str]:
        """Attributes the panel's global search matches on."""
        attributes = [str(attr) for attr in cls.global_search_attributes if str(attr)]
        return attributes

    @classmethod
    def is_globally_searchable(cls) -> bool:
        """True once at least one searchable attribute is declared."""
        return bool(cls.get_globally_searchable_attributes())

    @classmethod
    def get_global_search_result_title(cls, record: Any) -> str:
        return cls.get_record_title(record)

    @classmethod
    def get_global_search_result_details(cls, record: Any) -> dict[str, Any]:
        details: dict[str, Any] = {}
        for attr in cls.global_search_result_details:
            value = _record_value(record, str(attr))
            if value in (None, ""):
                continue
            details[str(attr).replace("_", " ").title()] = value
        return details

    @classmethod
    def get_global_search_result_url(cls, record: Any) -> str:
        return cls.page_url("view", record)

    @classmethod
    def get_global_search_results(
        cls,
        term: str,
        records: Sequence[Any],
        *,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Match ``records`` against ``term`` and build result rows."""
        from almasix.orbit.panels.global_search import build_result, search_records

        attributes = cls.get_globally_searchable_attributes()
        if not attributes or not str(term).strip():
            return []
        matches = search_records(records, term, attributes=attributes)
        cap = cls.global_search_result_limit if limit is None else limit
        rows: list[dict[str, Any]] = []
        for record in matches[: max(0, cap)]:
            rows.append(
                build_result(
                    title=cls.get_global_search_result_title(record),
                    url=cls.get_global_search_result_url(record),
                    details=cls.get_global_search_result_details(record),
                )
            )
        return rows

    @classmethod
    def get_should_register_navigation(cls, **ctx: Any) -> bool:
        """Whether this resource appears in panel navigation."""
        return _resolve_nav_flag(cls, "should_register_navigation", default=True, **ctx)

    @classmethod
    def get_navigation_badge(cls, **ctx: Any) -> str | None:
        return _resolve_nav_str(cls, "navigation_badge", **ctx)

    @classmethod
    def get_navigation_badge_color(cls, **ctx: Any) -> str | None:
        return _resolve_nav_str(cls, "navigation_badge_color", **ctx)

    @classmethod
    def get_navigation_badge_tooltip(cls, **ctx: Any) -> str | None:
        return _resolve_nav_str(cls, "navigation_badge_tooltip", **ctx)

    @classmethod
    def get_navigation_parent_item(cls) -> str | None:
        return cls.navigation_parent_item

    @classmethod
    def get_cluster(cls) -> type[Any] | str | None:
        return cls.cluster

    @classmethod
    def get_url_path_prefix(cls) -> str:
        """Panel path + optional tenant + cluster slug prefix (no trailing slash)."""
        panel_path = str(getattr(cls, "_panel_path", "") or "").rstrip("/")
        tenant_path = str(getattr(cls, "_tenant_path", "") or "").strip("/")
        cluster = cls.get_cluster()
        cluster_prefix = ""
        if cluster is not None:
            if isinstance(cluster, str):
                slug = cluster.strip().strip("/")
                cluster_prefix = f"/{slug}" if slug else ""
            else:
                path_fn = getattr(cluster, "path_prefix", None)
                if callable(path_fn):
                    cluster_prefix = str(path_fn()).rstrip("/") or ""
                    if cluster_prefix and not cluster_prefix.startswith("/"):
                        cluster_prefix = f"/{cluster_prefix}"
                else:
                    slug_fn = getattr(cluster, "get_slug", None)
                    slug = slug_fn() if callable(slug_fn) else ""
                    cluster_prefix = f"/{slug}" if slug else ""
        parts: list[str] = []
        if panel_path and panel_path != "/":
            parts.append(panel_path.lstrip("/"))
        if tenant_path:
            parts.append(tenant_path)
        if cluster_prefix:
            parts.append(cluster_prefix.strip("/"))
        if not parts:
            return panel_path if panel_path == "/" else ""
        return "/" + "/".join(parts)

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
        prefix = cls.get_url_path_prefix()
        root = f"{prefix}/{slug}" if prefix else f"/{slug}"
        return {
            "index": root,
            "create": f"{root}/create",
            "edit": f"{root}/{{id}}/edit",
            "view": f"{root}/{{id}}",
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
        mutable = cls.records_are_mutable()
        if not table._actions:
            actions = [
                ViewAction.make().url(
                    lambda record=None, **_: cls.page_url("view", record)
                ),
            ]
            if mutable:
                actions.append(
                    EditAction.make().url(
                        lambda record=None, **_: cls.page_url("edit", record)
                    )
                )
                actions.append(DeleteAction.make())
                if cls.soft_deletes:
                    actions.append(
                        RestoreAction.make().visible(
                            lambda record=None, **_: is_trashed(record)
                        )
                    )
                    actions.append(
                        ForceDeleteAction.make().visible(
                            lambda record=None, **_: is_trashed(record)
                        )
                    )
            table.actions(actions)
        if cls.soft_deletes and not table._filters:
            table.filters([TrashedFilter()])
        if not table._bulk_actions and mutable:
            table.bulk_actions(
                [
                    BulkActionGroup.make(
                        [DeleteBulkAction.make().icon("heroicon-o-trash")]
                    )
                ]
            )
        if not table._header_actions and mutable:
            table.header_actions(
                [CreateAction.make().url(lambda **_: cls.page_url("create"))]
            )
        if table._record_url is None:
            table.record_url(lambda record=None, **_: cls.page_url("view", record))
        return table

    @classmethod
    def get_infolist(cls) -> Infolist:
        infolist = cls.infolist(Infolist.make("infolist"))
        if infolist.get_components():
            return infolist
        # No infolist schema: mirror the form's layout, including nested entries.
        from almasix.orbit.panels.infolist_from_form import components_from_form

        return Infolist.make("infolist").schema(components_from_form(cls.get_form().get_components()))

    @classmethod
    def get_relations(cls) -> list[type[Any]]:
        return []


def _record_value(record: Any, attribute: str) -> Any:
    if isinstance(record, dict):
        return record.get(attribute)
    return getattr(record, attribute, None)


def _singularize(value: str) -> str:
    """Singular form of a URL segment — ``stories`` → ``story``."""
    lower = value.lower()
    if lower.endswith("ies"):
        return value[:-3] + "y"
    if lower.endswith("es") and re.search(r"(s|x|z|ch|sh)es$", lower):
        return value[:-2]
    if lower.endswith("s") and not lower.endswith("ss"):
        return value[:-1]
    return value


def _snake(name: str) -> str:
    out: list[str] = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0:
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


def _pluralize(value: str) -> str:
    """English plural for URL segments (``author`` → ``authors``).

    Runs through singularize first so already-plural stems like ``settings``
    do not become ``settingses``.
    """
    try:
        from almasix.orm.inflector import pluralize, singularize

        return pluralize(singularize(value))
    except Exception:
        pass
    lower = value.lower()
    if re.search(r"(s|x|z|ch|sh)$", lower):
        return value + "es"
    if re.search(r"[^aeiou]y$", lower):
        return value[:-1] + "ies"
    return value + "s"


def _resolve_nav_flag(cls: type[Any], attr: str, *, default: bool = True, **ctx: Any) -> bool:
    """Read a ClassVar bool, or call a same-named classmethod override on a subclass."""
    for klass in cls.__mro__[:-1]:  # exclude ``object``
        if attr not in klass.__dict__:
            continue
        value = klass.__dict__[attr]
        if isinstance(value, classmethod):
            return bool(value.__func__(cls, **ctx))  # type: ignore[misc]
        if callable(value) and not isinstance(value, type):
            continue
        if callable(value):
            return bool(value(**ctx))
        return bool(value)
    return default


def _resolve_nav_str(cls: type[Any], attr: str, **ctx: Any) -> str | None:
    value = getattr(cls, attr, None)
    if callable(value):
        value = value(**ctx)
    if value is None:
        return None
    return str(value)


def _can(user: Any, ability: str, record: Any = None) -> bool:
    if user is None:
        return False
    for attr in ("has_permission", "hasPermissionTo"):
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
    can_fn = getattr(user, "can", None)
    if callable(can_fn):
        try:
            if record is not None:
                allowed = bool(can_fn(ability, record))
            else:
                allowed = bool(can_fn(ability))
        except TypeError:
            allowed = bool(can_fn(ability))
        if allowed:
            return True
        # Gate-backed Authorizable.can() denies unregistered abilities. Fall open
        # so panels work before policies are registered (matches header chrome).
        if _gate_ability_unregistered(user, ability):
            return True
        return False
    return False


def _gate_ability_unregistered(user: Any, ability: str) -> bool:
    """True when ``user.can`` is Gate-backed and ``ability`` is not defined."""
    try:
        from almasix.auth.access.authorizable import Authorizable
    except Exception:
        return False
    if not isinstance(user, Authorizable):
        return False
    try:
        from almasix.auth import Gate

        return not Gate.has(ability)
    except Exception:
        return True
