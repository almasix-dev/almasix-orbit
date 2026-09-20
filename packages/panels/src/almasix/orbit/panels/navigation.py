"""Panel navigation — groups, custom items, and Shamar-style split layout."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.evaluate import evaluate

NavLayout = Literal["sidebar", "top", "sidebar_topbar", "apps"]


def normalize_nav_layout(layout: str) -> Literal["sidebar", "top", "sidebar_topbar"]:
    """Map public aliases onto internal layout modes (``apps`` → ``sidebar_topbar``)."""
    if layout == "apps":
        return "sidebar_topbar"
    if layout in ("sidebar", "top", "sidebar_topbar"):
        return layout  # type: ignore[return-value]
    return "sidebar_topbar"


class NavigationItem(Component):
    """Custom or derived navigation link."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._url: str | None = None
        self._icon: str | None = None
        self._active_icon: str | None = None
        self._group: str | None = None
        self._subgroup: str | None = None
        self._sort: int = 0
        self._active: bool = False
        self._badge: Any = None
        self._badge_color: Any = None
        self._badge_tooltip: Any = None
        self._open_url_in_new_tab: bool | Callable[..., bool] = False
        self._is_active_when: Callable[..., bool] | None = None
        self._parent_item: str | None = None

    def url(self, url: str) -> Self:
        self._url = url
        return self

    def icon(self, name: str) -> Self:
        self._icon = name
        return self

    def active_icon(self, name: str) -> Self:
        self._active_icon = name
        return self

    def group(self, name: str | None) -> Self:
        self._group = name
        return self

    def subgroup(self, name: str | None) -> Self:
        self._subgroup = name
        return self

    def sub_category(self, name: str | None) -> Self:
        """Alias for :meth:`subgroup` (second-level nav category)."""
        return self.subgroup(name)

    def sort(self, value: int) -> Self:
        self._sort = value
        return self

    def badge(
        self,
        value: Any = None,
        color: Any = None,
    ) -> Self:
        """Set badge text (or callable) and optional color."""
        self._badge = value
        if color is not None:
            self._badge_color = color
        return self

    def badge_color(self, color: Any) -> Self:
        self._badge_color = color
        return self

    def badge_tooltip(self, tooltip: Any) -> Self:
        self._badge_tooltip = tooltip
        return self

    def open_url_in_new_tab(self, condition: bool | Callable[..., bool] = True) -> Self:
        self._open_url_in_new_tab = condition
        return self

    def is_active_when(self, callback: Callable[..., bool]) -> Self:
        self._is_active_when = callback
        return self

    def parent_item(self, label: str | None) -> Self:
        """Nest this item under another nav item (by label)."""
        self._parent_item = (str(label).strip() or None) if label is not None else None
        return self

    def resolve_active(self, **ctx: Any) -> bool:
        if self._is_active_when is not None:
            return bool(evaluate(self._is_active_when, **ctx))
        return bool(self._active)

    def to_nav_dict(self, **ctx: Any) -> dict[str, Any]:
        badge = evaluate(self._badge, **ctx)
        badge_color = evaluate(self._badge_color, **ctx)
        badge_tooltip = evaluate(self._badge_tooltip, **ctx)
        open_new = bool(evaluate(self._open_url_in_new_tab, **ctx))
        active = self.resolve_active(**ctx) if self._is_active_when is not None else bool(self._active)
        return {
            "slug": self.get_name() or "",
            "label": self.get_label(**ctx),
            "icon": self._icon,
            "active_icon": self._active_icon,
            "group": self._group,
            "subgroup": self._subgroup,
            "url": self._url or "#",
            "sort": self._sort,
            "active": active,
            "badge": None if badge is None else str(badge),
            "badge_color": None if badge_color is None else str(badge_color),
            "badge_tooltip": None if badge_tooltip is None else str(badge_tooltip),
            "open_in_new_tab": open_new,
            "parent_item": self._parent_item,
            "is_active_when": self._is_active_when,
        }


