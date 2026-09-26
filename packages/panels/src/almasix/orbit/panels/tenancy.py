"""Multi-tenancy configuration, switcher chrome, and query scoping helpers."""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from contextvars import ContextVar
from typing import Any, Protocol, Self, runtime_checkable

from almasix.orbit.support.html import e

# Request-local override. The configured ``.current()`` stays the fallback so
# one visitor's switch cannot leak through the shared panel object.
_active_tenants: ContextVar[dict[int, Tenant | None] | None] = ContextVar(
    "orbit_active_tenants",
    default=None,
)
# Monotonic token. ``id(tenancy)`` is unsafe: a collected instance's id can be
# reused, and the request cache would then show the wrong company.
_request_keys = 0


class Tenant:
    """Current tenant context object (host supplies persistence)."""

    def __init__(
        self,
        id: Any,
        name: str,
        *,
        slug: str | None = None,
        avatar_url: str | None = None,
    ) -> None:
        self.id = id
        self.name = name
        self.slug = slug or str(id)
        self.avatar_url = avatar_url

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "avatar_url": self.avatar_url,
        }

    @classmethod
    def from_model(
        cls,
        obj: Any,
        *,
        slug_attr: str = "slug",
        name_attr: str = "name",
        avatar_attr: str | None = "avatar_url",
    ) -> Tenant:
        """Build a :class:`Tenant` from an ORM / duck-typed model instance."""
        tid = getattr(obj, "id", None)
        if tid is None and isinstance(obj, dict):
            tid = obj.get("id")
        name = _attr(obj, name_attr) or str(tid)
        slug_raw = _attr(obj, slug_attr)
        slug = str(slug_raw) if slug_raw is not None else str(tid)
        avatar = _attr(obj, avatar_attr) if avatar_attr else None
        return cls(tid, str(name), slug=slug, avatar_url=str(avatar) if avatar else None)


@runtime_checkable
class HasTenants(Protocol):
    """User contract: which tenants exist and whether a slug/id is allowed."""

    def get_tenants(self, panel: Any) -> Sequence[Tenant | Any]:  # pragma: no cover
        """Return tenants the user may switch into for ``panel``."""
        ...

    def can_access_tenant(self, tenant: Tenant | Any) -> bool:  # pragma: no cover
        """Return True when the user may open ``tenant`` (URL / switcher)."""
        ...


