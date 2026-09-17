"""Panel clusters — grouped resource namespaces with sub-navigation."""

from __future__ import annotations

from typing import Any, ClassVar, Literal, Self

from almasix.orbit.support.component import Component

SubNavPosition = Literal["start", "end", "top"]


class Cluster(Component):
    """Filament-style cluster: prefixes URLs and owns sub-navigation."""

    navigation_icon: ClassVar[str | None] = None
    navigation_label: ClassVar[str | None] = None
    navigation_group: ClassVar[str | None] = None
    navigation_sort: ClassVar[int] = 0
    slug: ClassVar[str | None] = None
    sub_navigation_position: ClassVar[SubNavPosition] = "start"

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._resources: list[type[Any]] = []
        self._pages: list[type[Any]] = []
        self._breadcrumb: str | None = None

    @classmethod
    def get_slug(cls) -> str:
        if cls.slug:
            return cls.slug
        name = cls.__name__
        if name.endswith("Cluster"):
            name = name[: -len("Cluster")]
        return "".join(
            ("_" + c.lower() if c.isupper() and i else c.lower()) for i, c in enumerate(name)
        ).lstrip("_")

    @classmethod
    def get_navigation_label(cls) -> str:
        return cls.navigation_label or cls.get_slug().replace("_", " ").title()

    def resources(self, resources: list[type[Any]]) -> Self:
        self._resources = list(resources)
        return self

    def pages(self, pages: list[type[Any]]) -> Self:
        self._pages = list(pages)
        return self

    def breadcrumb(self, text: str) -> Self:
        self._breadcrumb = text
        return self

    def get_breadcrumb(self) -> str:
        return self._breadcrumb or self.get_navigation_label()

    def get_resources(self) -> list[type[Any]]:
        return list(self._resources)

    def get_pages(self) -> list[type[Any]]:
        return list(self._pages)

    def path_prefix(self) -> str:
        return f"/{self.get_slug()}"
