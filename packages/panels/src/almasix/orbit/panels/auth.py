"""Auth page schemas and MFA provider protocol."""

from __future__ import annotations

from typing import Any

from almasix.orbit.forms.components import Checkbox, TextInput
from almasix.orbit.forms.form import Form
from almasix.orbit.panels.mfa import (
    AppAuthentication as AppAuthentication,
)
from almasix.orbit.panels.mfa import (
    EmailAuthentication as EmailAuthentication,
)
from almasix.orbit.panels.mfa import (
    MfaProvider as MfaProvider,
)
from almasix.orbit.panels.mfa import (
    render_app_setup,
)
from almasix.orbit.panels.page import Page
from almasix.orbit.support.conduit_attrs import conduit_attr
from almasix.orbit.support.html import e


def _login_brand_html(
    *,
    brand: str,
    brand_logo: str | None = None,
    brand_logo_dark: str | None = None,
    brand_logo_only: bool = False,
) -> str:
    """Brand mark for auth pages.

    - Logo only when ``brand_logo_only`` and a logo is set
    - Name only when no logo is set
    - Logo + name side-by-side when both are shown
    """
    show_name = not (brand_logo and brand_logo_only)
    parts: list[str] = []
    if brand_logo:
        alt = e(brand) if not show_name else ""
        dark = brand_logo_dark or brand_logo
        if dark == brand_logo:
            logo = f'<img class="or-login-logo" src="{e(brand_logo)}" alt="{alt}" />'
        else:
            logo = (
                f'<img class="or-login-logo or-login-logo-light" src="{e(brand_logo)}" alt="{alt}" />'
                f'<img class="or-login-logo or-login-logo-dark" src="{e(dark)}" alt="" />'
            )
        parts.append(f'<span class="or-login-logo-slot">{logo}</span>')
    if show_name:
        parts.append(f'<span class="or-login-brand-name">{e(brand)}</span>')
    if not parts:
        return ""
    classes = "or-login-brand"
    if brand_logo and brand_logo_only:
        classes += " or-login-brand-logo-only"
    return f'<div class="{classes}">{"".join(parts)}</div>'


def _login_header_html(
    *,
    title: str,
    subtitle: str,
    brand: str,
    brand_logo: str | None = None,
    brand_logo_dark: str | None = None,
    brand_logo_only: bool = False,
) -> str:
    return (
        f'<header class="or-login-header">'
        f"{_login_brand_html(brand=brand, brand_logo=brand_logo, brand_logo_dark=brand_logo_dark, brand_logo_only=brand_logo_only)}"
        f'<h1 class="or-login-title">{e(title)}</h1>'
        f'<p class="or-login-subtitle">{subtitle}</p>'
        f"</header>"
    )


class Login(Page):
    title = "Sign in"
    slug = "login"
    navigation_label = "Login"

    @classmethod
    def get_form(cls) -> Form:
        return Form.make("login").schema(
            [
                TextInput.make("email")
                .label("Email address")
                .email()
                .required()
                .autocomplete("username"),
                TextInput.make("password")
                .label("Password")
                .password()
                .required()
                .autocomplete("current-password"),
                Checkbox.make("remember").label("Remember me"),
            ]
        )

    @classmethod
    def render(cls, **ctx: Any) -> str:
        brand = str(ctx.get("brand") or "Orbit")
        brand_logo = ctx.get("brand_logo")
        brand_logo_dark = ctx.get("brand_logo_dark")
        brand_logo_only = bool(ctx.get("brand_logo_only"))
        error = ctx.get("error")
        form = cls.get_form()
        state = ctx.get("data")
        if not isinstance(state, dict):
            state = {
                "email": ctx.get("email") or "",
                "remember": bool(ctx.get("remember")),
            }
        error_html = ""
        if error:
            error_html = (
                f'<div class="or-login-alert" role="alert">{e(str(error))}</div>'
            )
        subtitle = f"Welcome back. Sign in to continue to {e(brand)}."
        footer = ""
        if ctx.get("show_signup") and ctx.get("signup_url"):
            footer = (
                f'<p class="or-login-footer">'
                f"Don't have an account? "
                f'<a class="or-login-footer-link" href="{e(str(ctx["signup_url"]))}">Sign up</a>'
                f"</p>"
            )
        return (
            f'<div class="or-page or-page-auth or-page-login">'
            f"{_login_header_html(title=cls.get_title(), subtitle=subtitle, brand=brand, brand_logo=brand_logo, brand_logo_dark=brand_logo_dark, brand_logo_only=brand_logo_only)}"
            f"{error_html}"
            f'<form class="or-form or-login-form"{conduit_attr("submit", "authenticate")}>'
            f"{form.render(state)}"
            f'<button type="submit" class="or-btn or-btn-primary or-btn-block">'
            f"Sign in</button>"
            f"</form>"
            f"{footer}"
            f"</div>"
        )