class Tenancy:
    """Panel-level multi-tenancy configuration and helpers."""

    def __init__(self) -> None:
        global _request_keys
        _request_keys += 1
        self._request_key = _request_keys
        self._tenant_model: type[Any] | None = None
        self._ownership_relationship = "tenant"
        self._slug_attribute = "slug"
        self._name_attribute = "name"
        self._avatar_attribute: str | None = "avatar_url"
        self._current: Tenant | None = None
        self._tenants: list[Tenant] = []
        self._registration: bool | type[Any] = False
        self._profile: bool | type[Any] = False
        self._billing: bool | type[Any] = False
        self._menu_items: list[Any] = []
        self._scope: Callable[[Any, Tenant], Any] | None = None
        self._associate: Callable[[Any, Tenant], Any] | None = None
        self._tenant_route_prefix: bool | str = False
        self._unique_middleware_key: str = "default"
        self._enabled: bool = True
        self._tenant_middleware: list[Any] = []
        self._tenant_middleware_persistent: bool = False

    def model(self, model: type[Any]) -> Self:
        self._tenant_model = model
        self._enabled = True
        return self

    def ownership_relationship(self, name: str) -> Self:
        self._ownership_relationship = name
        return self

    def slug_attribute(self, name: str) -> Self:
        self._slug_attribute = name
        return self

    def name_attribute(self, name: str) -> Self:
        self._name_attribute = name
        return self

    def avatar_attribute(self, name: str | None) -> Self:
        self._avatar_attribute = name
        return self

    def registration(self, condition: bool | type[Any] = True) -> Self:
        self._registration = condition
        return self

    def profile(self, condition: bool | type[Any] = True) -> Self:
        self._profile = condition
        return self

    def billing(self, condition: bool | type[Any] = True) -> Self:
        self._billing = condition
        return self

    def tenants(self, tenants: Sequence[Tenant | Any]) -> Self:
        self._tenants = _dedupe_tenant_ids([self.coerce_tenant(t) for t in tenants])
        return self

    def current(self, tenant: Tenant | Any | None) -> Self:
        """Set the fallback tenant used when this request has not chosen one."""
        self._current = None if tenant is None else self.coerce_tenant(tenant)
        self.release()
        return self

    def get_current(self) -> Tenant | None:
        """Tenant for this request, otherwise the configured fallback."""
        active = _active_tenants.get()
        if isinstance(active, dict) and self._request_key in active:
            return active[self._request_key]
        return self._current

    def adopt(self, tenant: Tenant | Any | None) -> Tenant | None:
        """Select ``tenant`` for this request only. Does not change the fallback."""
        coerced = None if tenant is None else self.coerce_tenant(tenant)
        prev = _active_tenants.get()
        mapping = dict(prev) if isinstance(prev, dict) else {}
        mapping[self._request_key] = coerced
        _active_tenants.set(mapping)
        return coerced

    def release(self) -> None:
        """Drop the request override so :meth:`get_current` returns the fallback."""
        prev = _active_tenants.get()
        if not isinstance(prev, dict) or self._request_key not in prev:
            return
        mapping = dict(prev)
        del mapping[self._request_key]
        _active_tenants.set(mapping)

    def allows(self, user: Any, tenant: Tenant | Any | None) -> bool:
        """True when ``user`` may open ``tenant``. No user means no membership gate."""
        if tenant is None:
            return False
        if user is None:
            return True
        checker = getattr(user, "can_access_tenant", None)
        if not callable(checker):
            return True
        try:
            return bool(checker(tenant))
        except Exception:
            return False

    def session_key(self, panel_id: str) -> str:
        return f"orbit.tenant.{panel_id or 'default'}"

    def remember_slug(self, panel_id: str, slug: str | None) -> None:
        """Store the chosen slug on the current session, when one is started."""
        try:
            from almasix.session.store import get_session

            store = get_session()
        except Exception:
            return
        if store is None:
            return
        key = self.session_key(panel_id)
        if slug:
            store.put(key, str(slug))
        else:
            store.forget(key)

    def recall_slug(self, panel_id: str) -> str | None:
        """Slug saved for this panel, or ``None`` outside a session."""
        try:
            from almasix.session.store import get_session

            store = get_session()
        except Exception:
            return None
        if store is None:
            return None
        value = store.get(self.session_key(panel_id))
        text = str(value).strip() if value else ""
        return text or None

    def switch_path(self, slug: str, panel: Any = None) -> str:
        """Panel home for ``slug``. Switching always leaves the page you were on."""
        extra = self.route_prefix_segment() if self.get_tenant_route_prefix() else ""
        if panel is not None and hasattr(panel, "url"):
            if self.get_tenant_route_prefix():
                if extra:
                    return str(panel.url(extra, slug))
                return str(panel.url(slug))
            return str(panel.url() or "/") or "/"
        if self.get_tenant_route_prefix():
            if extra:
                return f"/{extra}/{slug}"
            return f"/{slug}"
        return "/"

    def find_by_slug(self, slug: str | None) -> Tenant | None:
        if slug is None or slug == "":
            return None
        needle = str(slug)
        for tenant in self.get_tenants():
            if tenant.slug == needle or str(tenant.id) == needle:
                return tenant
        return None

    def get_tenants(self) -> list[Tenant]:
        return list(self._tenants)

    def resolve_tenants(self, user: Any = None, panel: Any = None) -> list[Tenant]:
        """Prefer configured tenants; else ask a :class:`HasTenants` user."""
        if self._tenants:
            return [tenant for tenant in self._tenants if self.allows(user, tenant)]
        if user is None:
            return []
        getter = getattr(user, "get_tenants", None)
        if not callable(getter):
            return []
        try:
            raw = getter(panel)
        except TypeError:
            raw = getter()
        out: list[Tenant] = []
        for item in raw or []:
            tenant = self.coerce_tenant(item)
            checker = getattr(user, "can_access_tenant", None)
            if callable(checker) and not checker(tenant):
                continue
            out.append(tenant)
        return out

    def coerce_tenant(self, value: Tenant | Any) -> Tenant:
        if isinstance(value, Tenant):
            return value
        return Tenant.from_model(
            value,
            slug_attr=self._slug_attribute,
            name_attr=self._name_attribute,
            avatar_attr=self._avatar_attribute,
        )

    def scope_using(self, callback: Callable[[Any, Tenant], Any]) -> Self:
        """ORM / list handoff: ``callback(query, tenant) -> query``."""
        self._scope = callback
        return self

    def scope_query(self, query: Any) -> Any:
        """Limit ``query`` to the current tenant.

        A ``scope_using`` callback replaces the default. Without one, rows and
        queries that carry the ownership id (``tenant_id`` by default) are
        filtered. Rows with no ownership field stay, so shared catalogs keep
        showing.
        """
        tenant = self.get_current()
        if tenant is None:
            return query
        if self._scope is not None:
            return self._scope(query, tenant)
        fk = f"{self._ownership_relationship or 'tenant'}_id"
        return _default_tenant_scope(query, tenant, fk)

    def orm_constraint(self, resource: Any = None) -> tuple[str, Any] | None:
        """``(column, id)`` for an ORM ``where`` when no custom scope callback is set."""
        if self._scope is not None or not self.is_enabled():
            return None
        if resource is not None:
            scoped = getattr(resource, "is_tenant_scoped", None)
            if callable(scoped) and not scoped():
                return None
            if not getattr(resource, "is_scoped_to_tenant", True):
                return None
        tenant = self.get_current()
        if tenant is None:
            return None
        return (f"{self._ownership_relationship or 'tenant'}_id", tenant.id)

    def associate_using(self, callback: Callable[[Any, Tenant], Any]) -> Self:
        """Set ownership on create: ``callback(record, tenant) -> record``."""
        self._associate = callback
        return self

    def associate_record(self, record: Any) -> Any:
        """Attach the current tenant to ``record`` (FK helper; hosts opt in)."""
        current = self.get_current()
        if current is None:
            return record
        if self._associate is not None:
            return self._associate(record, current)
        rel = self._ownership_relationship or "tenant"
        fk = f"{rel}_id"
        if isinstance(record, dict):
            out = dict(record)
            out.setdefault(fk, current.id)
            return out
        if not hasattr(record, fk) or getattr(record, fk, None) is None:
            try:
                setattr(record, fk, current.id)
            except Exception:
                pass
        return record

    def menu_items(self, items: Sequence[Any]) -> Self:
        self._menu_items = list(items)
        return self

    def tenant_route_prefix(self, prefix: bool | str = True) -> Self:
        """Include ``{tenant}`` (and optional segment) in panel resource URLs."""
        self._tenant_route_prefix = prefix
        return self

    def get_tenant_route_prefix(self) -> bool | str:
        return self._tenant_route_prefix

    def unique_middleware_key(self, key: str) -> Self:
        self._unique_middleware_key = str(key or "default")
        return self

    def get_unique_middleware_key(self) -> str:
        return self._unique_middleware_key

    def scope_name(self) -> str:
        """Stable name for docs / host-level query scopes."""
        return f"orbit.tenancy.{self._unique_middleware_key}"

    def tenant_middleware(
        self,
        middleware: Sequence[Any],
        *,
        is_persistent: bool = False,
    ) -> Self:
        self._tenant_middleware = list(middleware)
        self._tenant_middleware_persistent = bool(is_persistent)
        return self

    def get_tenant_middleware(self) -> list[Any]:
        return list(self._tenant_middleware)

    def tenant_middleware_is_persistent(self) -> bool:
        return self._tenant_middleware_persistent

    def is_enabled(self) -> bool:
        if not self._enabled:
            return False
        return (
            self._tenant_model is not None
            or bool(self._tenants)
            or self._registration is not False
            or self._profile is not False
            or self._billing is not False
            or self._scope is not None
            or self._current is not None
        )

    def disable(self) -> Self:
        self._enabled = False
        return self

    def get_tenant_model(self) -> type[Any] | None:
        return self._tenant_model

    def get_ownership_relationship(self) -> str:
        return self._ownership_relationship

    def get_slug_attribute(self) -> str:
        return self._slug_attribute

    def get_name_attribute(self) -> str:
        return self._name_attribute

    def get_avatar_attribute(self) -> str | None:
        return self._avatar_attribute

    def registration_enabled(self) -> bool:
        return self._registration is not False

    def profile_enabled(self) -> bool:
        return self._profile is not False

    def billing_enabled(self) -> bool:
        return self._billing is not False

    def registration_page(self) -> type[Any] | None:
        from almasix.orbit.panels.pages.tenancy import RegisterTenant

        return _resolve_tenancy_page(self._registration, default_cls=RegisterTenant)

    def profile_page(self) -> type[Any] | None:
        from almasix.orbit.panels.pages.tenancy import EditTenantProfile

        return _resolve_tenancy_page(self._profile, default_cls=EditTenantProfile)

    def billing_page(self) -> type[Any] | None:
        from almasix.orbit.panels.pages.tenancy import ManageBilling

        return _resolve_tenancy_page(self._billing, default_cls=ManageBilling)

    def route_prefix_segment(self) -> str:
        """URL segment before ``{tenant}``, or empty when prefix is a bare bool."""
        prefix = self._tenant_route_prefix
        if prefix is False or prefix is True:
            return ""
        return str(prefix).strip().strip("/")

    def path_prefix_for(self, tenant_slug: str | None = None) -> str:
        """Build ``[extra/]{tenant}`` path fragment (no leading slash) when routing."""
        if not self._tenant_route_prefix:
            return ""
        slug = tenant_slug or (self._current.slug if self._current else "{tenant}")
        extra = self.route_prefix_segment()
        if extra:
            return f"{extra}/{slug}"
        return str(slug)

    def render_menu(self, *, panel: Any = None) -> str:
        """Links for register / profile / billing and custom menu items."""
        bits: list[str] = []
        base = ""
        if panel is not None and hasattr(panel, "url"):
            base = str(panel.url()).rstrip("/")

        def _href(slug: str) -> str:
            if base:
                return f"{base}/{slug}"
            return f"/{slug}"

        if self.registration_enabled():
            bits.append(
                f'<a class="or-tenant-menu-item" href="{e(_href("new"))}">'
                f"<span>Register</span></a>"
            )
        if self.profile_enabled():
            bits.append(
                f'<a class="or-tenant-menu-item" href="{e(_href("profile"))}">'
                f"<span>Tenant profile</span></a>"
            )
        if self.billing_enabled():
            bits.append(
                f'<a class="or-tenant-menu-item" href="{e(_href("billing"))}">'
                f"<span>Billing</span></a>"
            )
        for item in self._menu_items:
            if isinstance(item, dict):
                label = e(str(item.get("label") or item.get("name") or "Item"))
                url = e(str(item.get("url") or "#"))
                bits.append(
                    f'<a class="or-tenant-menu-item" href="{url}"><span>{label}</span></a>'
                )
            elif hasattr(item, "render"):
                bits.append(str(item.render()))
            else:
                bits.append(f'<span class="or-tenant-menu-item">{e(str(item))}</span>')
        if not bits:
            return ""
        return f'<div class="or-tenant-menu-actions">{"".join(bits)}</div>'

    def render_switcher(self, *, user: Any = None, panel: Any = None) -> str:
        tenants = self.resolve_tenants(user=user, panel=panel)
        current = self.get_current()
        if not tenants and current is None:
            return ""
        if current is None and tenants:
            current = tenants[0]
        button_label = e(current.name if current else "Tenant")
        avatar = _avatar_html(current)
        options_html: list[str] = []
        select_opts: list[str] = []
        for t in tenants:
            is_current = current is not None and t.id == current.id
            active = " is-active" if is_current else ""
            sel = " selected" if is_current else ""
            t_avatar = _avatar_html(t)
            option_label = f"{t_avatar}<span>{e(t.name)}</span>"
            if self.get_tenant_route_prefix():
                href = e(self.switch_path(t.slug, panel))
                options_html.append(
                    f'<a class="or-tenant-option{active}" href="{href}" '
                    f'data-tenant="{e(t.slug)}">{option_label}</a>'
                )
            else:
                options_html.append(
                    f'<button type="button" class="or-tenant-option{active}" '
                    f'data-tenant="{e(t.slug)}" '
                    f'wire:click="setTenant(\'{e(t.slug)}\')" '
                    f'@click="open = false">{option_label}</button>'
                )
            select_opts.append(
                f'<option value="{e(t.slug)}"{sel}>{e(t.name)}</option>'
            )
        menu = self.render_menu(panel=panel)
        divider = (
            '<div class="or-tenant-menu-divider" role="separator"></div>'
            if menu and options_html
            else ""
        )
        select = ""
        if select_opts:
            current_slug = e(current.slug if current else "")
            select = (
                f'<select id="or-tenant" class="or-sr-only" name="tenant" '
                f'wire:model.live="tenant" aria-hidden="true" tabindex="-1">'
                f'{"".join(select_opts)}</select>'
                f'<input type="hidden" data-orbit-tenant="{current_slug}" />'
            )
        return (
            '<div class="or-tenant-switcher" x-data="{ open: false }" '
            '@click.outside="open = false">'
            '<button type="button" class="or-tenant-switcher-btn" '
            '@click="open = !open" aria-haspopup="true" '
            ':aria-expanded="open">'
            f"{avatar}"
            f'<span class="or-tenant-name">{button_label}</span>'
            '<svg class="or-icon or-tenant-chevron" width="14" height="14" '
            'viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">'
            '<path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.17'
            "l3.71-3.94a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5"
            'a.75.75 0 01.02-1.06z" clip-rule="evenodd"/></svg>'
            "</button>"
            '<div class="or-tenant-menu" x-show="open" x-cloak role="menu">'
            f"{menu}{divider}{''.join(options_html)}{select}"
            "</div></div>"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.is_enabled(),
            "model": getattr(self._tenant_model, "__name__", None),
            "ownership_relationship": self._ownership_relationship,
            "slug_attribute": self._slug_attribute,
            "name_attribute": self._name_attribute,
            "avatar_attribute": self._avatar_attribute,
            "registration": self.registration_enabled(),
            "profile": self.profile_enabled(),
            "billing": self.billing_enabled(),
            "tenant_route_prefix": self._tenant_route_prefix,
            "unique_middleware_key": self._unique_middleware_key,
            "scope_name": self.scope_name(),
            "tenant_middleware": [str(m) for m in self._tenant_middleware],
            "tenant_middleware_persistent": self._tenant_middleware_persistent,
            "current": self._current.to_dict() if self._current else None,
            "tenants": [t.to_dict() for t in self._tenants],
            "menu_items": list(self._menu_items),
        }


