"""Additional action presets (Replicate, ForceDelete, Restore, groups).

Parent wiring:
- Package ``__init__.py`` re-exports these (no edits to locked ``action.py``).
- ``ActionGroup`` can be passed wherever action lists are accepted once the parent
  flattens or renders groups in table/header action slots.
- Import/Export live in ``import_export.py`` and are re-exported here for one presets surface.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Self

from almasix.orbit.actions.action import Action
from almasix.orbit.actions.import_export import ExportAction, ImportAction
from almasix.orbit.support.html import e


class ReplicateAction(Action):
    def __init__(self, name: str | None = "replicate") -> None:
        super().__init__(name)
        self.label("Replicate").icon("heroicon-o-plus").color("gray")
        self._exclude_attributes: list[str] = []

    def exclude_attributes(self, names: Sequence[str]) -> Self:
        self._exclude_attributes = list(names)
        return self

    def get_exclude_attributes(self) -> list[str]:
        return list(self._exclude_attributes)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["exclude_attributes"] = list(self._exclude_attributes)
        return d


class ForceDeleteAction(Action):
    def __init__(self, name: str | None = "force_delete") -> None:
        super().__init__(name)
        self.label("Force delete").icon("heroicon-o-trash").color("danger").requires_confirmation()
        self.modal_heading("Force delete?")
        self.modal_description("This permanently removes the record and cannot be undone.")


class ForceDeleteBulkAction(ForceDeleteAction):
    def __init__(self, name: str | None = "force_delete_bulk") -> None:
        super().__init__(name)
        self.label("Force delete selected")


class RestoreAction(Action):
    def __init__(self, name: str | None = "restore") -> None:
        super().__init__(name)
        self.label("Restore").icon("heroicon-o-check").color("success")


class RestoreBulkAction(RestoreAction):
    def __init__(self, name: str | None = "restore_bulk") -> None:
        super().__init__(name)
        self.label("Restore selected")


class ActionGroup(Action):
    """Dropdown / button group wrapping nested actions."""

    def __init__(self, name: str | None = "actions") -> None:
        super().__init__(name)
        self.label("Actions").icon("heroicon-o-cog-6-tooth").color("gray")
        self._actions: list[Action] = []
        self._dropdown = True
        self._button_group_style = False

    @classmethod
    def make(cls, actions: Sequence[Action] | str | None = None) -> Self:  # type: ignore[override]
        if isinstance(actions, str) or actions is None:
            return cls(actions if isinstance(actions, str) else None)
        inst = cls(None)
        inst.actions(actions)
        return inst

    def actions(self, items: Sequence[Action]) -> Self:
        self._actions = list(items)
        return self

    def get_actions(self) -> list[Action]:
        return list(self._actions)

    def dropdown(self, condition: bool = True) -> Self:
        self._dropdown = condition
        self._button_group_style = not condition
        return self

    def button_group(self, condition: bool = True) -> Self:
        self._button_group_style = condition
        self._dropdown = not condition
        return self

    def flat_actions(self) -> list[Action]:
        out: list[Action] = []
        for action in self._actions:
            if isinstance(action, ActionGroup):
                out.extend(action.flat_actions())
            else:
                out.append(action)
        return out

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "actions": [a.to_dict() for a in self._actions],
                "dropdown": self._dropdown,
                "button_group": self._button_group_style,
            }
        )
        return d

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx) or not self.can(**ctx):
            return ""
        children = "".join(a.render(state, **ctx) for a in self._actions)
        if not children.strip():
            return ""
        name = e(self.get_name() or "actions")
        label = e(self.get_label(**ctx) or "Actions")
        if self._button_group_style:
            return (
                f'<div class="or-action-group or-btn-group" data-action-group="{name}" role="group">'
                f"{children}</div>"
            )
        return (
            f'<div class="or-action-group or-dropdown" data-action-group="{name}" '
            f'data-dropdown="true">'
            f'<button type="button" class="or-btn or-btn-{e(self.get_color(**ctx))}" '
            f'aria-haspopup="menu"><span>{label}</span></button>'
            f'<div class="or-dropdown-menu" role="menu">{children}</div></div>'
        )


__all__ = [
    "ActionGroup",
    "ExportAction",
    "ForceDeleteAction",
    "ForceDeleteBulkAction",
    "ImportAction",
    "ReplicateAction",
    "RestoreAction",
    "RestoreBulkAction",
]
