"""Multi-tenancy configuration and query scoping helpers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Self

from almasix.orbit.support.html import e


class Tenant:
    """Current tenant context object (host supplies persistence)."""

    def __init__(self, id: Any, name: str, *, slug: str | None = None) -> None:
        self.id = id
        self.name = name
        self.slug = slug or str(id)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "slug": self.slug}


class Tenancy:
    def __init__(self) -> None:
        self._tenant_model: type[Any] | None = None
        self._ownership_relationship = "tenant"
        self._slug_attribute = "slug"
        self._name_attribute = "name"
        self._current: Tenant | None = None
        self._tenants: list[Tenant] = []
        self._registration_enabled = False
        self._profile_enabled = False
        self._billing_enabled = False
        self._menu_items: list[Any] = []
        self._scope: Callable[[Any, Tenant], Any] | None = None

    def model(self, model: type[Any]) -> Self:
        self._tenant_model = model
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

    def registration(self, condition: bool = True) -> Self:
        self._registration_enabled = condition
        return self

    def profile(self, condition: bool = True) -> Self:
        self._profile_enabled = condition
        return self

    def billing(self, condition: bool = True) -> Self:
        self._billing_enabled = condition
        return self

    def tenants(self, tenants: list[Tenant]) -> Self:
        self._tenants = list(tenants)
        return self

    def current(self, tenant: Tenant | None) -> Self:
        self._current = tenant
        return self

    def get_current(self) -> Tenant | None:
        return self._current

    def scope_using(self, callback: Callable[[Any, Tenant], Any]) -> Self:
        """ORM handoff: ``callback(query, tenant) -> query``."""
        self._scope = callback
        return self

    def scope_query(self, query: Any) -> Any:
        if self._current is None or self._scope is None:
            return query
        return self._scope(query, self._current)

    def menu_items(self, items: list[Any]) -> Self:
        self._menu_items = list(items)
        return self

    def render_switcher(self) -> str:
        if not self._tenants:
            return ""
        options = []
        for t in self._tenants:
            sel = " selected" if self._current and t.id == self._current.id else ""
            options.append(f'<option value="{e(t.slug)}"{sel}>{e(t.name)}</option>')
        return (
            '<div class="or-tenant-switcher">'
            f'<label class="or-label" for="or-tenant">Tenant</label>'
            f'<select id="or-tenant" class="or-select" name="tenant" wire:model.live="tenant">'
            f'{"".join(options)}</select></div>'
        )
