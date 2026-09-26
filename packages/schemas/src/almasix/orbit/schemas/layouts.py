
"""Layout components for schemas."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.html import e
from almasix.orbit.support.icons import icon as render_icon


class Layout(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._schema: list[Component] = []
        self._dense = False
        self._gap: bool | str = True
        self._defer_loading = False

    def schema(self, components: Sequence[Component]) -> Self:
        self._schema = list(components)
        return self

    def dense(self, condition: bool = True) -> Self:
        self._dense = condition
        return self

    def gap(self, value: bool | str = True) -> Self:
        self._gap = value
        return self

    def defer_loading(self, condition: bool = True) -> Self:
        self._defer_loading = condition
        return self

    def get_child_components(self) -> list[Component]:
        return list(self._schema)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["schema"] = [c.to_dict() for c in self._schema]
        d["dense"] = self._dense
        return d

    def _layout_classes(self, base: str) -> str:
        classes = [base]
        if self._dense:
            classes.append("or-dense")
        if self._gap is False:
            classes.append("or-gap-none")
        elif isinstance(self._gap, str):
            classes.append(f"or-gap-{self._gap}")
        return " ".join(classes)

    def render_children(self, state: Any = None, **ctx: Any) -> str:
        data = state if isinstance(state, dict) else {}
        child_ctx = {**ctx}
        if self.is_inline_label() or ctx.get("inline_label"):
            child_ctx["inline_label"] = True
        return "".join(
            c.render(child_render_state(c, data), **child_ctx)
            for c in self._schema
            if c.is_visible(**child_ctx)
        )


def child_render_state(component: Component, data: dict[str, Any] | None) -> Any:
    """Resolve the state argument for a child during render.

    Nested ``Layout`` containers keep the full state bag so descendant fields can
    resolve their own paths. Leaf fields receive ``data[path]`` only.
    """
    if not isinstance(data, dict):
        return None
    if isinstance(component, Layout):
        return data
    path = component.get_state_path() or ""
    return data.get(path) if path else None


class Grid(Layout):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._columns = 2
        self._grid_container = False

    def columns(self, count: int) -> Self:
        self._columns = count
        return self

    def grid_container(self, condition: bool = True) -> Self:
        self._grid_container = condition
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        classes = self._layout_classes(f"or-grid or-grid-cols-{self._columns}")
        if self._grid_container:
            classes += " or-grid-container"
        defer = ' data-defer="true"' if self._defer_loading else ""
        return f'<div class="{classes}"{defer}>{self.render_children(state, **ctx)}</div>'


class Flex(Layout):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._grow = True
        self._from: str | None = None

    def grow(self, condition: bool = True) -> Self:
        self._grow = condition
        return self

    def from_breakpoint(self, value: str) -> Self:
        """Stack below breakpoint (e.g. ``md``), flex row from that size up."""
        self._from = value
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        classes = self._layout_classes("or-flex")
        if self._grow:
            classes += " or-flex-grow"
        if self._from:
            classes += f" or-flex-from-{e(self._from)}"
        children = []
        data = state if isinstance(state, dict) else {}
        for child in self._schema:
            if not child.is_visible(**ctx):
                continue
            inner = child.render(child_render_state(child, data), **ctx)
            span = child._column_span
            span_cls = f" or-col-span-{span}" if span else ""
            children.append(f'<div class="or-flex-item{span_cls}">{inner}</div>')
        return f'<div class="{classes}">{"".join(children)}</div>'


class Group(Layout):
    """Fuse child components without fieldset chrome (Filament ``Group``)."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._columns: int | None = None

    def columns(self, count: int) -> Self:
        self._columns = count
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        classes = self._layout_classes("or-schema-group")
        if self._columns:
            classes += f" or-grid or-grid-cols-{self._columns}"
        return f'<div class="{classes}">{self.render_children(state, **ctx)}</div>'


