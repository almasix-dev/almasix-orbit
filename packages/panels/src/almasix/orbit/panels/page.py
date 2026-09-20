"""Custom panel pages."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit.support.html import e


class Page:
    navigation_icon: ClassVar[str] = "heroicon-o-home"
    active_navigation_icon: ClassVar[str | None] = None
    navigation_label: ClassVar[str | None] = None
    navigation_group: ClassVar[str | None] = None
    navigation_subgroup: ClassVar[str | None] = None
    #: Alias for :attr:`navigation_subgroup` (second-level nav category).
    navigation_sub_category: ClassVar[str | None] = None
    navigation_sort: ClassVar[int] = 0
    navigation_badge: ClassVar[Any] = None
    navigation_badge_color: ClassVar[Any] = None
    navigation_badge_tooltip: ClassVar[Any] = None
    navigation_parent_item: ClassVar[str | None] = None
    should_register_navigation: ClassVar[bool] = True
    cluster: ClassVar[type[Any] | str | None] = None
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
    def get_should_register_navigation(cls, **ctx: Any) -> bool:
        from almasix.orbit.panels.resource import _resolve_nav_flag

        return _resolve_nav_flag(cls, "should_register_navigation", default=True, **ctx)

    @classmethod
    def get_navigation_badge(cls, **ctx: Any) -> str | None:
        from almasix.orbit.panels.resource import _resolve_nav_str

        return _resolve_nav_str(cls, "navigation_badge", **ctx)

    @classmethod
    def get_navigation_badge_color(cls, **ctx: Any) -> str | None:
        from almasix.orbit.panels.resource import _resolve_nav_str

        return _resolve_nav_str(cls, "navigation_badge_color", **ctx)

    @classmethod
    def get_navigation_badge_tooltip(cls, **ctx: Any) -> str | None:
        from almasix.orbit.panels.resource import _resolve_nav_str

        return _resolve_nav_str(cls, "navigation_badge_tooltip", **ctx)

    @classmethod
    def get_navigation_parent_item(cls) -> str | None:
        return cls.navigation_parent_item

    @classmethod
    def get_cluster(cls) -> type[Any] | str | None:
        return cls.cluster

    @classmethod
    def get_url_path_prefix(cls) -> str:
        """Panel path + optional tenant + cluster slug prefix (no trailing slash)."""
        panel_path = str(getattr(cls, "_panel_path", "") or "").rstrip("/")
        tenant_path = str(getattr(cls, "_tenant_path", "") or "").strip("/")
        cluster = cls.get_cluster()
        cluster_prefix = ""
        if cluster is not None:
            if isinstance(cluster, str):
                slug = cluster.strip().strip("/")
                cluster_prefix = f"/{slug}" if slug else ""
            else:
                path_fn = getattr(cluster, "path_prefix", None)
                if callable(path_fn):
                    cluster_prefix = str(path_fn()).rstrip("/") or ""
                    if cluster_prefix and not cluster_prefix.startswith("/"):
                        cluster_prefix = f"/{cluster_prefix}"
                else:
                    slug_fn = getattr(cluster, "get_slug", None)
                    slug = slug_fn() if callable(slug_fn) else ""
                    cluster_prefix = f"/{slug}" if slug else ""
        parts: list[str] = []
        if panel_path and panel_path != "/":
            parts.append(panel_path.lstrip("/"))
        if tenant_path:
            parts.append(tenant_path)
        if cluster_prefix:
            parts.append(cluster_prefix.strip("/"))
        if not parts:
            return panel_path if panel_path == "/" else ""
        return "/" + "/".join(parts)

    @classmethod
    def can_access(cls, user: Any) -> bool:
        if cls.permission is None:
            return user is not None
        from almasix.orbit.panels.resource import _can

        return _can(user, cls.permission)

    @classmethod
    def render(cls, **ctx: Any) -> str:
        return f'<div class="or-page"><h1 class="or-page-title">{e(cls.get_title())}</h1></div>'