class NavigationGroup(Component):
    """Named group metadata (icon / sort) for sidebar roots."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._icon: str | None = None
        self._sort: int = 0
        self._items: list[NavigationItem] = []
        self._collapsed: bool | Callable[..., bool] = False
        self._collapsible: bool | Callable[..., bool] = True
        self._extra_sidebar_attributes: dict[str, Any] = {}
        self._extra_topbar_attributes: dict[str, Any] = {}

    def icon(self, name: str) -> Self:
        self._icon = name
        return self

    def sort(self, value: int) -> Self:
        self._sort = value
        return self

    def items(self, items: Sequence[NavigationItem]) -> Self:
        self._items = list(items)
        return self

    def collapsed(self, condition: bool | Callable[..., bool] = True) -> Self:
        self._collapsed = condition
        return self

    def collapsible(self, condition: bool | Callable[..., bool] = True) -> Self:
        self._collapsible = condition
        return self

    def extra_sidebar_attributes(self, attrs: dict[str, Any]) -> Self:
        self._extra_sidebar_attributes.update(attrs)
        return self

    def extra_topbar_attributes(self, attrs: dict[str, Any]) -> Self:
        self._extra_topbar_attributes.update(attrs)
        return self

    def is_collapsed(self, **ctx: Any) -> bool:
        return bool(evaluate(self._collapsed, **ctx))

    def is_collapsible(self, **ctx: Any) -> bool:
        return bool(evaluate(self._collapsible, **ctx))

    def get_extra_sidebar_attributes(self, **ctx: Any) -> dict[str, Any]:
        return {k: evaluate(v, **ctx) for k, v in self._extra_sidebar_attributes.items()}

    def get_extra_topbar_attributes(self, **ctx: Any) -> dict[str, Any]:
        return {k: evaluate(v, **ctx) for k, v in self._extra_topbar_attributes.items()}


class NavigationSubgroup(Component):
    """Second-level nav category metadata (icon / sort / parent group).

    Used under a :class:`NavigationGroup` for sidebar accordions and topbar
    dropdowns (``apps`` layout secondary items).
    """

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._parent: str | None = None
        self._icon: str | None = None
        self._sort: int = 0

    def parent(self, group: str | None) -> Self:
        """Parent navigation group label (``None`` = ungrouped root)."""
        self._parent = (str(group).strip() or None) if group is not None else None
        return self

    def icon(self, name: str) -> Self:
        self._icon = name
        return self

    def sort(self, value: int) -> Self:
        self._sort = value
        return self


class NavigationBuilder:
    """Replace the entire panel navigation via :meth:`Panel.navigation`."""

    def __init__(self) -> None:
        self._items: list[NavigationItem] = []
        self._groups: list[NavigationGroup] = []

    @classmethod
    def make(cls) -> Self:
        return cls()

    def items(self, items: Sequence[NavigationItem]) -> Self:
        self._items = list(items)
        return self

    def groups(self, groups: Sequence[NavigationGroup]) -> Self:
        self._groups = list(groups)
        for group in groups:
            for item in getattr(group, "_items", []) or []:
                if not item._group:
                    name = group.get_name() or group.get_label()
                    item.group(str(name) if name else None)
                self._items.append(item)
        return self

    def item(self, item: NavigationItem) -> Self:
        self._items.append(item)
        return self

    def get_items(self) -> list[NavigationItem]:
        return list(self._items)

    def get_groups(self) -> list[NavigationGroup]:
        return list(self._groups)


def _subgroup_meta_key(parent: str | None, name: str) -> tuple[str | None, str]:
    return (parent, name)


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
    active_icon: str | None = None
    badge: str | None = None
    badge_color: str | None = None
    badge_tooltip: str | None = None
    open_in_new_tab: bool = False
    parent_item: str | None = None
    children: list[MenuSecondaryChild] = field(default_factory=list)


@dataclass
class MenuSecondaryItem:
    label: str
    href: str | None = None
    active: bool = False
    icon: str | None = None
    active_icon: str | None = None
    badge: str | None = None
    badge_color: str | None = None
    badge_tooltip: str | None = None
    open_in_new_tab: bool = False
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


def nest_parent_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attach items with ``parent_item`` under matching parents (by label)."""
    roots: list[dict[str, Any]] = []
    by_label: dict[str, dict[str, Any]] = {}
    children_bucket: list[dict[str, Any]] = []

    for raw in items:
        item = dict(raw)
        item.setdefault("children", [])
        parent = (item.get("parent_item") or "").strip() or None
        if parent:
            children_bucket.append(item)
        else:
            roots.append(item)
            label = str(item.get("label") or "")
            if label:
                by_label[label] = item

    orphaned: list[dict[str, Any]] = []
    for child in children_bucket:
        parent_label = str(child.get("parent_item") or "")
        parent = by_label.get(parent_label)
        if parent is not None:
            parent.setdefault("children", []).append(child)
        else:
            orphaned.append(child)

    return roots + orphaned


