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
from almasix.orbit.support.icons import icon as render_icon


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
        self._icon_button = False

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

    def icon_button(self, condition: bool = True) -> Self:
        """Filament-style icon-only trigger (e.g. row ⋮ menu)."""
        self._icon_button = condition
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
        icon_name = self.get_icon(**ctx)
        ic = render_icon(icon_name) if icon_name else ""
        if self._button_group_style:
            return (
                f'<div class="or-action-group or-btn-group" data-action-group="{name}" role="group">'
                f"{children}</div>"
            )
        btn_cls = f"or-btn or-btn-{e(self.get_color(**ctx))}"
        if self._icon_button:
            btn_cls += " or-btn-icon or-icon-btn"
            trigger_inner = ic or f"<span>{label}</span>"
            label_attr = f' aria-label="{label}"'
        else:
            trigger_inner = f"{ic}<span>{label}</span>"
            label_attr = ""
        menu_cls = "or-dropdown-menu"
        if self._icon_button:
            menu_cls += " or-dropdown-menu-end"
        return (
            f'<div class="or-action-group or-dropdown" data-action-group="{name}" '
            f'data-dropdown="true" x-data="orbitDropdown" @click.outside="closeMenu()">'
            f'<button type="button" class="{btn_cls}"{label_attr} '
            f'aria-haspopup="menu" @click="toggleMenu($event)" '
            f':aria-expanded="menuOpen.toString()">'
            f"{trigger_inner}</button>"
            f'<div class="{menu_cls}" role="menu" x-show="menuOpen" x-cloak>'
            f"{children}</div></div>"
        )


class BulkActionGroup(ActionGroup):
    """Filament-named bulk actions dropdown (alias of ``ActionGroup``)."""

    def __init__(self, name: str | None = "bulk_actions") -> None:
        super().__init__(name)
        self.label("Bulk actions").icon("heroicon-o-ellipsis-vertical").color("gray")


__all__ = [
    "ActionGroup",
    "BulkActionGroup",
    "ExportAction",
    "ForceDeleteAction",
    "ForceDeleteBulkAction",
    "ImportAction",
    "ReplicateAction",
    "RestoreAction",
    "RestoreBulkAction",
]
