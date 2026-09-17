"""Table column summarizers (Sum, Average, Count, Range).

Parent wiring (into ``table.py`` / ``columns.py`` — forms owns those files):
- ``Column.summarize(Summarizer | Sequence[Summarizer])`` stores summarizers on the column.
- ``Table.render`` (or a footer helper) calls ``summarizer.summarize(records, attribute=col.name)``
  for the current page and full filtered set, then ``summarizer.render(value)`` into ``<tfoot>``.
- Prefer ``Table.summaries(page=True, all=True)`` to toggle page vs all-table summary rows.
- With ``Group``, also render per-group summary rows via the same summarizers.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.evaluate import evaluate
from almasix.orbit.support.html import e


class Summarizer(Component):
    """Base summarizer — override ``calculate`` or supply ``.using(callback)``."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._using: Callable[..., Any] | None = None
        self._query_scope: Callable[..., Any] | None = None
        self._hidden_label = False
        self._numeric = False
        self._decimal_places: int | None = None
        self._money_currency: str | None = None
        self._money_divide_by: float | int = 1
        self._prefix: str = ""
        self._suffix: str = ""
        self._limit: int | None = None
        self._attribute: str | None = None

    def using(self, callback: Callable[..., Any]) -> Self:
        self._using = callback
        return self

    def query(self, callback: Callable[..., Any]) -> Self:
        """Scope the record set before calculating (Filament ``->query``)."""
        self._query_scope = callback
        return self

    def attribute(self, name: str) -> Self:
        self._attribute = name
        return self

    def get_attribute(self) -> str | None:
        return self._attribute or self.get_name()

    def hidden_label(self, condition: bool = True) -> Self:
        self._hidden_label = condition
        return self

    def is_label_hidden(self) -> bool:
        return self._hidden_label

    def numeric(self, decimal_places: int | None = None) -> Self:
        self._numeric = True
        self._decimal_places = decimal_places
        return self

    def money(self, currency: str = "USD", *, divide_by: float | int = 1, decimal_places: int = 2) -> Self:
        self._money_currency = currency
        self._money_divide_by = divide_by
        self._decimal_places = decimal_places
        self._numeric = True
        return self

    def prefix(self, text: str) -> Self:
        self._prefix = text
        return self

    def suffix(self, text: str) -> Self:
        self._suffix = text
        return self

    def limit(self, length: int) -> Self:
        self._limit = length
        return self

    def scope_records(self, records: Sequence[Any]) -> list[Any]:
        records_list = list(records)
        if self._query_scope is None:
            return records_list
        result = evaluate(self._query_scope, records_list, records=records_list)
        if result is None:
            return records_list
        if isinstance(result, list):
            return result
        try:
            return list(result)
        except TypeError:
            return records_list

    def _record_value(self, record: Any, attribute: str) -> Any:
        if isinstance(record, dict):
            return record.get(attribute)
        return getattr(record, attribute, None)

    def values(self, records: Sequence[Any], attribute: str | None = None) -> list[Any]:
        attr = attribute or self.get_attribute() or ""
        scoped = self.scope_records(records)
        return [self._record_value(r, attr) for r in scoped]

    def numeric_values(self, records: Sequence[Any], attribute: str | None = None) -> list[float]:
        out: list[float] = []
        for v in self.values(records, attribute):
            if v is None:
                continue
            try:
                out.append(float(v))
            except (TypeError, ValueError):
                continue
        return out

    def calculate(self, records: Sequence[Any], attribute: str | None = None) -> Any:
        """Default calculate — subclasses override; ``using`` wins when set."""
        return None

    def summarize(self, records: Sequence[Any], attribute: str | None = None) -> Any:
        attr = attribute or self.get_attribute()
        if self._using is not None:
            scoped = self.scope_records(records)
            return evaluate(
                self._using,
                scoped,
                records=scoped,
                attribute=attr,
                summarizer=self,
            )
        return self.calculate(records, attr)

    def format_value(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, tuple) and len(value) == 2:
            lo, hi = value
            if lo == hi:
                text = self._format_scalar(lo)
            else:
                text = f"{self._format_scalar(lo)} – {self._format_scalar(hi)}"
        else:
            text = self._format_scalar(value)
        if self._limit is not None and len(text) > self._limit:
            text = text[: self._limit] + "…"
        return f"{self._prefix}{text}{self._suffix}"

    def _format_scalar(self, value: Any) -> str:
        if value is None:
            return ""
        if self._money_currency is not None:
            try:
                num = float(value) / float(self._money_divide_by)
            except (TypeError, ValueError):
                return str(value)
            places = 2 if self._decimal_places is None else self._decimal_places
            return f"{self._money_currency} {num:.{places}f}"
        if self._numeric:
            try:
                num = float(value)
            except (TypeError, ValueError):
                return str(value)
            if self._decimal_places is not None:
                return f"{num:.{self._decimal_places}f}"
            if num == int(num):
                return str(int(num))
            return str(num)
        return str(value)

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        value = state
        if value is None and "records" in ctx:
            value = self.summarize(ctx["records"], ctx.get("attribute"))
        formatted = self.format_value(value)
        label = self.get_label(**ctx)
        label_html = ""
        if label and not self._hidden_label:
            label_html = f'<span class="or-summary-label">{e(label)}</span> '
        elif label and self._hidden_label:
            label_html = f'<span class="or-summary-label or-sr-only">{e(label)}</span>'
        return (
            f'<div class="or-summary or-summary-{e(type(self).__name__)}" '
            f'data-summarizer="{e(self.get_name() or type(self).__name__)}">'
            f'{label_html}<span class="or-summary-value">{e(formatted)}</span></div>'
        )

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "hidden_label": self._hidden_label,
                "numeric": self._numeric,
                "money_currency": self._money_currency,
                "has_using": self._using is not None,
            }
        )
        return d


