
"""Query builder — Filament-style constraint UI model."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Self

from almasix.orbit.support.component import Component


class Operator(StrEnum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IS_SET = "is_set"
    IS_NOT_SET = "is_not_set"
    IN = "in"


class Constraint(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._operators: list[Operator] = [Operator.EQUALS, Operator.NOT_EQUALS]
        self._attribute: str | None = name

    def operators(self, *ops: Operator) -> Self:
        self._operators = list(ops)
        return self

    def attribute(self, name: str) -> Self:
        self._attribute = name
        return self

    def get_attribute(self) -> str:
        return self._attribute or self.get_name() or ""

    def apply(self, records: list[Any], operator: Operator, value: Any) -> list[Any]:
        attr = self.get_attribute()

        def val(r: Any) -> Any:
            return r.get(attr) if isinstance(r, dict) else getattr(r, attr, None)

        out = []
        for r in records:
            v = val(r)
            if operator == Operator.EQUALS and v == value:
                out.append(r)
            elif operator == Operator.NOT_EQUALS and v != value:
                out.append(r)
            elif operator == Operator.CONTAINS and value is not None and str(value).lower() in str(v or "").lower():
                out.append(r)
            elif operator == Operator.STARTS_WITH and str(v or "").lower().startswith(str(value).lower()):
                out.append(r)
            elif operator == Operator.ENDS_WITH and str(v or "").lower().endswith(str(value).lower()):
                out.append(r)
            elif operator == Operator.GREATER_THAN and v is not None and value is not None and v > value:
                out.append(r)
            elif operator == Operator.LESS_THAN and v is not None and value is not None and v < value:
                out.append(r)
            elif operator == Operator.IS_SET and v not in (None, ""):
                out.append(r)
            elif operator == Operator.IS_NOT_SET and v in (None, ""):
                out.append(r)
            elif operator == Operator.IN and v in (value or []):
                out.append(r)
        return out


class TextConstraint(Constraint):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._operators = [
            Operator.EQUALS,
            Operator.NOT_EQUALS,
            Operator.CONTAINS,
            Operator.STARTS_WITH,
            Operator.ENDS_WITH,
            Operator.IS_SET,
            Operator.IS_NOT_SET,
        ]


class SelectConstraint(Constraint):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._options: dict[Any, Any] = {}
        self._operators = [Operator.EQUALS, Operator.NOT_EQUALS, Operator.IN]

    def options(self, options: dict[Any, Any]) -> Self:
        self._options = dict(options)
        return self


class BooleanConstraint(Constraint):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._operators = [Operator.EQUALS]


class DateConstraint(Constraint):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._operators = [
            Operator.EQUALS,
            Operator.GREATER_THAN,
            Operator.LESS_THAN,
            Operator.IS_SET,
            Operator.IS_NOT_SET,
        ]


class NumberConstraint(Constraint):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._operators = [
            Operator.EQUALS,
            Operator.NOT_EQUALS,
            Operator.GREATER_THAN,
            Operator.LESS_THAN,
        ]


class QueryBuilder(Component):
    def __init__(self, name: str | None = "query_builder") -> None:
        super().__init__(name)
        self._constraints: list[Constraint] = []
        self._rules: list[dict[str, Any]] = []

    def constraints(self, constraints: list[Constraint]) -> Self:
        self._constraints = list(constraints)
        return self

    def rules(self, rules: list[dict[str, Any]]) -> Self:
        self._rules = list(rules)
        return self

    def get_constraints(self) -> list[Constraint]:
        return list(self._constraints)

    def apply(self, records: list[Any]) -> list[Any]:
        result = list(records)
        by_name = {c.get_name(): c for c in self._constraints}
        for rule in self._rules:
            constraint = by_name.get(rule.get("constraint"))
            if constraint is None:
                continue
            op = Operator(rule.get("operator", Operator.EQUALS.value))
            result = constraint.apply(result, op, rule.get("value"))
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "constraints": [c.to_dict() for c in self._constraints],
            "rules": self._rules,
        }

    def render(self, state: Any = None, **ctx: Any) -> str:
        from almasix.orbit.support.html import e

        if not self.is_visible(**ctx):
            return ""
        rows: list[str] = []
        for constraint in self._constraints:
            name = e(constraint.get_name() or "")
            label = e(constraint.get_label(**ctx))
            ops = "".join(
                f'<option value="{e(op.value)}">{e(op.value.replace("_", " "))}</option>'
                for op in constraint._operators
            )
            value_input = (
                f'<input class="or-input" name="{name}_value" placeholder="Value" '
                f'wire:model="query.{name}.value" />'
            )
            if hasattr(constraint, "_options") and constraint._options:  # type: ignore[attr-defined]
                opts = "".join(
                    f'<option value="{e(k)}">{e(v)}</option>'
                    for k, v in constraint._options.items()  # type: ignore[attr-defined]
                )
                value_input = (
                    f'<select class="or-select" name="{name}_value" '
                    f'wire:model="query.{name}.value">{opts}</select>'
                )
            rows.append(
                f'<div class="or-qb-row" data-constraint="{name}">'
                f'<span class="or-qb-label">{label}</span>'
                f'<select class="or-select or-qb-operator" name="{name}_operator" '
                f'wire:model="query.{name}.operator">{ops}</select>'
                f"{value_input}</div>"
            )
        return (
            f'<div class="or-field or-query-builder" data-field="{e(self.get_name() or "query")}">'
            f'<div class="or-qb-rows">{"".join(rows)}</div></div>'
        )
