
"""Form builder wrapping Schema."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Self

from almasix.orbit.schemas.schema import Schema
from almasix.orbit.support.component import Component


class Form(Schema):
    """Filament-style Form configuration object."""

    def schema(self, components: Sequence[Component]) -> Self:  # type: ignore[override]
        return self.components(components)

    def validate(self, data: dict[str, Any] | None = None) -> dict[str, list[str]]:
        """Return field → error messages using simple rule strings."""
        state = data if data is not None else self.get_state()
        errors: dict[str, list[str]] = {}
        for c in self.get_components():
            from almasix.orbit.forms.components import Field

            if not isinstance(c, Field):
                continue
            path = c.get_state_path() or ""
            value = state.get(path)
            for rule in c.get_rules():
                if not isinstance(rule, str):
                    continue
                msg = _check_rule(rule, value, path)
                if msg:
                    errors.setdefault(path, []).append(msg)
        return errors


def _check_rule(rule: str, value: Any, path: str) -> str | None:
    if rule == "required":
        if value is None or value == "" or value == []:
            return f"The {path} field is required."
        return None
    if rule == "email":
        if value and "@" not in str(value):
            return f"The {path} must be a valid email address."
        return None
    if rule == "numeric":
        if value not in (None, "") and not _is_number(value):
            return f"The {path} must be numeric."
        return None
    if rule == "integer":
        if value not in (None, "") and not str(value).lstrip("-").isdigit():
            return f"The {path} must be an integer."
        return None
    if rule == "url":
        if value and not str(value).startswith(("http://", "https://")):
            return f"The {path} must be a valid URL."
        return None
    if rule.startswith("max:"):
        n = int(rule.split(":", 1)[1])
        if value is not None and len(str(value)) > n:
            return f"The {path} must not be greater than {n} characters."
        return None
    if rule.startswith("min:"):
        n = int(rule.split(":", 1)[1])
        if value is not None and len(str(value)) < n:
            return f"The {path} must be at least {n} characters."
        return None
    return None


def _is_number(value: Any) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False