class Sum(Summarizer):
    def calculate(self, records: Sequence[Any], attribute: str | None = None) -> float:
        vals = self.numeric_values(records, attribute)
        return float(sum(vals)) if vals else 0.0


class Average(Summarizer):
    def calculate(self, records: Sequence[Any], attribute: str | None = None) -> float | None:
        vals = self.numeric_values(records, attribute)
        if not vals:
            return None
        return float(sum(vals)) / len(vals)


class Count(Summarizer):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._icons = False

    def icons(self, condition: bool = True) -> Self:
        self._icons = condition
        return self

    def calculate(self, records: Sequence[Any], attribute: str | None = None) -> int:
        scoped = self.scope_records(records)
        attr = attribute or self.get_attribute()
        if not attr:
            return len(scoped)
        # Count non-null attribute values when an attribute is set
        return sum(1 for r in scoped if self._record_value(r, attr) is not None)

    def render(self, state: Any = None, **ctx: Any) -> str:
        if self._icons and "records" in ctx:
            attr = ctx.get("attribute") or self.get_attribute() or ""
            counts: dict[str, int] = {}
            for v in self.values(ctx["records"], attr):
                key = "" if v is None else str(v)
                counts[key] = counts.get(key, 0) + 1
            chips = "".join(
                f'<span class="or-summary-icon-count" data-icon="{e(k)}">{e(str(n))}</span>'
                for k, n in counts.items()
            )
            label = self.get_label(**ctx)
            label_html = (
                f'<span class="or-summary-label">{e(label)}</span> ' if label and not self._hidden_label else ""
            )
            return f'<div class="or-summary or-summary-Count or-summary-icons">{label_html}{chips}</div>'
        return super().render(state, **ctx)


class Range(Summarizer):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._exclude_null = True
        self._minimal_date = False
        self._minimal_text = False

    def exclude_null(self, condition: bool = True) -> Self:
        self._exclude_null = condition
        return self

    def minimal_date_time_difference(self, condition: bool = True) -> Self:
        self._minimal_date = condition
        return self

    def minimal_textual_difference(self, condition: bool = True) -> Self:
        self._minimal_text = condition
        return self

    def calculate(self, records: Sequence[Any], attribute: str | None = None) -> tuple[Any, Any] | None:
        vals = self.values(records, attribute)
        if self._exclude_null:
            vals = [v for v in vals if v is not None]
        if not vals:
            return None
        try:
            return (min(vals), max(vals))
        except TypeError:
            # Non-comparable mix — fall back to string order
            as_str = [str(v) for v in vals]
            return (min(as_str), max(as_str))

    def format_value(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, tuple) and len(value) == 2:
            lo, hi = value
            if self._minimal_text and isinstance(lo, str) and isinstance(hi, str):
                return self._minimal_textual(lo, hi)
            if self._minimal_date:
                return self._minimal_dates(str(lo), str(hi))
        return super().format_value(value)

    def _minimal_textual(self, lo: str, hi: str) -> str:
        if lo == hi:
            return lo
        i = 0
        while i < min(len(lo), len(hi)) and lo[i] == hi[i]:
            i += 1
        # Show enough of each side to reveal the first difference
        end = i + 1
        return f"{lo[:end]} – {hi[:end]}"

    def _minimal_dates(self, lo: str, hi: str) -> str:
        if lo == hi:
            return lo
        # If date portion (first 10 chars YYYY-MM-DD) differs, show dates only
        if len(lo) >= 10 and len(hi) >= 10 and lo[:10] != hi[:10]:
            return f"{lo[:10]} – {hi[:10]}"
        return f"{lo} – {hi}"