class Split(Layout):
    """Side-by-side schema columns that stack below a breakpoint."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._from: str | None = None

    def from_breakpoint(self, value: str) -> Self:
        self._from = value
        return self

    def from_(self, value: str) -> Self:
        return self.from_breakpoint(value)

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        classes = self._layout_classes("or-schema-split")
        if self._from:
            classes += f" or-schema-split-from-{e(self._from)}"
        data = state if isinstance(state, dict) else {}
        children = []
        for child in self._schema:
            if not child.is_visible(**ctx):
                continue
            children.append(
                f'<div class="or-schema-split-item">'
                f"{child.render(child_render_state(child, data), **ctx)}</div>"
            )
        return f'<div class="{classes}">{"".join(children)}</div>'


class Section(Layout):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._heading: str | None = None
        self._description: str | None = None
        self._collapsible = False
        self._collapsed = False
        self._compact = False
        self._aside = False
        self._icon: str | None = None
        self._persist_collapsed = False
        self._secondary = False

    def heading(self, text: str) -> Self:
        self._heading = text
        return self

    def description(self, text: str) -> Self:
        self._description = text
        return self

    def collapsible(self, condition: bool = True) -> Self:
        self._collapsible = condition
        return self

    def collapsed(self, condition: bool = True) -> Self:
        self._collapsed = condition
        return self

    def compact(self, condition: bool = True) -> Self:
        self._compact = condition
        return self

    def aside(self, condition: bool = True) -> Self:
        self._aside = condition
        return self

    def secondary(self, condition: bool = True) -> Self:
        """Muted / secondary section chrome (Filament ``secondary``)."""
        self._secondary = condition
        return self

    def icon(self, name: str) -> Self:
        self._icon = name
        return self

    def persist_collapsed(self, condition: bool = True) -> Self:
        self._persist_collapsed = condition
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        title = e(self._heading or self.get_label())
        desc = f'<p class="or-section-desc">{e(self._description)}</p>' if self._description else ""
        ic = f'<span class="or-section-icon">{render_icon(self._icon)}</span>' if self._icon else ""
        classes = "or-section"
        if self._compact:
            classes += " or-section-compact"
        if self._aside:
            classes += " or-section-aside"
        if self._secondary:
            classes += " or-section-secondary"
        persist = (
            f' data-persist-collapsed="{e(self.get_name() or "section")}"'
            if self._persist_collapsed
            else ""
        )
        collapse_bind = ""
        header_click = ""
        body_bind = ""
        caret = ""
        if self._collapsible:
            collapse_bind = (
                f' x-data="{{ collapsed: {str(self._collapsed).lower()} }}"'
            )
            header_click = (
                ' @click="collapsed = !collapsed" @keydown.enter.prevent="collapsed = !collapsed" '
                '@keydown.space.prevent="collapsed = !collapsed" role="button" tabindex="0" '
                ':aria-expanded="(!collapsed).toString()"'
            )
            body_bind = ' x-show="!collapsed"'
            caret = (
                '<span class="or-section-caret" aria-hidden="true" '
                ':class="collapsed && \'is-collapsed\'">'
                '<svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">'
                '<path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.17l3.71-3.94a.75.75 0 '
                "111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z\" "
                'clip-rule="evenodd" /></svg></span>'
            )
        return (
            f'<section class="{classes}" data-collapsible="{str(self._collapsible).lower()}" '
            f'data-collapsed="{str(self._collapsed).lower()}"{persist}{collapse_bind}>'
            f'<header class="or-section-header"{header_click}>{caret}{ic}'
            f'<div class="or-section-heading"><h3 class="or-section-title">{title}</h3>{desc}</div>'
            f"</header>"
            f'<div class="or-section-body"{body_bind}>{self.render_children(state, **ctx)}</div>'
            f"</section>"
        )


def _extra_markup(component: Component, **ctx: Any) -> tuple[str, str]:
    """Split ``extra_attributes`` into a class token and an attribute string."""
    attrs = dict(component.get_extra_attributes(**ctx))
    extra_class = str(attrs.pop("class", "") or "").strip()
    parts: list[str] = []
    for key, value in attrs.items():
        if value is True:
            parts.append(e(str(key)))
        elif value is False or value is None:
            continue
        else:
            parts.append(f'{e(str(key))}="{e(value)}"')
    attr_html = (" " + " ".join(parts)) if parts else ""
    return extra_class, attr_html


class Tab(Layout):
    """One panel inside :class:`Tabs`.

    ``Tab.make("Account").icon(...).badge(...).schema([...])`` is the way to
    style a tab. ``Tabs.tabs`` still accepts ``(label, schema)`` tuples and
    dicts, and turns those into ``Tab`` instances.
    """

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._icon: str | None = None
        self._badge: Any = None
        self._badge_color: str | None = None

    def icon(self, name: str | None) -> Self:
        self._icon = name
        return self

    def badge(self, value: Any) -> Self:
        self._badge = value
        return self

    def badge_color(self, color: str | None) -> Self:
        """Tint the badge. ``success``, ``danger``, ``warning``, or ``info``."""
        self._badge_color = color
        return self


class Tabs(Layout):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._tabs: list[Tab] = []
        self._persist_tab = False
        self._active_tab: int = 0

    def tabs(self, *tab_defs: Tab | tuple[str, Sequence[Component]] | dict[str, Any]) -> Self:
        parsed: list[Tab] = []
        for item in tab_defs:
            if isinstance(item, Tab):
                parsed.append(item)
                continue
            if isinstance(item, dict):
                tab = Tab.make(item.get("id") or None)
                tab.label(str(item.get("label") or item.get("id") or "Tab"))
                tab.schema(list(item.get("schema") or item.get("components") or []))
                if item.get("icon"):
                    tab.icon(str(item["icon"]))
                if item.get("badge") is not None:
                    tab.badge(item.get("badge"))
                if item.get("badge_color"):
                    tab.badge_color(str(item["badge_color"]))
                parsed.append(tab)
                continue
            label, comps = item
            parsed.append(Tab.make().label(str(label)).schema(list(comps)))
        self._tabs = parsed
        return self

    def persist_tab(self, condition: bool = True) -> Self:
        self._persist_tab = condition
        return self

    def active_tab(self, index: int) -> Self:
        self._active_tab = max(0, int(index))
        return self

    def get_child_components(self) -> list[Component]:
        out: list[Component] = []
        for tab in self._tabs:
            out.extend(tab.get_child_components())
        out.extend(self._schema)
        return out

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        nav = []
        bodies = []
        data = state if isinstance(state, dict) else {}
        active_i = min(self._active_tab, max(len(self._tabs) - 1, 0)) if self._tabs else 0
        for i, tab in enumerate(self._tabs):
            if not tab.is_visible(**ctx):
                continue
            active = " is-active" if i == active_i else ""
            icon = tab._icon
            ic = f'<span class="or-tab-icon">{render_icon(icon)}</span>' if icon else ""
            badge_html = ""
            badge = tab._badge
            if badge is not None:
                badge_val = badge(**ctx) if callable(badge) else badge
                if badge_val is not None:
                    color = f" or-nav-badge-{e(tab._badge_color)}" if tab._badge_color else ""
                    badge_html = f'<span class="or-tab-badge{color}">{e(badge_val)}</span>'
            extra_class, extra_attrs = _extra_markup(tab, **ctx)
            class_attr = f"or-tab{active}{(' ' + extra_class) if extra_class else ''}"
            tab_id = tab.get_name()
            id_attr = f' data-tab-id="{e(tab_id)}"' if tab_id else ""
            nav.append(
                f'<button type="button" class="{class_attr}" data-tab="{i}"{id_attr}{extra_attrs} '
                f'@click="tab = {i}" :class="tab === {i} && \'is-active\'">'
                f"{ic}{e(tab.get_label(**ctx))}{badge_html}</button>"
            )
            inner = "".join(
                c.render(child_render_state(c, data), **ctx)
                for c in tab.get_child_components()
                if c.is_visible(**ctx)
            )
            bodies.append(
                f'<div class="or-tab-panel{active}" data-panel="{i}" '
                f'x-show="tab === {i}" {"" if i == active_i else "x-cloak"}>{inner}</div>'
            )
        persist = (
            f' data-persist-tab="{e(self.get_name() or "tabs")}"' if self._persist_tab else ""
        )
        return (
            f'<div class="or-tabs" x-data="{{ tab: {active_i} }}"{persist}>'
            f'<div class="or-tabs-nav">{"".join(nav)}</div>'
            f'<div class="or-tabs-body">{"".join(bodies)}</div>'
            "</div>"
        )


class Fieldset(Layout):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._contained = True

    def contained(self, condition: bool = True) -> Self:
        """When False, drop card chrome and render a bare fieldset (Filament ``contained``)."""
        self._contained = condition
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        legend = e(self.get_label())
        contained = "" if self._contained else " or-fieldset-bare"
        return (
            f'<fieldset class="or-fieldset{contained}">'
            f'<legend class="or-fieldset-legend">{legend}</legend>'
            f"{self.render_children(state, **ctx)}</fieldset>"
        )


class WizardStep(Layout):
    """One step inside :class:`Wizard`.

    ``WizardStep.make("Account").description(...).icon(...).schema([...])``
    carries the label, copy, and icons. ``Wizard.steps`` still accepts
    ``(label, schema)`` tuples and dicts.
    """

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._description: str | None = None
        self._icon: str | None = None
        self._completed_icon: str | None = None

    def description(self, text: str | None) -> Self:
        self._description = text
        return self

    def icon(self, name: str | None) -> Self:
        self._icon = name
        return self

    def completed_icon(self, name: str | None) -> Self:
        """Icon shown in the stepper once this step has been passed."""
        self._completed_icon = name
        return self


class Wizard(Layout):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._steps: list[WizardStep] = []
        self._skippable = False
        self._start_step: int = 0
        self._linear = True
        self._vertical = False

    def steps(
        self, *step_defs: WizardStep | tuple[str, Sequence[Component]] | dict[str, Any]
    ) -> Self:
        parsed: list[WizardStep] = []
        for item in step_defs:
            if isinstance(item, WizardStep):
                parsed.append(item)
                continue
            if isinstance(item, dict):
                step = WizardStep.make(item.get("id") or None)
                step.label(str(item.get("label") or item.get("id") or "Step"))
                step.schema(list(item.get("schema") or item.get("components") or []))
                if item.get("description"):
                    step.description(str(item["description"]))
                if item.get("icon"):
                    step.icon(str(item["icon"]))
                if item.get("completed_icon"):
                    step.completed_icon(str(item["completed_icon"]))
                parsed.append(step)
                continue
            label, comps = item
            parsed.append(WizardStep.make().label(str(label)).schema(list(comps)))
        self._steps = parsed
        return self

    def skippable(self, condition: bool = True) -> Self:
        self._skippable = condition
        return self

    def start_step(self, index: int) -> Self:
        self._start_step = max(0, int(index))
        return self

    def linear(self, condition: bool = True) -> Self:
        """Require completing the current step before advancing (default).

        When linear, nav jumps ahead are blocked until earlier steps are reached
        via Continue (HTML5 constraint validation on fields in the current pane).
        Pass ``False`` (or use :meth:`non_linear`) to allow free step jumping.
        """
        self._linear = bool(condition)
        return self

    def non_linear(self, condition: bool = True) -> Self:
        """Allow jumping to any step from the stepper nav."""
        self._linear = not bool(condition)
        return self

    def vertical(self, condition: bool = True) -> Self:
        """Place the stepper beside the step body instead of above it."""
        self._vertical = bool(condition)
        return self

    def get_child_components(self) -> list[Component]:
        out: list[Component] = []
        for step in self._steps:
            out.extend(step.get_child_components())
        out.extend(self._schema)
        return out

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        parts = []
        nav = []
        data = state if isinstance(state, dict) else {}
        visible = [step for step in self._steps if step.is_visible(**ctx)]
        total = len(visible)
        start = min(self._start_step, max(total - 1, 0)) if total else 0
        last = max(total - 1, 0)
        for i, step in enumerate(visible):
            label = step.get_label(**ctx)
            inner = "".join(
                c.render(child_render_state(c, data), **ctx)
                for c in step.get_child_components()
                if c.is_visible(**ctx)
            )
            desc = (
                f'<p class="or-wizard-step-desc">{e(step._description)}</p>'
                if step._description
                else ""
            )
            parts.append(
                f'<div class="or-wizard-step" data-step="{i}" x-show="step === {i}" '
                f'{"" if i == start else "x-cloak"}>'
                f'<h4 class="or-wizard-step-title">{e(label)}</h4>{desc}{inner}</div>'
            )
            connector = (
                '<span class="or-wizard-nav-connector" aria-hidden="true"></span>'
                if i < last
                else ""
            )
            index_num = render_icon(step._icon) if step._icon else str(i + 1)
            done = render_icon(step._completed_icon) if step._completed_icon else "✓"
            extra_class, extra_attrs = _extra_markup(step, **ctx)
            nav_class = "or-wizard-nav-item" + (f" {extra_class}" if extra_class else "")
            nav.append(
                f'<button type="button" class="{nav_class}" data-step="{i}"{extra_attrs} '
                f'@click="go({i})" '
                f":class=\"{{ "
                f"'is-active': step === {i}, "
                f"'is-complete': step > {i}, "
                f"'is-locked': linear && {i} > maxReached "
                f'}}" '
                f":aria-current=\"step === {i} ? 'step' : null\" "
                f':disabled="linear && {i} > maxReached" '
                f':aria-disabled="(linear && {i} > maxReached).toString()">'
                f'<span class="or-wizard-nav-index" aria-hidden="true">'
                f'<span class="or-wizard-nav-index-num" x-show="step <= {i}">{index_num}</span>'
                f'<span class="or-wizard-nav-check" x-cloak x-show="step > {i}">{done}</span>'
                f"</span>"
                f'<span class="or-wizard-nav-text">'
                f'<span class="or-wizard-nav-label">{e(label)}</span>'
                f'<span class="or-wizard-nav-meta">Step {i + 1} of {total}</span>'
                f"</span></button>{connector}"
            )
        skip = ""
        if self._skippable:
            skip = (
                '<button type="button" class="or-link-btn" @click="skip()">'
                "Skip</button>"
            )
        footer = (
            f'<div class="or-wizard-footer">'
            f'<button type="button" class="or-btn or-btn-gray or-btn-sm" '
            f'@click="back()" :disabled="step === 0">Back</button>'
            f"{skip}"
            f'<button type="button" class="or-btn or-btn-primary or-btn-sm" '
            f'@click="next()" '
            f':disabled="step === {last}">Continue</button>'
            f"</div>"
        )
        orientation = " or-wizard--vertical" if self._vertical else " or-wizard--horizontal"
        linear_attr = "true" if self._linear else "false"
        return (
            f'<div class="or-wizard{orientation}" x-data="orbitWizard" '
            f'data-steps="{total}" data-start="{start}" data-linear="{linear_attr}" '
            f'data-orientation="{"vertical" if self._vertical else "horizontal"}">'
            f'<div class="or-wizard-nav" role="list">{"".join(nav)}</div>'
            f'<div class="or-wizard-main">'
            f'<div class="or-wizard-body">{"".join(parts)}</div>'
            f"{footer}</div></div>"
        )


class Callout(Layout):
    """Status callout with optional footer actions."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._description: str | None = None
        self._status: str = "info"
        self._color: str | None = None
        self._icon: str | None = None
        self._icon_color: str | None = None
        self._footer_actions: list[Component] = []
        self._footer_alignment: str = "start"

    def description(self, text: str) -> Self:
        self._description = text
        return self

    def status(self, value: str) -> Self:
        self._status = value
        return self

    def danger(self) -> Self:
        return self.status("danger")

    def info(self) -> Self:
        return self.status("info")

    def success(self) -> Self:
        return self.status("success")

    def warning(self) -> Self:
        return self.status("warning")

    def color(self, value: str) -> Self:
        self._color = value
        return self

    def icon(self, name: str) -> Self:
        self._icon = name
        return self

    def icon_color(self, value: str) -> Self:
        self._icon_color = value
        return self

    def footer_actions(self, actions: Sequence[Component]) -> Self:
        self._footer_actions = list(actions)
        return self

    def footer_actions_alignment(self, value: str) -> Self:
        self._footer_alignment = value
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        color = self._color or self._status
        title = e(self.get_label(**ctx) or self._status.title())
        desc = f'<p class="or-callout-desc">{e(self._description)}</p>' if self._description else ""
        body = self.render_children(state, **ctx)
        ic_name = self._icon or {
            "danger": "heroicon-o-x-mark",
            "success": "heroicon-o-check",
            "warning": "heroicon-o-bell",
            "info": "heroicon-o-information-circle",
        }.get(self._status, "heroicon-o-information-circle")
        ic = render_icon(ic_name)
        icon_color = self._icon_color or color
        footer = ""
        if self._footer_actions:
            acts = "".join(a.render(state, **ctx) for a in self._footer_actions)
            footer = (
                f'<div class="or-callout-footer or-align-{e(self._footer_alignment)}">{acts}</div>'
            )
        return (
            f'<div class="or-callout or-callout-{e(self._status)} or-color-{e(color)}" role="status">'
            f'<div class="or-callout-icon or-color-{e(icon_color)}">{ic}</div>'
            f'<div class="or-callout-body"><div class="or-callout-title">{title}</div>'
            f"{desc}{body}</div>{footer}</div>"
        )


class EmptyState(Layout):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._heading: str | None = None
        self._description: str | None = None
        self._icon: str | None = None
        self._actions: list[Component] = []

    def heading(self, text: str) -> Self:
        self._heading = text
        return self

    def description(self, text: str) -> Self:
        self._description = text
        return self

    def icon(self, name: str) -> Self:
        self._icon = name
        return self

    def actions(self, actions: Sequence[Component]) -> Self:
        self._actions = list(actions)
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        title = e(self._heading or self.get_label(**ctx) or "Nothing here")
        desc = f'<p class="or-empty-state-desc">{e(self._description)}</p>' if self._description else ""
        ic = f'<div class="or-empty-state-icon">{render_icon(self._icon)}</div>' if self._icon else ""
        acts = "".join(a.render(state, **ctx) for a in self._actions)
        actions_html = f'<div class="or-empty-state-actions">{acts}</div>' if acts else ""
        body = self.render_children(state, **ctx)
        return (
            f'<div class="or-empty-state or-schema-empty">'
            f"{ic}<h3 class=\"or-empty-state-heading\">{title}</h3>{desc}{body}{actions_html}</div>"
        )
