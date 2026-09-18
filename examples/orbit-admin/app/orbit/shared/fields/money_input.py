"""Custom money field example."""

from __future__ import annotations

from typing import Any

from almasix.orbit.forms import Field
from almasix.orbit.support.html import e


class MoneyInput(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._currency = "USD"

    def currency(self, code: str) -> MoneyInput:
        self._currency = code
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        name = e(self.get_state_path() or self.get_name() or "")
        value = "" if state is None else e(state)
        binding = self._wire_binding(name)
        control = (
            f'<div class="or-input-affix">'
            f'<span class="or-input-prefix"><span class="or-affix-text">{e(self._currency)}</span></span>'
            f'<input class="or-input" id="or-{name}" name="{name}" value="{value}"{binding} />'
            f"</div>"
        )
        return self.wrap_field(name, control, **ctx)
