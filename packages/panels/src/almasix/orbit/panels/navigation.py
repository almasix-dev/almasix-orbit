"""Panel navigation — groups, custom items, and Shamar-style split layout."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.evaluate import evaluate

NavLayout = Literal["sidebar", "top", "sidebar_topbar"]


class NavigationItem(Component):
    """Custom or derived navigation link."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._url: str | None = None
        self._icon: str | None = None
        self._group: str | None = None
        self._subgroup: str | None = None
        self._sort: int = 0
        self._active: bool = False

    def url(self, url: str) -> Self:
        self._url = url
        return self

    def icon(self, name: str) -> Self:
        self._icon = name
        return self

    def group(self, name: str | None) -> Self:
        self._group = name
        return self

    def subgroup(self, name: str | None) -> Self:
        self._subgroup = name
        return self

    def sort(self, value: int) -> Self:
        self._sort = value
        return self

    def to_nav_dict(self) -> dict[str, Any]:
        return {
            "slug": self.get_name() or "",
            "label": self.get_label(),
            "icon": self._icon,
            "group": self._group,
            "subgroup": self._subgroup,
            "url": self._url or "#",
            "sort": self._sort,
            "active": self._active,
        }


class NavigationGroup(Component):
    """Named group metadata (icon / sort) for sidebar roots."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._icon: str | None = None
        self._sort: int = 0
        self._items: list[NavigationItem] = []

    def icon(self, name: str) -> Self:
        self._icon = name
        return self

    def sort(self, value: int) -> Self:
        self._sort = value
        return self

    def items(self, items: Sequence[NavigationItem]) -> Self:
        self._items = list(items)
        return self


@dataclass
class MenuRoot:
    label: str
    icon: str | None
    href: str
    root_index: int
    active: bool
    group: str | None = None


@dataclass
class MenuSecondaryChild:
    label: str
    href: str
    active: bool
    icon: str | None = None


@dataclass
class MenuSecondaryItem:
    label: str
    href: str | None = None
    active: bool = False
    icon: str | None = None
    children: list[MenuSecondaryChild] = field(default_factory=list)


@dataclass
class MenuLayoutContext:
    menu_roots: list[MenuRoot]
    menu_active_root: MenuRoot | None
    menu_active_root_index: int | None
    menu_secondary: list[MenuSecondaryItem]
    flat_items: list[dict[str, Any]]
    layout: NavLayout = "sidebar_topbar"


def _sort_key(item: dict[str, Any]) -> tuple[int, str]:
    return (int(item.get("sort") or 0), str(item.get("label") or ""))


def group_items(items: list[dict[str, Any]]) -> dict[str | None, list[dict[str, Any]]]:
    grouped: dict[str | None, list[dict[str, Any]]] = {}
    for item in sorted(items, key=_sort_key):
        grouped.setdefault(item.get("group"), []).append(item)
    return grouped


def build_menu_secondary(
    items: list[dict[str, Any]],
    *,
    active_url: str | None = None,
) -> list[MenuSecondaryItem]:
    """Build top-bar secondary items; subgroups collapse into dropdowns."""
    sorted_items = sorted(items, key=_sort_key)
    entries: list[tuple[int, MenuSecondaryItem]] = []
    subgroups: dict[str, list[dict[str, Any]]] = {}
    subgroup_order: list[str] = []

    for item in sorted_items:
        subgroup = (item.get("subgroup") or "").strip() or None
        active = bool(active_url and item.get("url") == active_url)
        if not subgroup:
            entries.append(
                (
                    int(item.get("sort") or 0),
                    MenuSecondaryItem(
                        label=str(item.get("label") or ""),
                        href=str(item.get("url") or "#"),
                        active=active,
                        icon=item.get("icon"),
                    ),
                )
            )
            continue
        if subgroup not in subgroups:
            subgroups[subgroup] = []
            subgroup_order.append(subgroup)
        subgroups[subgroup].append(item)

    for name in subgroup_order:
        members = subgroups[name]
        children = [
            MenuSecondaryChild(
                label=str(m.get("label") or ""),
                href=str(m.get("url") or "#"),
                active=bool(active_url and m.get("url") == active_url),
                icon=m.get("icon"),
            )
            for m in sorted(members, key=_sort_key)
        ]
        entries.append(
            (
                min(int(m.get("sort") or 0) for m in members),
                MenuSecondaryItem(
                    label=name,
                    href=children[0].href if children else None,
                    active=any(c.active for c in children),
                    children=children,
                ),
            )
        )

    entries.sort(key=lambda pair: (pair[0], pair[1].label))
    return [item for _, item in entries]


def build_menu_layout(
    items: list[dict[str, Any]],
    *,
    group_meta: dict[str, NavigationGroup] | None = None,
    active_path: str | None = None,
    layout: NavLayout = "sidebar_topbar",
    panel_path: str = "/",
) -> MenuLayoutContext:
    """Shamar-style: sidebar roots = groups; topbar = active group's items."""
    meta = group_meta or {}
    flat = list(items)
    grouped = group_items(flat)

    # Resolve active item by longest matching URL prefix
    active_item: dict[str, Any] | None = None
    if active_path:
        candidates = [i for i in flat if active_path.startswith(str(i.get("url") or ""))]
        if candidates:
            active_item = max(candidates, key=lambda i: len(str(i.get("url") or "")))

    active_group = active_item.get("group") if active_item else None
    roots: list[MenuRoot] = []
    root_keys: list[str | None] = []

    # Ordered group keys: named groups by meta sort, then ungrouped
    named = [g for g in grouped if g is not None]
    named.sort(
        key=lambda g: (
            meta[g]._sort if g in meta else 0,
            g or "",
        )
    )
    if None in grouped:
        ordered_keys: list[str | None] = named + [None]
    else:
        ordered_keys = named

    for index, key in enumerate(ordered_keys):
        members = grouped.get(key) or []
        if not members:
            continue
        href = str(members[0].get("url") or panel_path)
        label = key if key is not None else "Menu"
        icon = meta[key]._icon if key in meta else members[0].get("icon")
        active = (key == active_group) if active_group is not None else (index == 0 and active_item is None)
        if active_item and key == active_item.get("group"):
            active = True
        roots.append(
            MenuRoot(
                label=str(label),
                icon=icon,
                href=href,
                root_index=index,
                active=active,
                group=key,
            )
        )
        root_keys.append(key)

    active_root = next((r for r in roots if r.active), roots[0] if roots else None)
    active_index = active_root.root_index if active_root else None
    secondary_source = grouped.get(active_root.group) if active_root else flat
    secondary = build_menu_secondary(
        list(secondary_source or []),
        active_url=str(active_item.get("url")) if active_item else None,
    )

    if layout == "sidebar":
        # Flatten into sidebar only — still preserve group labels in flat list
        secondary = []
    elif layout == "top":
        roots = []
        secondary = build_menu_secondary(flat, active_url=str(active_item.get("url")) if active_item else None)

    return MenuLayoutContext(
        menu_roots=roots,
        menu_active_root=active_root,
        menu_active_root_index=active_index,
        menu_secondary=secondary,
        flat_items=flat,
        layout=layout,
    )


def resolve_active_path(path: str | None, **ctx: Any) -> str | None:
    if path is not None:
        return path
    return evaluate(ctx.get("active_path"), **ctx) if "active_path" in ctx else None
