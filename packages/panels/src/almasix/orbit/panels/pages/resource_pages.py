"""Resource CRUD page hosts — List / Create / Edit / View."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit.actions.action import DeleteAction, EditAction, ViewAction
from almasix.orbit.forms.walk import iter_fields
from almasix.orbit.panels.content_width import resolve_content_max_width
from almasix.orbit.panels.page import Page
from almasix.orbit.support.conduit_attrs import conduit_attr
from almasix.orbit.support.html import e

# Narrower default for create/edit/view so forms/infolists read comfortably.
DEFAULT_FORM_CONTENT_MAX_WIDTH = "screen-lg"


def _resource_width_style(resource: type[Any], *, operation: str | None = None) -> str:
    raw = getattr(resource, "content_max_width", None)
    if operation in {"create", "edit", "view"}:
        form_raw = getattr(resource, "form_content_max_width", None)
        if form_raw:
            raw = form_raw
        elif not raw:
            raw = DEFAULT_FORM_CONTENT_MAX_WIDTH
    if not raw:
        return ""
    return f' style="max-width: {e(resolve_content_max_width(raw).css_value)}"'


def _auth_user() -> Any:
    try:
        from almasix.orbit.panels.routing import _current_user

        return _current_user()
    except Exception:
        return None


def _page_header_actions(resource: type[Any], operation: str, record: Any = None) -> str:
    """Filament-style header actions for view/edit.

    Shown by default like table row actions. When a permission API is present and
    denies the ability, the action is omitted.
    """
    user = _auth_user()
    mutable_fn = getattr(resource, "records_are_mutable", None)
    mutable = bool(mutable_fn()) if callable(mutable_fn) else bool(
        getattr(resource, "records_mutable", False)
    )

    def allowed(fn: Any) -> bool:
        # ``show`` only calls this when ``user`` is not None.
        try:
            return bool(fn(user, record))
        except TypeError:
            return bool(fn(user))

    # Prefer Resource.can_*; if Gate/auth denies everything (no policies), still
    # show chrome so panels work before policies are registered.
    def show(fn: Any) -> bool:
        if user is None:
            return True
        if allowed(fn):
            return True
        # Gate-backed User.can() returns False with no policy — fall open.
        can_fn = getattr(user, "can", None)
        if callable(can_fn) and not any(
            callable(getattr(user, attr, None))
            for attr in ("has_permission", "hasPermissionTo")
        ):
            perms = getattr(user, "permissions", None)
            if perms is None and not hasattr(user, "is_admin"):
                return True
        return False

    actions: list[Any] = []
    if operation == "view":
        if mutable and show(resource.can_update):
            actions.append(
                EditAction.make().url(lambda r=record, **_: resource.page_url("edit", r))
            )
        if mutable and show(resource.can_delete):
            actions.append(DeleteAction.make())
    elif operation == "edit":
        if show(resource.can_view):
            actions.append(
                ViewAction.make().url(lambda r=record, **_: resource.page_url("view", r))
            )
        if mutable and show(resource.can_delete):
            actions.append(DeleteAction.make())
    if not actions:
        return ""
    return (
        '<div class="or-page-actions">'
        + "".join(a.render(record=record) for a in actions)
        + "</div>"
    )


def _resource_is_mutable(resource: type[Any]) -> bool:
    mutable_fn = getattr(resource, "records_are_mutable", None)
    if callable(mutable_fn):
        return bool(mutable_fn())
    return bool(getattr(resource, "records_mutable", False))


def _record_id(record: Any) -> str:
    if record is None:
        return ""
    if isinstance(record, dict):
        return str(record.get("id", ""))
    return str(getattr(record, "id", "") or "")


def _hydrate_form_state(form: Any, record: Any) -> dict[str, Any]:
    data: dict[str, Any] = {}
    if record is None:
        return data
    for field in iter_fields(form.get_components()):
        name = field.get_state_path() or field.get_name()
        if not name:
            continue
        if isinstance(record, dict):
            if name in record:
                data[name] = record[name]
        else:
            data[name] = getattr(record, name, None)
    # Keep nested keys that aren't top-level fields (wizard bags, etc.).
    if isinstance(record, dict):
        for key, value in record.items():
            data.setdefault(key, value)
    return data


class Tab:
    """List-page filter tab."""

    def __init__(self, id: str, label: str | None = None) -> None:
        self.id = id
        self._label = label or id.replace("_", " ").title()
        self._icon: str | None = None
        self._badge: Any = None
        self._badge_color: str | None = None
        self._modify_query: Any = None

    def label(self, text: str) -> Tab:
        self._label = text
        return self

    def icon(self, name: str) -> Tab:
        self._icon = name
        return self

    def badge(self, value: Any) -> Tab:
        """Static value or callable evaluated at render time."""
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

    def resolve_badge(self, **ctx: Any) -> str | int | None:
        value = self._badge
        if callable(value):
            try:
                value = value(**ctx)
            except TypeError:
                value = value()
        if value is None:
            return None
        return value

    def render(self, *, active: bool = False, **ctx: Any) -> str:
        from almasix.orbit.support.icons import icon as render_icon

        active_cls = " is-active" if active else ""
        ic = render_icon(self._icon) if self._icon else ""
        badge = ""
        badge_value = self.resolve_badge(**ctx)
        if badge_value is not None:
            color = f" or-color-{e(self._badge_color)}" if self._badge_color else ""
            badge = f'<span class="or-list-tab-badge{color}">{e(badge_value)}</span>'
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
                '<div class="or-list-tabs-bar">'
                '<div class="or-list-tabs" role="tablist">'
                + "".join(t.render(active=(t.id == active), records=records) for t in tabs)
                + "</div></div>"
            )
            for t in tabs:
                if t.id == active and records is not None:
                    records = t.apply_query(records)
        table = resource.get_table()
        if records is not None:
            table.records(records)
        search = str(ctx.get("table_search") or "").strip()
        if search:
            table.search(search)
        sort = str(ctx.get("table_sort") or "").strip()
        if sort:
            direction = str(ctx.get("table_sort_direction") or "asc")
            table.sort(sort, direction)
        try:
            page = max(1, int(ctx.get("page") or 1))
        except (TypeError, ValueError):
            page = 1
        raw_per = ctx.get("per_page")
        try:
            if raw_per in (None, ""):
                per_page = 10
            else:
                per_page = int(raw_per)
                if per_page < 0:
                    per_page = 10
        except (TypeError, ValueError):
            per_page = 10
        filters = ctx.get("table_filters")
        if isinstance(filters, dict) and filters:
            table.filter_state(filters)
        table.paginate(page, per_page)
        header_actions = "".join(a.render(**ctx) for a in table._header_actions)
        width = _resource_width_style(resource, operation="list")
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
        if not _resource_is_mutable(resource):
            return (
                f'<div class="or-page or-page-create" data-resource="{e(resource.get_slug())}"'
                f"{_resource_width_style(resource, operation='create')}>"
                f'<header class="or-page-header">'
                f'<h1 class="or-page-title">Create {e(resource.get_navigation_label())}</h1>'
                f"</header>"
                f'<p class="or-muted">This demo resource uses a fixed seed list and cannot be changed.</p>'
                f"</div>"
            )
        form = resource.get_form()
        if state:
            form.fill(state)
        ctx = {**ctx, "resource": resource}
        if "model" not in ctx:
            try:
                ctx["model"] = resource.get_model()
            except Exception:
                ctx["model"] = getattr(resource, "model", None)
        return (
            f'<div class="or-page or-page-create" data-resource="{e(resource.get_slug())}"'
            f"{_resource_width_style(resource, operation='create')}>"
            f'<header class="or-page-header">'
            f'<h1 class="or-page-title">Create {e(resource.get_navigation_label())}</h1>'
            f"</header>"
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
        if not data and record is not None:
            data = _hydrate_form_state(form, record)
        if data:
            form.fill(data)
        record_id = _record_id(record)
        header_actions = _page_header_actions(resource, "edit", record)
        mutable = _resource_is_mutable(resource)
        ctx = {**ctx, "resource": resource}
        if "model" not in ctx:
            try:
                ctx["model"] = resource.get_model()
            except Exception:
                ctx["model"] = getattr(resource, "model", None)
        if not mutable:
            readonly = form.readonly() if hasattr(form, "readonly") else form
            return (
                f'<div class="or-page or-page-edit" data-resource="{e(resource.get_slug())}" '
                f'data-record="{e(record_id)}"{_resource_width_style(resource, operation="edit")}>'
                f'<header class="or-page-header">'
                f'<h1 class="or-page-title">{e(resource.get_navigation_label())}</h1>'
                f"{header_actions}</header>"
                f'<p class="or-muted">This demo resource uses a fixed seed list and cannot be changed.</p>'
                f"{readonly.render(data or form.get_state(), **ctx)}</div>"
            )
        return (
            f'<div class="or-page or-page-edit" data-resource="{e(resource.get_slug())}" '
            f'data-record="{e(record_id)}"{_resource_width_style(resource, operation="edit")}>'
            f'<header class="or-page-header">'
            f'<h1 class="or-page-title">Edit {e(resource.get_navigation_label())}</h1>'
            f"{header_actions}</header>"
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
        record_id = _record_id(record)
        header_actions = _page_header_actions(resource, "view", record)
        return (
            f'<div class="or-page or-page-view" data-resource="{e(resource.get_slug())}" '
            f'data-record="{e(record_id)}"{_resource_width_style(resource, operation="view")}>'
            f'<header class="or-page-header">'
            f'<h1 class="or-page-title">{e(resource.get_navigation_label())}</h1>'
            f"{header_actions}</header>"
            f"{infolist.render(record, **ctx)}</div>"
        )
