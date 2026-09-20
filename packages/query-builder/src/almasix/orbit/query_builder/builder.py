
"""Query builder — constraint UI and in-memory apply for Orbit lists."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Self

from almasix.orbit.support.component import Component

_PRESENCE_OPERATORS = {"is_set", "is_not_set"}


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

    def get_operators(self) -> list[Operator]:
        return list(self._operators)

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

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["operators"] = [op.value for op in self._operators]
        data["attribute"] = self.get_attribute()
        return data


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

    def get_options(self) -> dict[Any, Any]:
        return dict(self._options)

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["options"] = dict(self._options)
        return data


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
        self._logic: str = "and"

    def constraints(self, constraints: list[Constraint]) -> Self:
        self._constraints = list(constraints)
        return self

    def rules(self, rules: list[dict[str, Any]]) -> Self:
        self._rules = list(rules)
        return self

    def add_rule(self, constraint: str, operator: str | Operator, value: Any = None) -> Self:
        """Append one rule without replacing the rest."""
        op = operator.value if isinstance(operator, Operator) else str(operator)
        self._rules.append({"constraint": constraint, "operator": op, "value": value})
        return self

    def clear_rules(self) -> Self:
        self._rules = []
        return self

    def get_rules(self) -> list[dict[str, Any]]:
        return list(self._rules)

    def logic(self, value: str) -> Self:
        """Combine rules with ``and`` (default) or ``or``."""
        self._logic = "or" if str(value).lower() == "or" else "and"
        return self

    def get_logic(self) -> str:
        return self._logic

    def get_constraints(self) -> list[Constraint]:
        return list(self._constraints)

    def apply(self, records: list[Any]) -> list[Any]:
        if not self._rules:
            return list(records)
        by_name = {c.get_name(): c for c in self._constraints}
        if self._logic == "or":
            matched: list[Any] = []
            seen: set[int] = set()
            for rule in self._rules:
                constraint = by_name.get(rule.get("constraint"))
                if constraint is None:
                    continue
                op = Operator(rule.get("operator", Operator.EQUALS.value))
                for record in constraint.apply(list(records), op, rule.get("value")):
                    marker = id(record)
                    if marker in seen:
                        continue
                    seen.add(marker)
                    matched.append(record)
            return matched
        result = list(records)
        for rule in self._rules:
            constraint = by_name.get(rule.get("constraint"))
            if constraint is None:
                continue
            op = Operator(rule.get("operator", Operator.EQUALS.value))
            result = constraint.apply(result, op, rule.get("value"))
        return result

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data.update(
            {
                "constraints": [c.to_dict() for c in self._constraints],
                "rules": self._rules,
                "logic": self._logic,
            }
        )
        return data

    def _hydrate_from_state(self, state: Any) -> None:
        if isinstance(state, dict):
            if state.get("logic"):
                self.logic(str(state["logic"]))
            rules = state.get("rules")
            if isinstance(rules, list):
                self.rules(rules)
        elif isinstance(state, list):
            self.rules(state)

    def _rule_for(self, name: str) -> dict[str, Any]:
        for rule in self._rules:
            if rule.get("constraint") == name:
                return rule
        return {}

    def _value_input(self, constraint: Constraint, name: str, rule: dict[str, Any]) -> str:
        from almasix.orbit.support.html import e

        operator = str(rule.get("operator") or "")
        if operator in _PRESENCE_OPERATORS:
            return ""
        raw = rule.get("value")
        value = "" if raw in (None, False) else str(raw)
        if isinstance(constraint, BooleanConstraint):
            checked = " checked" if raw in (True, "true", "1", 1) else ""
            return (
                f'<input class="or-checkbox" type="checkbox" name="{name}_value" '
                f'wire:model="query.{name}.value"{checked} />'
            )
        if isinstance(constraint, DateConstraint):
            return (
                f'<input class="or-input" type="date" name="{name}_value" value="{e(value)}" '
                f'wire:model="query.{name}.value" />'
            )
        if isinstance(constraint, NumberConstraint):
            return (
                f'<input class="or-input" type="number" name="{name}_value" value="{e(value)}" '
                f'wire:model="query.{name}.value" />'
            )
        options = getattr(constraint, "_options", None)
        if options:
            opts = "".join(
                f'<option value="{e(k)}"'
                f'{" selected" if str(k) == value else ""}>{e(v)}</option>'
                for k, v in options.items()
            )
            return (
                f'<select class="or-select" name="{name}_value" '
                f'wire:model="query.{name}.value">{opts}</select>'
            )
        return (
            f'<input class="or-input" name="{name}_value" placeholder="Value" value="{e(value)}" '
            f'wire:model="query.{name}.value" />'
        )

    def render(self, state: Any = None, **ctx: Any) -> str:
        from almasix.orbit.support.html import e

        if not self.is_visible(**ctx):
            return ""
        self._hydrate_from_state(state)
        field = e(self.get_name() or "query")
        and_sel = " selected" if self._logic != "or" else ""
        or_sel = " selected" if self._logic == "or" else ""
        logic_html = (
            f'<div class="or-qb-logic">'
            f'<span class="or-qb-logic-label">Match</span>'
            f'<select class="or-select or-qb-logic-select" name="{field}_logic" '
            f'wire:model="query.logic">'
            f'<option value="and"{and_sel}>all rules</option>'
            f'<option value="or"{or_sel}>any rule</option>'
            f"</select></div>"
        )
        rows: list[str] = []
        for constraint in self._constraints:
            name = e(constraint.get_name() or "")
            label = e(constraint.get_label(**ctx))
            rule = self._rule_for(constraint.get_name() or "")
            current_op = str(
                rule.get("operator")
                or (constraint._operators[0].value if constraint._operators else Operator.EQUALS.value)
            )
            ops = "".join(
                f'<option value="{e(op.value)}"'
                f'{" selected" if op.value == current_op else ""}>'
                f"{e(op.value.replace('_', ' '))}</option>"
                for op in constraint._operators
            )
            value_input = self._value_input(constraint, name, {**rule, "operator": current_op})
            rows.append(
                f'<div class="or-qb-row" data-constraint="{name}">'
                f'<span class="or-qb-label">{label}</span>'
                f'<select class="or-select or-qb-operator" name="{name}_operator" '
                f'wire:model="query.{name}.operator">{ops}</select>'
                f"{value_input}</div>"
            )
        logic = f' data-logic="{e(self._logic)}"'
        return (
            f'<div class="or-field or-query-builder" data-field="{field}"{logic}>'
            f"{logic_html}"
            f'<div class="or-qb-rows">{"".join(rows)}</div></div>'
        )
