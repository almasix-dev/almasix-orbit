"""Prime schema components — Text, Icon, Image, UnorderedList."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Literal, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.evaluate import evaluate
from almasix.orbit.support.html import e
from almasix.orbit.support.icons import icon as render_icon

Size = Literal["xs", "sm", "md", "lg", "xl"]
Weight = Literal["light", "normal", "medium", "semibold", "bold"]


class Text(Component):
    """Inline or block text prime (optionally markdown/html/badge)."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._content: str | Callable[..., str] | None = None
        self._markdown = False
        self._html = False
        self._badge = False
        self._color: str | Callable[..., str] | None = None
        self._size: Size = "md"
        self._weight: Weight = "normal"
        self._tooltip: str | None = None
        self._icon: str | None = None

    def content(self, value: str | Callable[..., str]) -> Self:
        self._content = value
        return self

    def markdown(self, condition: bool = True) -> Self:
        self._markdown = condition
        return self

    def html(self, condition: bool = True) -> Self:
        self._html = condition
        return self

    def badge(self, condition: bool = True) -> Self:
        self._badge = condition
        return self

    def color(self, value: str | Callable[..., str]) -> Self:
        self._color = value
        return self

    def size(self, value: Size) -> Self:
        self._size = value
        return self

    def weight(self, value: Weight) -> Self:
        self._weight = value
        return self

    def tooltip(self, value: str) -> Self:
        self._tooltip = value
        return self

    def icon(self, name: str) -> Self:
        self._icon = name
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        if self._content is not None:
            raw = evaluate(self._content, state=state, **ctx)
        else:
            raw = "" if state is None else str(state)
        if self._html:
            body = str(raw)
        elif self._markdown:
            body = e(str(raw)).replace("**", "<strong>", 1).replace("**", "</strong>", 1)
            body = body.replace("*", "<em>", 1).replace("*", "</em>", 1)
            body = body.replace("`", "<code>", 1).replace("`", "</code>", 1)
        else:
            body = e(str(raw))
        color = evaluate(self._color, **ctx) if self._color else None
        color_cls = f" or-color-{e(color)}" if color else ""
        badge_cls = " or-badge" if self._badge else ""
        tip = f' title="{e(self._tooltip)}"' if self._tooltip else ""
        ic = render_icon(self._icon) if self._icon else ""
        return (
            f'<span class="or-prime or-prime-text or-size-{self._size} or-weight-{self._weight}'
            f'{badge_cls}{color_cls}"{tip}>{ic}{body}</span>'
        )


class Icon(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._icon: str | Callable[..., str] = name or "heroicon-o-check"
        self._color: str | None = None
        self._size: Size = "md"
        self._tooltip: str | None = None

    def icon(self, name: str | Callable[..., str]) -> Self:
        self._icon = name
        return self

    def color(self, value: str) -> Self:
        self._color = value
        return self

    def size(self, value: Size) -> Self:
        self._size = value
        return self

    def tooltip(self, value: str) -> Self:
        self._tooltip = value
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = str(evaluate(self._icon, state=state, **ctx) or "heroicon-o-check")
        color_cls = f" or-color-{e(self._color)}" if self._color else ""
        tip = f' title="{e(self._tooltip)}"' if self._tooltip else ""
        return (
            f'<span class="or-prime or-prime-icon or-size-{self._size}{color_cls}"{tip}>'
            f"{render_icon(name)}</span>"
        )


class Image(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._src: str | Callable[..., str] | None = None
        self._width: str | int | None = None
        self._height: str | int | None = None
        self._image_size: str | int | None = None
        self._alignment: Literal["start", "center", "end"] = "start"
        self._tooltip: str | None = None

    def src(self, value: str | Callable[..., str]) -> Self:
        self._src = value
        return self

    def width(self, value: str | int) -> Self:
        self._width = value
        return self

    def height(self, value: str | int) -> Self:
        self._height = value
        return self

    def image_size(self, value: str | int) -> Self:
        self._image_size = value
        return self

    def alignment(self, value: Literal["start", "center", "end"]) -> Self:
        self._alignment = value
        return self

    def tooltip(self, value: str) -> Self:
        self._tooltip = value
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        url = evaluate(self._src, state=state, **ctx) if self._src is not None else state
        if not url:
            return ""
        w = self._image_size or self._width
        h = self._image_size or self._height
        style_parts = []
        if w is not None:
            style_parts.append(f"width:{w}px" if isinstance(w, int) else f"width:{w}")
        if h is not None:
            style_parts.append(f"height:{h}px" if isinstance(h, int) else f"height:{h}")
        style = f' style="{";".join(style_parts)}"' if style_parts else ""
        tip = f' title="{e(self._tooltip)}"' if self._tooltip else ""
        return (
            f'<div class="or-prime or-prime-image or-align-{self._alignment}">'
            f'<img src="{e(url)}" alt="" class="or-prime-img"{style}{tip} /></div>'
        )


class UnorderedList(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._items: Sequence[str | Component] | Callable[..., Sequence[Any]] = []
        self._bullet_size: Size = "md"

    def items(self, value: Sequence[str | Component] | Callable[..., Sequence[Any]]) -> Self:
        self._items = value
        return self

    def bullet_size(self, value: Size) -> Self:
        self._bullet_size = value
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        raw = evaluate(self._items, state=state, **ctx)
        lis = []
        for item in raw or []:
            if isinstance(item, Component):
                lis.append(f"<li>{item.render(state, **ctx)}</li>")
            else:
                lis.append(f"<li>{e(item)}</li>")
        return (
            f'<ul class="or-prime or-prime-list or-bullet-{self._bullet_size}">'
            f"{''.join(lis)}</ul>"
        )
