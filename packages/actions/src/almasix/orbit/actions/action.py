"""Action objects — button + optional modal form + callback."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.evaluate import evaluate
from almasix.orbit.support.html import e
from almasix.orbit.support.icons import icon as render_icon


class Action(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._action: Callable[..., Any] | None = None
        self._color: str | Callable[..., str] = "primary"
        self._icon: str | Callable[..., str] | None = None
        self._requires_confirmation = False
        self._confirmation_forced_off = False
        self._modal_heading: str | Callable[..., str] | None = None
        self._modal_description: str | Callable[..., str] | None = None
        self._form_schema: list[Component] = []
        self._url: str | Callable[..., str] | None = None
        self._authorize: Callable[..., bool] | bool | None = None
        self._success_notification: str | None = None
        self._button_group: str = "default"
        self._modal = False
        self._slide_over = False
        self._modal_width: str | Callable[..., str] | None = None

    def action(self, callback: Callable[..., Any]) -> Self:
        self._action = callback
        return self

    def get_action(self) -> Callable[..., Any] | None:
        return self._action

    def color(self, color: str | Callable[..., str]) -> Self:
        self._color = color
        return self

    def get_color(self, **ctx: Any) -> str:
        result = evaluate(self._color, **ctx)
        return "primary" if result is None else str(result)

    def icon(self, name: str | Callable[..., str]) -> Self:
        self._icon = name
        return self

    def get_icon(self, **ctx: Any) -> str | None:
        if self._icon is None:
            return None
        result = evaluate(self._icon, **ctx)
        return None if result is None else str(result)

    def requires_confirmation(self, condition: bool = True) -> Self:
        self._requires_confirmation = condition
        if condition:
            self._confirmation_forced_off = False
        return self

    def without_confirmation(self, condition: bool = True) -> Self:
        """Explicit opt-out — danger actions confirm by default otherwise."""
        self._confirmation_forced_off = condition
        if condition:
            self._requires_confirmation = False
        return self

    def needs_confirmation(self, **ctx: Any) -> bool:
        if self._confirmation_forced_off:
            return False
        if self._requires_confirmation:
            return True
        return self.get_color(**ctx) == "danger"

    def modal(self, condition: bool = True) -> Self:
        """Prefer modal/quick action over URL navigation when both apply."""
        self._modal = condition
        return self

    def is_modal(self) -> bool:
        return (
            self._modal
            or bool(self._form_schema)
            or self._requires_confirmation
            or (not self._confirmation_forced_off and self._color == "danger")
        )

    def slide_over(self, condition: bool = True) -> Self:
        self._slide_over = condition
        self._modal = condition or self._modal
        return self

    def is_slide_over(self) -> bool:
        return self._slide_over

    def modal_width(self, width: str | Callable[..., str]) -> Self:
        self._modal_width = width
        return self

    def get_modal_width(self, **ctx: Any) -> str | None:
        if self._modal_width is None:
            return None
        result = evaluate(self._modal_width, **ctx)
        return None if result is None else str(result)

    def modal_heading(self, text: str | Callable[..., str]) -> Self:
        self._modal_heading = text
        return self

    def modal_description(self, text: str | Callable[..., str]) -> Self:
        self._modal_description = text
        return self

    def form(self, components: Sequence[Component]) -> Self:
        self._form_schema = list(components)
        return self

    def get_form_schema(self) -> list[Component]:
        return list(self._form_schema)

    def url(self, url: str | Callable[..., str]) -> Self:
        self._url = url
        return self

    def get_url(self, **ctx: Any) -> str | None:
        if self._url is None:
            return None
        result = evaluate(self._url, **ctx)
        return None if result is None else str(result)

    def authorize(self, callback: Callable[..., bool] | bool) -> Self:
        self._authorize = callback
        return self

    def success_notification(self, message: str) -> Self:
        self._success_notification = message
        return self

    def can(self, **ctx: Any) -> bool:
        auth = self._authorize
        if auth is None:
            return True
        return bool(evaluate(auth, **ctx))

    def call(self, *args: Any, **kwargs: Any) -> Any:
        if self._action is None:
            return None
        return self._action(*args, **kwargs)

    def _render_form_fields(self, record: Any | None = None, **ctx: Any) -> str:
        if not self._form_schema:
            return ""
        parts: list[str] = []
        state: dict[str, Any] = {}
        if isinstance(record, dict):
            state = dict(record)
        elif record is not None:
            for field in self._form_schema:
                fname = field.get_name()
                if fname:
                    state[fname] = getattr(record, fname, None)
        for field in self._form_schema:
            fname = field.get_name() or ""
            value = state.get(fname) if fname else None
            parts.append(field.render(value, record=record, **{k: v for k, v in ctx.items() if k != "state"}))
        return "".join(parts)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update({
            "color": self._color if not callable(self._color) else None,
            "icon": self._icon if not callable(self._icon) else None,
            "requires_confirmation": self._requires_confirmation,
            "modal": self._modal,
            "modal_heading": self._modal_heading if not callable(self._modal_heading) else None,
            "modal_description": self._modal_description if not callable(self._modal_description) else None,
            "has_form": bool(self._form_schema),
            "success_notification": self._success_notification,
            "has_url": self._url is not None,
            "slide_over": self._slide_over,
            "modal_width": self._modal_width if not callable(self._modal_width) else None,
        })
        return d

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx) or not self.can(**ctx):
            return ""
        record = ctx.get("record", state if isinstance(state, dict) else None)
        name = e(self.get_name() or "action")
        label = e(self.get_label(**ctx) or (self.get_name() or "Action").replace("_", " ").title())
        icon_name = self.get_icon(**ctx)
        ic = render_icon(icon_name) if icon_name else ""
        color = e(self.get_color(**ctx))
        needs_confirm = self.needs_confirmation(**ctx)
        has_form = bool(self._form_schema)
        use_modal = self._modal or has_form or needs_confirm
        href = None if use_modal else self.get_url(**ctx)
        if href:
            return (
                f'<a class="or-btn or-btn-{color}" data-action="{name}" href="{e(href)}">'
                f"{ic}<span>{label}</span></a>"
            )
        confirm = "true" if needs_confirm else "false"
        heading = ""
        if self._modal_heading:
            heading = str(evaluate(self._modal_heading, **ctx) or "")
        elif needs_confirm and not has_form:
            heading = f"{label}?"
        description = ""
        if self._modal_description:
            description = str(evaluate(self._modal_description, **ctx) or "")
        elif needs_confirm and not has_form and color == "danger":
            description = "This action cannot be undone."
        heading_attr = f' data-modal-heading="{e(heading)}"' if heading else ""
        desc_attr = f' data-modal-description="{e(description)}"' if description else ""
        slide_attr = ' data-slide-over="true"' if self._slide_over else ""
        width = self.get_modal_width(**ctx)
        width_attr = f' data-modal-width="{e(width)}"' if width else ""
        has_form_attr = ' data-has-form="true"' if has_form else ""
        rid = ""
        if isinstance(record, dict) and record.get("id") is not None:
            rid = str(record.get("id"))
        elif record is not None and getattr(record, "id", None) is not None:
            rid = str(getattr(record, "id"))
        rid_attr = f' data-record-id="{e(rid)}"' if rid else ""
        form_tpl = ""
        if has_form:
            form_record = record if (isinstance(record, dict) or record is not None) else None
            fields = self._render_form_fields(form_record, **{k: v for k, v in ctx.items() if k != "record"})
            form_tpl = f'<template class="or-action-form-tpl">{fields}</template>'
        return (
            f'<button type="button" class="or-btn or-btn-{color}" data-action="{name}" '
            f'data-confirm="{confirm}"{has_form_attr}{rid_attr}{heading_attr}{desc_attr}'
            f"{slide_attr}{width_attr} "
            f'wire:click="mountAction(\'{name}\')">'
            f"{ic}<span>{label}</span></button>{form_tpl}"
        )


class CreateAction(Action):
    def __init__(self, name: str | None = "create") -> None:
        super().__init__(name)
        self.label("Create").icon("heroicon-o-plus").color("primary")


class EditAction(Action):
    def __init__(self, name: str | None = "edit") -> None:
        super().__init__(name)
        self.label("Edit").icon("heroicon-o-pencil-square").color("primary")


class ViewAction(Action):
    def __init__(self, name: str | None = "view") -> None:
        super().__init__(name)
        self.label("View").icon("heroicon-o-magnifying-glass").color("gray")


class DeleteAction(Action):
    def __init__(self, name: str | None = "delete") -> None:
        super().__init__(name)
        self.label("Delete").icon("heroicon-o-trash").color("danger").requires_confirmation()
        self.modal_heading("Delete?")
        self.modal_description("This permanently removes the record.")


class DeleteBulkAction(DeleteAction):
    def __init__(self, name: str | None = "delete_bulk") -> None:
        super().__init__(name)
        self.label("Delete selected")
        self.modal_heading("Delete selected?")
        self.modal_description("This permanently removes the selected records.")
