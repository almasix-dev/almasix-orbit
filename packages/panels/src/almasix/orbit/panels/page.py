"""Custom panel pages."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit.support.html import e


class Page:
    navigation_icon: ClassVar[str] = "heroicon-o-home"
    navigation_label: ClassVar[str | None] = None
    navigation_group: ClassVar[str | None] = None
    navigation_subgroup: ClassVar[str | None] = None
    navigation_sort: ClassVar[int] = 0
    slug: ClassVar[str | None] = None
    title: ClassVar[str | None] = None
    permission: ClassVar[str | None] = None

    @classmethod
    def get_slug(cls) -> str:
        if cls.slug:
            return cls.slug
        name = cls.__name__
        if name.endswith("Page"):
            name = name[: -len("Page")]
        return "".join(
            ("_" + c.lower() if c.isupper() and i else c.lower()) for i, c in enumerate(name)
        ).lstrip("_")

    @classmethod
    def get_navigation_label(cls) -> str:
        return cls.navigation_label or (cls.title or cls.get_slug().replace("_", " ").title())

    @classmethod
    def get_title(cls) -> str:
        return cls.title or cls.get_navigation_label()

    @classmethod
    def can_access(cls, user: Any) -> bool:
        if cls.permission is None:
            return user is not None
        from almasix.orbit.panels.resource import _can

        return _can(user, cls.permission)

    @classmethod
    def render(cls, **ctx: Any) -> str:
        return f'<div class="or-page"><h1 class="or-page-title">{e(cls.get_title())}</h1></div>'
