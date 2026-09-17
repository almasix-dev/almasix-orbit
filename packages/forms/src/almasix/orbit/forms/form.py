"""Form builder wrapping Schema."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import date, datetime
from typing import Any, Self

from almasix.orbit.schemas.schema import Schema
from almasix.orbit.support.component import Component
from almasix.orbit.support.evaluate import evaluate

_UniqueChecker = Callable[..., bool]
_ExistsChecker = Callable[..., bool]


class Form(Schema):
    """Filament-style Form configuration object."""

    _unique_checker: _UniqueChecker | None = None
    _exists_checker: _ExistsChecker | None = None

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._readonly = False

    def schema(self, components: Sequence[Component]) -> Self:  # type: ignore[override]
        return self.components(components)

    def readonly(self, condition: bool = True) -> Self:
        self._readonly = condition
        return self

    def is_readonly(self) -> bool:
        return self._readonly

    @classmethod
    def unique_using(cls, checker: _UniqueChecker | None) -> type[Form]:
        """Register a callback for ``unique:…`` rules: ``(value, table, column, **ctx) -> bool``."""
        cls._unique_checker = checker
        return cls

    @classmethod
    def exists_using(cls, checker: _ExistsChecker | None) -> type[Form]:
        """Register a callback for ``exists:…`` rules: ``(value, table, column, **ctx) -> bool``."""
        cls._exists_checker = checker
        return cls

    def validate(self, data: dict[str, Any] | None = None, **ctx: Any) -> dict[str, list[str]]:
        """Return field → error messages using rule strings and/or callables."""
        state = data if data is not None else self.get_state()
        errors: dict[str, list[str]] = {}
        for c in self.get_components():
            from almasix.orbit.forms.components import Field

            if not isinstance(c, Field):
                continue
            path = c.get_state_path() or ""
            value = state.get(path)
            attr = c.get_validation_attribute(**ctx) or path
            field_ctx = {
                **ctx,
                "state": state,
                "value": value,
                "field": c,
                "attribute": attr,
                "unique": ctx.get("unique", Form._unique_checker),
                "exists": ctx.get("exists", Form._exists_checker),
            }
            for rule in c.get_rules(**field_ctx):
                if callable(rule):
                    result = evaluate(rule, value, **field_ctx)
                    if callable(result):
                        continue
                    if result is True or result is None:
                        continue
                    if result is False:
                        errors.setdefault(path, []).append(
                            c.format_validation_message("default", attr, f"The {attr} field is invalid.")
                        )
                    else:
                        errors.setdefault(path, []).append(str(result))
                    continue
                if not isinstance(rule, str):
                    continue
                msg = _check_rule(
                    rule,
                    value,
                    path,
                    attr=attr,
                    field=c,
                    state=state,
                    unique=field_ctx.get("unique"),
                    exists=field_ctx.get("exists"),
                )
                if msg:
                    errors.setdefault(path, []).append(msg)
        return errors


def _check_rule(
    rule: str,
    value: Any,
    path: str,
    *,
    attr: str,
    field: Any = None,
    state: dict[str, Any] | None = None,
    **ctx: Any,
) -> str | None:
    state = state or {}

    def msg(key: str, default: str, **repl: Any) -> str:
        if field is not None and hasattr(field, "format_validation_message"):
            return field.format_validation_message(key, attr, default, **repl)
        return default

    if rule == "required":
        if value is None or value == "" or value == []:
            return msg("required", f"The {attr} field is required.")
        return None
    if rule == "email":
        if value and "@" not in str(value):
            return msg("email", f"The {attr} must be a valid email address.")
        return None
    if rule == "numeric":
        if value not in (None, "") and not _is_number(value):
            return msg("numeric", f"The {attr} must be numeric.")
        return None
    if rule == "integer":
        if value not in (None, "") and not str(value).lstrip("-").isdigit():
            return msg("integer", f"The {attr} must be an integer.")
        return None
    if rule == "url":
        if value and not str(value).startswith(("http://", "https://")):
            return msg("url", f"The {attr} must be a valid URL.")
        return None
    if rule == "date":
        if value not in (None, "") and _parse_date(value) is None:
            return msg("date", f"The {attr} must be a valid date.")
        return None
    if rule == "confirmed":
        other = state.get(f"{path}_confirmation")
        if value not in (None, "") and value != other:
            return msg("confirmed", f"The {attr} confirmation does not match.")
        return None
    if rule.startswith("same:"):
        other_path = rule.split(":", 1)[1]
        if value not in (None, "") and value != state.get(other_path):
            return msg("same", f"The {attr} and {other_path} must match.", other=other_path)
        return None
    if rule.startswith("in:"):
        allowed = [p.strip() for p in rule.split(":", 1)[1].split(",") if p.strip()]
        if value not in (None, "") and str(value) not in allowed:
            return msg("in", f"The selected {attr} is invalid.")
        return None
    if rule.startswith("after:"):
        bound = _resolve_date_bound(rule.split(":", 1)[1], state)
        current = _parse_date(value)
        if current is not None and bound is not None and not (current > bound):
            return msg("after", f"The {attr} must be a date after {bound.isoformat()}.", date=bound.isoformat())
        return None
    if rule.startswith("before:"):
        bound = _resolve_date_bound(rule.split(":", 1)[1], state)
        current = _parse_date(value)
        if current is not None and bound is not None and not (current < bound):
            return msg("before", f"The {attr} must be a date before {bound.isoformat()}.", date=bound.isoformat())
        return None
    if rule.startswith("unique:"):
        table, column = _parse_table_column(rule)
        checker = ctx.get("unique") or Form._unique_checker
        if value not in (None, "") and checker is not None:
            try:
                ok = checker(value, table=table, column=column, **ctx)
            except TypeError:
                ok = evaluate(checker, value, table=table, column=column, **ctx)
            if ok is False:
                return msg("unique", f"The {attr} has already been taken.")
        return None
    if rule.startswith("exists:"):
        table, column = _parse_table_column(rule)
        checker = ctx.get("exists") or Form._exists_checker
        if value not in (None, "") and checker is not None:
            try:
                ok = checker(value, table=table, column=column, **ctx)
            except TypeError:
                ok = evaluate(checker, value, table=table, column=column, **ctx)
            if ok is False:
                return msg("exists", f"The selected {attr} is invalid.")
        return None
    if rule.startswith("max:"):
        n = int(rule.split(":", 1)[1])
        if value is not None and len(str(value)) > n:
            return msg("max", f"The {attr} must not be greater than {n} characters.", max=n)
        return None
    if rule.startswith("min:"):
        n = int(rule.split(":", 1)[1])
        if value is not None and len(str(value)) < n:
            return msg("min", f"The {attr} must be at least {n} characters.", min=n)
        return None
    return None


def _parse_table_column(rule: str) -> tuple[str, str | None]:
    body = rule.split(":", 1)[1]
    parts = [p.strip() for p in body.split(",")]
    table = parts[0] if parts else ""
    column = parts[1] if len(parts) > 1 else None
    return table, column


def _resolve_date_bound(spec: str, state: dict[str, Any]) -> date | None:
    parsed = _parse_date(spec)
    if parsed is not None and (len(spec) >= 8 and spec[0:4].isdigit()):
        return parsed
    if spec in state:
        return _parse_date(state.get(spec))
    return _parse_date(spec)


def _parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for candidate in (text[:10], text):
        try:
            return date.fromisoformat(candidate)
        except ValueError:
            continue
    return None


def _is_number(value: Any) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False