def build_menu_secondary(
    items: list[dict[str, Any]],
    *,
    active_url: str | None = None,
    subgroup_meta: dict[tuple[str | None, str], NavigationSubgroup] | None = None,
    parent_group: str | None = None,
) -> list[MenuSecondaryItem]:
    """Build top-bar secondary items; subgroups collapse into dropdowns."""
    sorted_items = sorted(items, key=_sort_key)
    entries: list[tuple[int, MenuSecondaryItem]] = []
    subgroups: dict[str, list[dict[str, Any]]] = {}
    subgroup_order: list[str] = []
    meta = subgroup_meta or {}

    for item in sorted_items:
        subgroup = (item.get("subgroup") or item.get("sub_category") or "").strip() or None
        active = bool(item.get("active")) or bool(active_url and item.get("url") == active_url)
        child = MenuSecondaryChild(
            label=str(item.get("label") or ""),
            href=str(item.get("url") or "#"),
            active=active,
            icon=item.get("icon"),
            active_icon=item.get("active_icon"),
            badge=item.get("badge"),
            badge_color=item.get("badge_color"),
            badge_tooltip=item.get("badge_tooltip"),
            open_in_new_tab=bool(item.get("open_in_new_tab")),
            parent_item=item.get("parent_item"),
        )
        if not subgroup:
            entries.append(
                (
                    int(item.get("sort") or 0),
                    MenuSecondaryItem(
                        label=child.label,
                        href=child.href,
                        active=child.active,
                        icon=child.icon,
                        active_icon=child.active_icon,
                        badge=child.badge,
                        badge_color=child.badge_color,
                        badge_tooltip=child.badge_tooltip,
                        open_in_new_tab=child.open_in_new_tab,
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
                active=bool(m.get("active")) or bool(active_url and m.get("url") == active_url),
                icon=m.get("icon"),
                active_icon=m.get("active_icon"),
                badge=m.get("badge"),
                badge_color=m.get("badge_color"),
                badge_tooltip=m.get("badge_tooltip"),
                open_in_new_tab=bool(m.get("open_in_new_tab")),
            )
            for m in sorted(members, key=_sort_key)
        ]
        registered = meta.get(_subgroup_meta_key(parent_group, name))
        group_icon = registered._icon if registered is not None else None
        if not group_icon:
            icons = [m.get("icon") for m in members if m.get("icon")]
            group_icon = icons[0] if icons and len(set(icons)) == 1 else (icons[0] if icons else None)
        sort_val = (
            registered._sort
            if registered is not None
            else min(int(m.get("sort") or 0) for m in members)
        )
        entries.append(
            (
                sort_val,
                MenuSecondaryItem(
                    label=name,
                    href=children[0].href if children else None,
                    active=any(c.active for c in children),
                    icon=group_icon,
                    children=children,
                ),
            )
        )

    entries.sort(key=lambda pair: (pair[0], pair[1].label))
    return [item for _, item in entries]


def _item_matches_path(active_path: str, url: str | None) -> bool:
    """True when ``active_path`` is the item URL or a nested path under it.

    Panel home ``/`` is an exact match only — otherwise every path would match
    the empty prefix after stripping trailing slashes.
    """
    u = str(url or "").rstrip("/") or "/"
    p = str(active_path or "").rstrip("/") or "/"
    if u == "/":
        return p == "/"
    return p == u or p.startswith(u + "/")


def apply_active_state(
    items: list[dict[str, Any]],
    *,
    active_path: str | None = None,
) -> list[dict[str, Any]]:
    """Mark active items using path match and optional ``is_active_when`` callbacks."""
    flat = [dict(i) for i in items]
    ctx = {"active_path": active_path, "path": active_path}

    for item in flat:
        callback = item.get("is_active_when")
        if callable(callback):
            item["active"] = bool(evaluate(callback, **ctx))

    if active_path:
        candidates = [
            i
            for i in flat
            if not callable(i.get("is_active_when")) and _item_matches_path(active_path, i.get("url"))
        ]
        if candidates:
            best = max(candidates, key=lambda i: len(str(i.get("url") or "")))
            best_url = str(best.get("url") or "")
            for item in flat:
                if callable(item.get("is_active_when")):
                    continue
                item["active"] = str(item.get("url") or "") == best_url
        else:
            for item in flat:
                if not callable(item.get("is_active_when")):
                    item["active"] = False
    else:
        for item in flat:
            if not callable(item.get("is_active_when")):
                item.setdefault("active", False)

    return flat


def build_menu_layout(
    items: list[dict[str, Any]],
    *,
    group_meta: dict[str, NavigationGroup] | None = None,
    subgroup_meta: dict[tuple[str | None, str], NavigationSubgroup] | None = None,
    active_path: str | None = None,
    layout: NavLayout = "sidebar_topbar",
    panel_path: str = "/",
    group_order: Sequence[str] | None = None,
) -> MenuLayoutContext:
    """Shamar-style: sidebar roots = groups; topbar = active group's items."""
    layout = normalize_nav_layout(layout)  # type: ignore[assignment]
    meta = group_meta or {}
    sub_meta = subgroup_meta or {}
    flat = apply_active_state(items, active_path=active_path)
    for item in flat:
        # Normalize alias key onto ``subgroup``
        if not item.get("subgroup") and item.get("sub_category"):
            item["subgroup"] = item.get("sub_category")
    grouped = group_items(flat)

    active_item: dict[str, Any] | None = next((i for i in flat if i.get("active")), None)
    active_url = str(active_item.get("url")) if active_item else None

    active_group = active_item.get("group") if active_item else None
    roots: list[MenuRoot] = []
    root_keys: list[str | None] = []

    # Ordered group keys: explicit order, then named by meta sort, then ungrouped
    named = [g for g in grouped if g is not None]
    if group_order:
        order_index = {name: i for i, name in enumerate(group_order)}
        named.sort(
            key=lambda g: (
                order_index.get(g, len(order_index)),
                meta[g]._sort if g in meta else min(int(m.get("sort") or 0) for m in grouped[g]),
                g or "",
            )
        )
    else:
        named.sort(
            key=lambda g: (
                meta[g]._sort if g in meta else min(int(m.get("sort") or 0) for m in grouped[g]),
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
        active_url=active_url,
        subgroup_meta=sub_meta,
        parent_group=active_root.group if active_root else None,
    )

    if layout == "sidebar":
        # Flatten into sidebar only — still preserve group labels in flat list
        secondary = []
    elif layout == "top":
        # Top chrome: each navigation group is a dropdown; ungrouped items stay links.
        # Subgroups are ordered together inside the group dropdown (flat children).
        roots = []
        secondary_items: list[MenuSecondaryItem] = []
        for key in ordered_keys:
            members = grouped.get(key) or []
            if not members:
                continue
            if key is None:
                secondary_items.extend(
                    build_menu_secondary(
                        members,
                        active_url=active_url,
                        subgroup_meta=sub_meta,
                        parent_group=None,
                    )
                )
                continue
            children = [
                MenuSecondaryChild(
                    label=str(m.get("label") or ""),
                    href=str(m.get("url") or "#"),
                    active=bool(m.get("active")) or bool(active_url and m.get("url") == active_url),
                    icon=m.get("icon"),
                    active_icon=m.get("active_icon"),
                    badge=m.get("badge"),
                    badge_color=m.get("badge_color"),
                    badge_tooltip=m.get("badge_tooltip"),
                    open_in_new_tab=bool(m.get("open_in_new_tab")),
                )
                for m in sorted(
                    members,
                    key=lambda m: (
                        str(m.get("subgroup") or m.get("sub_category") or ""),
                        *_sort_key(m),
                    ),
                )
            ]
            group_icon = meta[key]._icon if key in meta else None
            if not group_icon:
                group_icon = next((c.icon for c in children if c.icon), None)
            secondary_items.append(
                MenuSecondaryItem(
                    label=str(key),
                    href=children[0].href if children else None,
                    active=any(c.active for c in children),
                    icon=group_icon,
                    children=children,
                )
            )
        secondary = secondary_items

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


def attrs_to_html(attrs: dict[str, Any]) -> str:
    """Serialize extra HTML attributes for nav group wrappers."""
    parts: list[str] = []
    for key, value in attrs.items():
        if value is None or value is False:
            continue
        if value is True:
            parts.append(e_attr(key))
            continue
        parts.append(f'{e_attr(key)}="{e_attr(str(value))}"')
    return (" " + " ".join(parts)) if parts else ""


def e_attr(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