def _resolve_tenancy_page(
    value: bool | type[Any],
    *,
    default_cls: type[Any],
) -> type[Any] | None:
    if value is False:
        return None
    if value is True:
        return default_cls
    if isinstance(value, type):
        return value
    return default_cls


def _numeric_id(value: Any) -> int | None:
    """Integer id, or ``None`` when ``value`` is not a plain number."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip()
    if text.isdigit():
        return int(text)
    return None


def _dedupe_tenant_ids(tenants: list[Tenant]) -> list[Tenant]:
    """Give each company its own numeric id. Later duplicates take the next free number."""
    taken: set[int] = set()
    out: list[Tenant] = []
    for tenant in tenants:
        number = _numeric_id(tenant.id)
        if number is None:
            out.append(tenant)
            continue
        if number in taken:
            number = max(taken) + 1
            tenant = Tenant(
                number,
                tenant.name,
                slug=tenant.slug,
                avatar_url=tenant.avatar_url,
            )
        taken.add(number)
        out.append(tenant)
    return out


def _row_tenant_id(row: Any, keys: tuple[str, ...]) -> Any:
    """Ownership id when ``row`` carries one of ``keys``, else ``None``."""
    if isinstance(row, dict):
        for key in keys:
            if key in row:
                return row.get(key)
        return None
    for key in keys:
        if hasattr(row, key):
            return getattr(row, key)
    return None


def _default_tenant_scope(query: Any, tenant: Tenant, fk: str) -> Any:
    """Keep rows that belong to ``tenant`` or that have no ownership field."""
    keys = (fk, "tenant_id") if fk != "tenant_id" else ("tenant_id",)
    if isinstance(query, list):
        kept: list[Any] = []
        for row in query:
            owner = _row_tenant_id(row, keys)
            if owner is None or str(owner) == str(tenant.id):
                kept.append(row)
        return kept
    where = getattr(query, "where", None)
    if callable(where):
        try:
            return where(fk, tenant.id)
        except Exception:
            return query
    return query


def _slugify(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")
    return text or "tenant"


def _attr(obj: Any, name: str | None) -> Any:
    if not name:
        return None
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


def _avatar_html(tenant: Tenant | None) -> str:
    if tenant is None:
        return '<span class="or-tenant-avatar" aria-hidden="true">?</span>'
    if tenant.avatar_url:
        return (
            f'<img class="or-tenant-avatar" src="{e(tenant.avatar_url)}" '
            f'alt="" width="28" height="28" />'
        )
    initials = "".join(p[:1] for p in str(tenant.name).split()[:2]).upper() or "?"
    return f'<span class="or-tenant-avatar" aria-hidden="true">{e(initials)}</span>'
