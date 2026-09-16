
"""Action objects — button + optional modal form + callback."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.html import e
from almasix.orbit.support.icons import icon as render_icon


class Action(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._action: Callable[..., Any] | None = None
        self._color: str = "primary"
        self._icon: str | None = None
        self._requires_confirmation = False
        self._modal_heading: str | None = None
        self._modal_description: str | None = None
        self._form_schema: list[Component] = []
        self._url: str | Callable[..., str] | None = None
        self._authorize: Callable[..., bool] | bool | None = None
        self._success_notification: str | None = None
        self._button_group: str = "default"

    def action(self, callback: Callable[..., Any]) -> Self:
        self._action = callback
        return self

    def get_action(self) -> Callable[..., Any] | None:
        return self._action

    def color(self, color: str) -> Self:
        self._color = color
        return self

    def icon(self, name: str) -> Self:
        self._icon = name
        return self

    def requires_confirmation(self, condition: bool = True) -> Self:
        self._requires_confirmation = condition
        return self

    def modal_heading(self, text: str) -> Self:
        self._modal_heading = text
        return self

    def modal_description(self, text: str) -> Self:
        self._modal_description = text
        return self

    def form(self, components: Sequence[Component]) -> Self:
        self._form_schema = list(components)
        return self

    def url(self, url: str | Callable[..., str]) -> Self:
        self._url = url
        return self

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
        return bool(auth(**ctx) if callable(auth) else auth)

    def call(self, *args: Any, **kwargs: Any) -> Any:
        if self._action is None:
            return None
        return self._action(*args, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update({
            "color": self._color,
            "icon": self._icon,
            "requires_confirmation": self._requires_confirmation,
            "modal_heading": self._modal_heading,
            "modal_description": self._modal_description,
            "has_form": bool(self._form_schema),
            "success_notification": self._success_notification,
        })
        return d

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx) or not self.can(**ctx):
            return ""
        name = e(self.get_name() or "action")
        label = e(self.get_label() or (self.get_name() or "Action").replace("_", " ").title())
        ic = render_icon(self._icon) if self._icon else ""
        color = e(self._color)
        confirm = "true" if self._requires_confirmation else "false"
        return (
            f'<button type="button" class="or-btn or-btn-{color}" data-action="{name}" '
            f'data-confirm="{confirm}" wire:click="mountAction(\'{name}\')">'
            f"{ic}<span>{label}</span></button>"
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


class DeleteBulkAction(DeleteAction):
    def __init__(self, name: str | None = "delete_bulk") -> None:
        super().__init__(name)
        self.label("Delete selected")
