"""Auth page schemas and MFA provider protocol."""

from __future__ import annotations

from typing import Any, Protocol

from almasix.orbit.forms.components import TextInput
from almasix.orbit.forms.form import Form
from almasix.orbit.panels.page import Page
from almasix.orbit.support.html import e


class Login(Page):
    title = "Sign in"
    slug = "login"
    navigation_label = "Login"

    @classmethod
    def get_form(cls) -> Form:
        return Form.make("login").schema(
            [
                TextInput.make("email").email().required().autocomplete("username"),
                TextInput.make("password").password().required().autocomplete("current-password"),
            ]
        )

    @classmethod
    def render(cls, **ctx: Any) -> str:
        form = cls.get_form()
        return (
            f'<div class="or-page or-page-auth or-page-login">'
            f'<h1 class="or-page-title">{e(cls.get_title())}</h1>'
            f'<form class="or-form" wire:submit="authenticate">'
            f"{form.render(**ctx)}"
            f'<button type="submit" class="or-btn or-btn-primary">Sign in</button>'
            f"</form></div>"
        )


class Register(Page):
    title = "Register"
    slug = "register"

    @classmethod
    def get_form(cls) -> Form:
        return Form.make("register").schema(
            [
                TextInput.make("name").required(),
                TextInput.make("email").email().required(),
                TextInput.make("password").password().required(),
                TextInput.make("password_confirmation").password().required(),
            ]
        )

    @classmethod
    def render(cls, **ctx: Any) -> str:
        return (
            f'<div class="or-page or-page-auth or-page-register">'
            f'<h1 class="or-page-title">{e(cls.get_title())}</h1>'
            f'<form class="or-form" wire:submit="register">'
            f"{cls.get_form().render(**ctx)}"
            f'<button type="submit" class="or-btn or-btn-primary">Create account</button>'
            f"</form></div>"
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
        return (
            f'<div class="or-page or-page-auth or-page-password-reset">'
            f'<h1 class="or-page-title">{e(cls.get_title())}</h1>'
            f'<form class="or-form" wire:submit="requestReset">'
            f"{cls.get_form().render(**ctx)}"
            f'<button type="submit" class="or-btn or-btn-primary">Email reset link</button>'
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
            f'<form class="or-form" wire:submit="saveProfile">'
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
