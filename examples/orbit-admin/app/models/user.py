"""User model for Orbit Admin auth."""

from __future__ import annotations

from almasix.auth import AuthenticatableMixin
from almasix.orm import Model


class User(AuthenticatableMixin, Model):
    fillable = ("name", "email", "password", "remember_token")
    hidden = ("password", "remember_token")
