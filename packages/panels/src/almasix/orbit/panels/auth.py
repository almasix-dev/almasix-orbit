"""Auth page schemas and MFA provider protocol."""

from __future__ import annotations

from typing import Any, Protocol

from almasix.orbit.forms.components import Checkbox, TextInput
from almasix.orbit.forms.form import Form
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
            f"{form.render()}"
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
            f"{cls.get_form().render()}"
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


class MfaProvider(Protocol):
    """Host implements TOTP/email MFA; Orbit supplies challenge schema hooks."""

    def get_id(self) -> str: ...

    def is_enabled(self, user: Any) -> bool: ...

    def get_management_schema(self) -> Form: ...

    def get_challenge_form(self) -> Form: ...


class AppAuthentication:
    """Built-in TOTP-shaped MFA provider (host verifies codes)."""

    def __init__(self, *, brand_name: str = "Orbit", code_expiry_seconds: int = 30) -> None:
        self.brand_name = brand_name
        self.code_expiry_seconds = code_expiry_seconds

    def get_id(self) -> str:
        return "app"

    def is_enabled(self, user: Any) -> bool:
        return bool(getattr(user, "mfa_app_enabled", False))

    def get_management_schema(self) -> Form:
        return Form.make("mfa_app").schema(
            [TextInput.make("code").label("Authenticator code").required()]
        )

    def get_challenge_form(self) -> Form:
        return Form.make("mfa_challenge").schema(
            [TextInput.make("code").label("Authentication code").required()]
        )