class Register(Page):
    title = "Register"
    slug = "register"

    @classmethod
    def get_form(cls) -> Form:
        return Form.make("register").schema(
            [
                TextInput.make("name").required(),
                TextInput.make("email")
                .email()
                .required()
                .unique("users", "email")
                .validation_messages({"unique": "An account with this email already exists."}),
                TextInput.make("password").password().required(),
                TextInput.make("password_confirmation").password().required(),
            ]
        )

    @classmethod
    def render(cls, **ctx: Any) -> str:
        brand = str(ctx.get("brand") or "Orbit")
        brand_logo = ctx.get("brand_logo")
        brand_logo_dark = ctx.get("brand_logo_dark")
        brand_logo_only = bool(ctx.get("brand_logo_only"))
        error = ctx.get("error")
        state = ctx.get("data")
        if not isinstance(state, dict):
            state = {
                "name": ctx.get("name") or "",
                "email": ctx.get("email") or "",
            }
        error_html = ""
        if error:
            error_html = (
                f'<div class="or-login-alert" role="alert">{e(str(error))}</div>'
            )
        subtitle = f"Create an account to use {e(brand)}."
        footer = ""
        if ctx.get("login_url"):
            footer = (
                f'<p class="or-login-footer">'
                f"Already registered? "
                f'<a class="or-login-footer-link" href="{e(str(ctx["login_url"]))}">Sign in</a>'
                f"</p>"
            )
        return (
            f'<div class="or-page or-page-auth or-page-register">'
            f"{_login_header_html(title=cls.get_title(), subtitle=subtitle, brand=brand, brand_logo=brand_logo, brand_logo_dark=brand_logo_dark, brand_logo_only=brand_logo_only)}"
            f"{error_html}"
            f'<form class="or-form or-login-form"{conduit_attr("submit", "register")}>'
            f"{cls.get_form().render(state)}"
            f'<button type="submit" class="or-btn or-btn-primary or-btn-block">'
            f"Create account</button>"
            f"</form>"
            f"{footer}"
            f"</div>"
        )


class PasswordReset(Page):
    title = "Reset password"
    slug = "password-reset"

    @classmethod
    def get_form(cls) -> Form:
        return Form.make("password_reset").schema(
            [TextInput.make("email").email().required()]
        )

    @classmethod
    def render(cls, **ctx: Any) -> str:
        brand = str(ctx.get("brand") or "Orbit")
        return (
            f'<div class="or-page or-page-auth or-page-password-reset">'
            f"{_login_header_html(title=cls.get_title(), subtitle='We will email you a reset link.', brand=brand, brand_logo=ctx.get('brand_logo'), brand_logo_dark=ctx.get('brand_logo_dark'), brand_logo_only=bool(ctx.get('brand_logo_only')))}"
            f'<form class="or-form or-login-form"{conduit_attr("submit", "requestReset")}>'
            f"{cls.get_form().render(**ctx)}"
            f'<button type="submit" class="or-btn or-btn-primary or-btn-block">'
            f"Email reset link</button>"
            f"</form></div>"
        )


class Profile(Page):
    title = "Profile"
    slug = "profile"

    @classmethod
    def get_form(cls) -> Form:
        return Form.make("profile").schema(
            [
                TextInput.make("name").required(),
                TextInput.make("email").email().required(),
            ]
        )

    @classmethod
    def render(cls, **ctx: Any) -> str:
        return (
            f'<div class="or-page or-page-profile">'
            f'<h1 class="or-page-title">{e(cls.get_title())}</h1>'
            f'<form class="or-form"{conduit_attr("submit", "saveProfile")}>'
            f"{cls.get_form().render(**ctx)}"
            f'<button type="submit" class="or-btn or-btn-primary">Save</button>'
            f"</form></div>"
        )


class MfaChallenge(Page):
    title = "Two-factor authentication"
    slug = "mfa-challenge"

    @classmethod
    def render(cls, **ctx: Any) -> str:
        brand = str(ctx.get("brand") or "Orbit")
        error = ctx.get("error")
        providers = list(ctx.get("providers") or [])
        user = ctx.get("user")
        selected_id = str(ctx.get("provider") or (providers[0].get_id() if providers else "app"))
        selected = next((p for p in providers if p.get_id() == selected_id), providers[0] if providers else None)
        error_html = ""
        if error:
            error_html = f'<div class="or-login-alert" role="alert">{e(str(error))}</div>'
        tabs = ""
        if len(providers) > 1:
            buttons = []
            for provider in providers:
                pid = e(provider.get_id())
                label = "Authenticator" if provider.get_id() == "app" else "Email"
                current = " aria-current=\"page\"" if provider.get_id() == selected_id else ""
                buttons.append(
                    f'<button type="button" class="or-btn or-btn-sm or-btn-gray" '
                    f'{conduit_attr("click", "selectProvider")}'
                    f' data-provider="{pid}"{current}>{e(label)}</button>'
                )
            tabs = f'<div class="or-mfa-providers">{"".join(buttons)}</div>'
        form_html = ""
        resend = ""
        if selected is not None:
            form_html = selected.get_challenge_form().render(ctx.get("data") or {})
            if selected.get_id() == "email":
                resend = (
                    f'<button type="button" class="or-link-btn" '
                    f'{conduit_attr("click", "resendCode")}>Resend code</button>'
                )
        setup = ""
        if selected is not None and selected.get_id() == "app" and ctx.get("show_setup"):
            setup = render_app_setup(selected.provision(user))
        sent = ""
        if ctx.get("sent"):
            sent = '<p class="or-mfa-sent">A new code is on its way.</p>'
        return (
            f'<div class="or-page or-page-auth or-page-mfa">'
            f"{_login_header_html(title=cls.get_title(), subtitle='Enter the code from your authenticator or email.', brand=brand, brand_logo=ctx.get('brand_logo'), brand_logo_dark=ctx.get('brand_logo_dark'), brand_logo_only=bool(ctx.get('brand_logo_only')))}"
            f"{error_html}{tabs}{setup}{sent}"
            f'<form class="or-form or-login-form"{conduit_attr("submit", "verifyMfa")}>'
            f"{form_html}"
            f'<button type="submit" class="or-btn or-btn-primary or-btn-block">Verify</button>'
            f"</form>{resend}</div>"
        )
