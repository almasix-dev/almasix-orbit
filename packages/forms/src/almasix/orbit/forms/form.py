"""Form builder wrapping Schema."""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from datetime import date, datetime
from typing import Any, Self

from almasix.orbit.forms.walk import iter_fields
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
        self._operation: str | None = None

    def schema(self, components: Sequence[Component]) -> Self:  # type: ignore[override]
        return self.components(components)

    def readonly(self, condition: bool = True) -> Self:
        self._readonly = condition
        return self

    def is_readonly(self) -> bool:
        return self._readonly

    def operation(self, value: str) -> Self:
        """Set create / edit / view context for dependent field visibility."""
        self._operation = value
        return self

    def get_operation(self) -> str | None:
        return self._operation

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
        """Return field → error messages using rule strings and/or callables.

        Walks nested layouts (Section / Grid / Tabs / Wizard / Repeater schemas).
        """
        state = data if data is not None else self.get_state()
        errors: dict[str, list[str]] = {}
        field_ctx_base = {
            **ctx,
            "state": state,
            "operation": ctx.get("operation", self._operation),
            "unique": ctx.get("unique", Form._unique_checker),
            "exists": ctx.get("exists", Form._exists_checker),
        }
        for c in iter_fields(self.get_components()):
            if not c.is_visible(**field_ctx_base):
                continue
            path = c.get_state_path() or ""
            if not path:
                continue
            value = _get_path(state, path)
            attr = c.get_validation_attribute(**field_ctx_base) or path
            field_ctx = {
                **field_ctx_base,
                "value": value,
                "field": c,
                "attribute": attr,
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
                            c.format_validation_message(
                                "default", attr, f"The {attr} field is invalid."
                            )
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


def _get_path(state: dict[str, Any], path: str) -> Any:
    if path in state:
        return state[path]
    current: Any = state
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


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

    # Empty values skip most rules except required / accepted / filled
    empty = value is None or value == "" or value == [] or value == {}

    if rule == "required":
        if empty:
            return msg("required", f"The {attr} field is required.")
        return None
    if rule == "nullable":
        return None
    if rule == "filled":
        if empty:
            return msg("filled", f"The {attr} field must have a value.")
        return None
    if rule == "accepted":
        if str(value).lower() not in {"1", "true", "yes", "on"}:
            return msg("accepted", f"The {attr} must be accepted.")
        return None
    if rule == "boolean":
        if value not in (None, "") and str(value).lower() not in {
            "1",
            "0",
            "true",
            "false",
            "yes",
            "no",
            "on",
            "off",
        }:
            return msg("boolean", f"The {attr} must be true or false.")
        return None
    if rule == "array":
        if value not in (None, "") and not isinstance(value, (list, tuple, dict)):
            return msg("array", f"The {attr} must be an array.")
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
    if rule == "json":
        if value not in (None, ""):
            import json

            try:
                if isinstance(value, (dict, list)):
                    return None
                json.loads(str(value))
            except (TypeError, ValueError):
                return msg("json", f"The {attr} must be valid JSON.")
        return None
    if rule == "uuid":
        if value not in (None, "") and not re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            str(value),
        ):
            return msg("uuid", f"The {attr} must be a valid UUID.")
        return None
    if rule == "ip":
        if value not in (None, ""):
            text = str(value)
            v4 = re.fullmatch(r"(\d{1,3}\.){3}\d{1,3}", text)
            v6 = ":" in text and re.fullmatch(r"[0-9a-fA-F:]+", text) and text.count(":") >= 2
            if not v4 and not v6:
                return msg("ip", f"The {attr} must be a valid IP address.")
        return None
    if rule == "alpha":
        if value and not str(value).isalpha():
            return msg("alpha", f"The {attr} must only contain letters.")
        return None
    if rule == "alpha_num":
        if value and not str(value).isalnum():
            return msg("alpha_num", f"The {attr} must only contain letters and numbers.")
        return None
    if rule == "alpha_dash":
        if value and not re.fullmatch(r"[A-Za-z0-9_-]+", str(value)):
            return msg("alpha_dash", f"The {attr} must only contain letters, numbers, dashes and underscores.")
        return None
    if rule == "confirmed":
        other = state.get(f"{path}_confirmation")
        if value not in (None, "") and value != other:
            return msg("confirmed", f"The {attr} confirmation does not match.")
        return None
    if rule.startswith("same:"):
        other_path = rule.split(":", 1)[1]
        if value not in (None, "") and value != _get_path(state, other_path):
            return msg("same", f"The {attr} and {other_path} must match.", other=other_path)
        return None
    if rule.startswith("different:"):
        other_path = rule.split(":", 1)[1]
        if value not in (None, "") and value == _get_path(state, other_path):
            return msg("different", f"The {attr} and {other_path} must be different.", other=other_path)
        return None
    if rule.startswith("in:"):
        allowed = [p.strip() for p in rule.split(":", 1)[1].split(",") if p.strip()]
        if value not in (None, "") and str(value) not in allowed:
            return msg("in", f"The selected {attr} is invalid.")
        return None
    if rule.startswith("not_in:"):
        blocked = [p.strip() for p in rule.split(":", 1)[1].split(",") if p.strip()]
        if value not in (None, "") and str(value) in blocked:
            return msg("not_in", f"The selected {attr} is invalid.")
        return None
    if rule.startswith("regex:"):
        pattern = rule.split(":", 1)[1]
        if value not in (None, "") and not re.search(pattern, str(value)):
            return msg("regex", f"The {attr} format is invalid.")
        return None
    if rule.startswith("starts_with:"):
        prefixes = [p.strip() for p in rule.split(":", 1)[1].split(",") if p.strip()]
        if value not in (None, "") and not any(str(value).startswith(p) for p in prefixes):
            return msg("starts_with", f"The {attr} must start with one of: {', '.join(prefixes)}.")
        return None
    if rule.startswith("ends_with:"):
        suffixes = [p.strip() for p in rule.split(":", 1)[1].split(",") if p.strip()]
        if value not in (None, "") and not any(str(value).endswith(s) for s in suffixes):
            return msg("ends_with", f"The {attr} must end with one of: {', '.join(suffixes)}.")
        return None
    if rule.startswith("digits:"):
        n = int(rule.split(":", 1)[1])
        if value not in (None, "") and not (str(value).isdigit() and len(str(value)) == n):
            return msg("digits", f"The {attr} must be {n} digits.", digits=n)
        return None
    if rule.startswith("between:"):
        lo_s, hi_s = rule.split(":", 1)[1].split(",", 1)
        lo, hi = float(lo_s), float(hi_s)
        if value not in (None, ""):
            if _is_number(value):
                num = float(value)
                if not (lo <= num <= hi):
                    return msg("between", f"The {attr} must be between {lo} and {hi}.", min=lo, max=hi)
            elif not (lo <= len(str(value)) <= hi):
                return msg("between", f"The {attr} must be between {lo} and {hi} characters.", min=lo, max=hi)
        return None
    if rule.startswith("gt:"):
        return _compare_numeric(rule, value, attr, field, state, op="gt", msg=msg)
    if rule.startswith("gte:"):
        return _compare_numeric(rule, value, attr, field, state, op="gte", msg=msg)
    if rule.startswith("lt:"):
        return _compare_numeric(rule, value, attr, field, state, op="lt", msg=msg)
    if rule.startswith("lte:"):
        return _compare_numeric(rule, value, attr, field, state, op="lte", msg=msg)
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
        table, column, ignore = _parse_unique_rule(rule)
        checker = ctx.get("unique") or Form._unique_checker
        if value not in (None, "") and checker is not None:
            try:
                ok = checker(value, table=table, column=column, ignore=ignore, **ctx)
            except TypeError:
                ok = evaluate(checker, value, table=table, column=column, ignore=ignore, **ctx)
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
    if rule.startswith("mimes:"):
        allowed = [p.strip().lower() for p in rule.split(":", 1)[1].split(",") if p.strip()]
        if value not in (None, ""):
            name = str(value).rsplit(".", 1)[-1].lower() if "." in str(value) else str(value).lower()
            if name not in allowed:
                return msg("mimes", f"The {attr} must be a file of type: {', '.join(allowed)}.")
        return None
    if rule.startswith("max:"):
        n = int(rule.split(":", 1)[1])
        if value is not None:
            if isinstance(value, (list, tuple, dict)):
                if len(value) > n:
                    return msg("max", f"The {attr} must not have more than {n} items.", max=n)
            elif _is_number(value) and not isinstance(value, bool) and type(value) is not str:
                if float(value) > n:
                    return msg("max", f"The {attr} must not be greater than {n}.", max=n)
            elif len(str(value)) > n:
                return msg("max", f"The {attr} must not be greater than {n} characters.", max=n)
        return None
    if rule.startswith("min:"):
        n = int(rule.split(":", 1)[1])
        if value is not None and value != "":
            if isinstance(value, (list, tuple, dict)):
                if len(value) < n:
                    return msg("min", f"The {attr} must have at least {n} items.", min=n)
            elif _is_number(value) and not isinstance(value, bool) and type(value) is not str:
                if float(value) < n:
                    return msg("min", f"The {attr} must be at least {n}.", min=n)
            elif len(str(value)) < n:
                return msg("min", f"The {attr} must be at least {n} characters.", min=n)
        return None
    if rule == "distinct":
        # Host should pass sibling values via ctx["siblings"]; otherwise no-op.
        siblings = ctx.get("siblings")
        if isinstance(siblings, (list, tuple)) and value not in (None, ""):
            if list(siblings).count(value) > 1:
                return msg("distinct", f"The {attr} field has a duplicate value.")
        return None
    return None


def _compare_numeric(
    rule: str,
    value: Any,
    attr: str,
    field: Any,
    state: dict[str, Any],
    *,
    op: str,
    msg: Callable[..., str],
) -> str | None:
    if value in (None, "") or not _is_number(value):
        return None
    spec = rule.split(":", 1)[1]
    other = state.get(spec, spec)
    if not _is_number(other):
        return None
    left, right = float(value), float(other)
    ok = {
        "gt": left > right,
        "gte": left >= right,
        "lt": left < right,
        "lte": left <= right,
    }[op]
    if not ok:
        words = {"gt": "greater than", "gte": "greater than or equal to", "lt": "less than", "lte": "less than or equal to"}
        return msg(op, f"The {attr} must be {words[op]} {right}.", value=right)
    return None


def _parse_unique_rule(rule: str) -> tuple[str, str | None, Any]:
    """Parse ``unique:table,column,ignore``."""
    body = rule.split(":", 1)[1]
    parts = [p.strip() for p in body.split(",")]
    table = parts[0] if parts else ""
    column = parts[1] if len(parts) > 1 else None
    ignore = parts[2] if len(parts) > 2 else None
    return table, column, ignore


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
