"""Tenant registration and profile page stubs."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit.panels.page import Page
from almasix.orbit.support.html import e


class RegisterTenant(Page):
    """Base page for creating a new tenant (subclass and override hooks)."""

    title = "Register tenant"
    slug = "new"
    navigation_icon: ClassVar[str] = "heroicon-o-plus-circle"
    should_register_navigation: ClassVar[bool] = False

    @classmethod
    def get_label(cls) -> str:
        return cls.get_title()

    @classmethod
    def form(cls, form: Any = None) -> Any:
        """Return / mutate the registration form schema."""
        return form

    @classmethod
    def handle_registration(cls, data: dict[str, Any], **ctx: Any) -> Any:
        """Create and return the new tenant. Hosts call this after validation."""
        raise NotImplementedError(
            f"{cls.__name__}.handle_registration() must create and return a tenant"
        )

    @classmethod
    def render(cls, **ctx: Any) -> str:
        form = ctx.get("form")
        form_html = ""
        if form is not None and hasattr(form, "render"):
            form_html = form.render(ctx.get("state") or {}, **ctx)
        elif form is not None:
            form_html = str(form)
        else:
            built = cls.form()
            if built is not None and hasattr(built, "render"):
                form_html = built.render(ctx.get("state") or {}, **ctx)
        if not form_html:
            form_html = '<p class="or-muted">Configure a registration form.</p>'
        return (
            f'<div class="or-page or-page-tenant-register">'
            f'<h1 class="or-page-title">{e(cls.get_title())}</h1>'
            f"{form_html}"
            f"</div>"
        )


class EditTenantProfile(Page):
    """Base page for editing the current tenant profile."""

    title = "Tenant profile"
    slug = "profile"
    navigation_icon: ClassVar[str] = "heroicon-o-building-office"
    should_register_navigation: ClassVar[bool] = False

    @classmethod
    def get_label(cls) -> str:
        return cls.get_title()

    @classmethod
    def form(cls, form: Any = None) -> Any:
        """Return / mutate the profile form schema."""
        return form

    @classmethod
    def handle_save(cls, data: dict[str, Any], **ctx: Any) -> Any:
        """Persist tenant profile changes. Hosts call this after validation."""
        raise NotImplementedError(
            f"{cls.__name__}.handle_save() must persist tenant profile changes"
        )

    @classmethod
    def render(cls, **ctx: Any) -> str:
        form = ctx.get("form")
        form_html = ""
        if form is not None and hasattr(form, "render"):
            form_html = form.render(ctx.get("state") or {}, **ctx)
        elif form is not None:
            form_html = str(form)
        else:
            built = cls.form()
            if built is not None and hasattr(built, "render"):
                form_html = built.render(ctx.get("state") or {}, **ctx)
        tenant = ctx.get("tenant")
        subtitle = ""
        if tenant is not None:
            name = getattr(tenant, "name", None) or (
                tenant.get("name") if isinstance(tenant, dict) else None
            )
            if name:
                subtitle = f'<p class="or-muted">{e(str(name))}</p>'
        if not form_html:
            form_html = '<p class="or-muted">Configure a profile form.</p>'
        return (
            f'<div class="or-page or-page-tenant-profile">'
            f'<h1 class="or-page-title">{e(cls.get_title())}</h1>'
            f"{subtitle}"
            f"{form_html}"
            f"</div>"
        )
