"""Resource CRUD page hosts — List / Create / Edit / View."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit.panels.content_width import resolve_content_max_width
from almasix.orbit.panels.page import Page
from almasix.orbit.support.conduit_attrs import conduit_attr
from almasix.orbit.support.html import e


def _resource_width_style(resource: type[Any]) -> str:
    raw = getattr(resource, "content_max_width", None)
    if not raw:
        return ""
    return f' style="max-width: {e(resolve_content_max_width(raw).css_value)}"'


class Tab:
    """List-page filter tab."""

    def __init__(self, id: str, label: str | None = None) -> None:
        self.id = id
        self._label = label or id.replace("_", " ").title()
        self._icon: str | None = None
        self._badge: str | int | None = None
        self._badge_color: str | None = None
        self._modify_query: Any = None

    def label(self, text: str) -> Tab:
        self._label = text
        return self

    def icon(self, name: str) -> Tab:
        self._icon = name
        return self

    def badge(self, value: str | int) -> Tab:
        self._badge = value
        return self

    def badge_color(self, color: str) -> Tab:
        self._badge_color = color
        return self

    def modify_query_using(self, callback: Any) -> Tab:
        self._modify_query = callback
        return self

    def apply_query(self, records: list[Any]) -> list[Any]:
        if self._modify_query is None:
            return records
        return list(self._modify_query(records))

    def render(self, *, active: bool = False) -> str:
        from almasix.orbit.support.icons import icon as render_icon

        active_cls = " is-active" if active else ""
        ic = render_icon(self._icon) if self._icon else ""
        badge = ""
        if self._badge is not None:
            color = f" or-color-{e(self._badge_color)}" if self._badge_color else ""
            badge = f'<span class="or-nav-badge{color}">{e(self._badge)}</span>'
        return (
            f'<button type="button" class="or-list-tab{active_cls}" data-tab="{e(self.id)}" '
            f'wire:click="setTab(\'{e(self.id)}\')">{ic}<span>{e(self._label)}</span>{badge}</button>'
        )


class ResourcePage(Page):
    """Base page bound to a Resource class."""

    resource: ClassVar[type[Any] | None] = None

    @classmethod
    def get_resource(cls) -> type[Any]:
        if cls.resource is None:
            raise RuntimeError(f"{cls.__name__} must set resource = YourResource")
        return cls.resource


class ListRecords(ResourcePage):
    """Index page: tabs + table + header actions."""

    @classmethod
    def get_tabs(cls) -> list[Tab]:
        return []

    @classmethod
    def get_default_active_tab(cls) -> str | None:
        tabs = cls.get_tabs()
        return tabs[0].id if tabs else None

    @classmethod
    def render(cls, records: list[Any] | None = None, active_tab: str | None = None, **ctx: Any) -> str:
        resource = cls.get_resource()
        title = e(resource.get_navigation_label())
        tabs = cls.get_tabs()
        active = active_tab or cls.get_default_active_tab()
        tab_html = ""
        if tabs:
            tab_html = (
                '<div class="or-list-tabs">'
                + "".join(t.render(active=(t.id == active)) for t in tabs)
                + "</div>"
            )
            for t in tabs:
                if t.id == active and records is not None:
                    records = t.apply_query(records)
        table = resource.get_table()
        if records is not None:
            table.records(records)
        header_actions = "".join(a.render(**ctx) for a in table._header_actions)
        width = _resource_width_style(resource)
        return (
            f'<div class="or-page or-page-list" data-resource="{e(resource.get_slug())}"{width}>'
            f'<header class="or-page-header"><h1 class="or-page-title">{title}</h1>'
            f'<div class="or-page-actions">{header_actions}</div></header>'
            f"{tab_html}{table.render(skip_header_actions=True, **ctx)}</div>"
        )


class CreateRecord(ResourcePage):
    @classmethod
    def render(cls, state: dict[str, Any] | None = None, **ctx: Any) -> str:
        resource = cls.get_resource()
        form = resource.get_form()
        if state:
            form.fill(state)
        return (
            f'<div class="or-page or-page-create" data-resource="{e(resource.get_slug())}"'
            f"{_resource_width_style(resource)}>"
            f'<h1 class="or-page-title">Create {e(resource.get_navigation_label())}</h1>'
            f'<form class="or-form"{conduit_attr("submit", "create")}>'
            f"{form.render(form.get_state() if state is None else state, **ctx)}"
            f'<div class="or-form-actions">'
            f'<button type="submit" class="or-btn or-btn-primary">Create</button></div>'
            f"</form></div>"
        )


class EditRecord(ResourcePage):
    @classmethod
    def render(cls, record: Any = None, state: dict[str, Any] | None = None, **ctx: Any) -> str:
        resource = cls.get_resource()
        form = resource.get_form()
        data = state
        if data is None and record is not None:
            data = {}
            for c in form.get_components():
                name = c.get_state_path() or c.get_name()
                if not name:
                    continue
                data[name] = record[name] if isinstance(record, dict) else getattr(record, name, None)
        if data:
            form.fill(data)
        record_id = ""
        if record is not None:
            record_id = str(record.get("id", "") if isinstance(record, dict) else getattr(record, "id", ""))
        return (
            f'<div class="or-page or-page-edit" data-resource="{e(resource.get_slug())}" '
            f'data-record="{e(record_id)}"{_resource_width_style(resource)}>'
            f'<h1 class="or-page-title">Edit {e(resource.get_navigation_label())}</h1>'
            f'<form class="or-form"{conduit_attr("submit", "save")}>'
            f"{form.render(data or form.get_state(), **ctx)}"
            f'<div class="or-form-actions">'
            f'<button type="submit" class="or-btn or-btn-primary">Save</button></div>'
            f"</form></div>"
        )


class ViewRecord(ResourcePage):
    @classmethod
    def render(cls, record: Any = None, **ctx: Any) -> str:
        resource = cls.get_resource()
        infolist = resource.get_infolist()
        record_id = ""
        if record is not None:
            record_id = str(record.get("id", "") if isinstance(record, dict) else getattr(record, "id", ""))
        return (
            f'<div class="or-page or-page-view" data-resource="{e(resource.get_slug())}" '
            f'data-record="{e(record_id)}"{_resource_width_style(resource)}>'
            f'<h1 class="or-page-title">{e(resource.get_navigation_label())}</h1>'
            f"{infolist.render(record, **ctx)}</div>"
        )
