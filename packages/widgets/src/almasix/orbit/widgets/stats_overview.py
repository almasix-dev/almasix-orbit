"""Stats overview widget."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Self

from almasix.orbit.support.evaluate import evaluate
from almasix.orbit.widgets.stat import Stat
from almasix.orbit.widgets.widget import Widget

StatLike = Stat | Callable[..., Stat | Sequence[Stat]]


class StatsOverviewWidget(Widget):
    """Row of :class:`~almasix.orbit.widgets.stat.Stat` cards."""

    def __init__(self, name: str | None = "stats") -> None:
        super().__init__(name)
        self._stats: list[StatLike] = []

    def stats(self, stats: Sequence[StatLike]) -> Self:
        self._stats = list(stats)
        return self

    def get_stats(self, **ctx: Any) -> list[Stat]:
        out: list[Stat] = []
        for item in self._stats:
            if callable(item) and not isinstance(item, Stat):
                result = evaluate(item, **ctx)
                if isinstance(result, Stat):
                    out.append(result)
                elif isinstance(result, Sequence):
                    out.extend(s for s in result if isinstance(s, Stat))
            elif isinstance(item, Stat):
                out.append(item)
        return out

    def render_body(self, state: Any = None, **ctx: Any) -> str:
        cards = [s.render(state, **ctx) for s in self.get_stats(**ctx)]
        return f'<div class="or-stats">{"".join(cards)}</div>'
