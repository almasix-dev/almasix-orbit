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


class ManageBilling(Page):
    """Default tenant billing page — lists plans from the panel billing provider."""

    title = "Billing"
    slug = "billing"
    navigation_icon: ClassVar[str] = "heroicon-o-credit-card"
    should_register_navigation: ClassVar[bool] = False

    @classmethod
    def get_label(cls) -> str:
        return cls.get_title()

    @classmethod
    def handle_subscribe(cls, plan_id: str, **ctx: Any) -> dict[str, Any]:
        panel = ctx.get("panel")
        getter = getattr(panel, "get_billing_provider", None) if panel is not None else None
        provider = getter() if callable(getter) else None
        if provider is None:
            return {"ok": False, "error": "No billing provider."}
        subscribe = getattr(provider, "subscribe", None)
        if not callable(subscribe):
            return {"ok": False, "error": "Provider cannot subscribe."}
        try:
            result = subscribe(
                str(plan_id),
                tenant=ctx.get("tenant"),
                user=ctx.get("user"),
            )
        except Exception as exc:
            return {"ok": False, "error": str(exc) or "Subscribe failed."}
        return dict(result) if isinstance(result, dict) else {"ok": True}

    @classmethod
    def render(cls, **ctx: Any) -> str:
        panel = ctx.get("panel")
        tenant = ctx.get("tenant")
        getter = getattr(panel, "get_billing_provider", None) if panel is not None else None
        provider = getter() if callable(getter) else None
        plans: list[Any] = []
        current: dict[str, Any] | None = None
        portal: str | None = None
        if provider is not None:
            try:
                plans = list(provider.plans(tenant=tenant) or [])
            except Exception:
                plans = []
            try:
                current = provider.current_subscription(tenant=tenant)
            except Exception:
                current = None
            try:
                portal = provider.portal_url(tenant=tenant)
            except Exception:
                portal = None
        current_id = ""
        current_label = ""
        if isinstance(current, dict):
            current_id = str(current.get("plan_id") or "")
            plan = current.get("plan") or {}
            if isinstance(plan, dict):
                current_label = str(plan.get("name") or current_id)
            elif current_id:
                current_label = current_id
        status = (
            f'<p class="or-muted">Current plan: {e(current_label)}</p>'
            if current_label
            else '<p class="or-muted">No active subscription.</p>'
        )
        portal_html = (
            f'<p><a class="or-btn or-btn-sm" href="{e(portal)}">Customer portal</a></p>'
            if portal
            else ""
        )
        cards: list[str] = []
        for plan in plans:
            try:
                data = plan.to_dict() if hasattr(plan, "to_dict") else dict(plan)
            except Exception:
                data = {
                    "id": getattr(plan, "id", ""),
                    "name": getattr(plan, "name", plan),
                }
            pid = str(data.get("id") or "")
            name = e(str(data.get("name") or pid))
            label = e(str(data.get("price_label") or data.get("interval") or ""))
            desc = e(str(data.get("description") or ""))
            current_class = " is-current" if pid and pid == current_id else ""
            action = (
                '<span class="or-muted">Current plan</span>'
                if pid and pid == current_id
                else (
                    '<form method="post" class="or-billing-subscribe">'
                    f'<input type="hidden" name="plan_id" value="{e(pid)}" />'
                    '<button type="submit" class="or-btn or-btn-sm">Subscribe</button>'
                    "</form>"
                )
            )
            desc_html = f'<p class="or-muted">{desc}</p>' if desc else ""
            cards.append(
                f'<article class="or-card or-billing-plan{current_class}">'
                f"<h2>{name}</h2>"
                f'<p class="or-billing-price">{label}</p>'
                f"{desc_html}"
                f"{action}"
                f"</article>"
            )
        body = "".join(cards) or '<p class="or-muted">No plans configured.</p>'
        return (
            f'<div class="or-page or-page-tenant-billing">'
            f'<h1 class="or-page-title">{e(cls.get_title())}</h1>'
            f"{status}{portal_html}"
            f'<div class="or-billing-plans">{body}</div>'
            f"</div>"
        )
