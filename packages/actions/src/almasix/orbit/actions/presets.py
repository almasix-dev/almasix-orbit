"""Additional action presets (Replicate, ForceDelete, Restore, groups).

Parent wiring:
- Package ``__init__.py`` re-exports these (no edits to locked ``action.py``).
- ``ActionGroup`` can be passed wherever action lists are accepted once the parent
  flattens or renders groups in table/header action slots.
- Import/Export live in ``import_export.py`` and are re-exported here for one presets surface.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Self

from almasix.orbit.actions.action import Action, BulkAction
from almasix.orbit.actions.import_export import ExportAction, ImportAction
from almasix.orbit.support.html import e
from almasix.orbit.support.icons import icon as render_icon


class ReplicateAction(Action):
    def __init__(self, name: str | None = "replicate") -> None:
        super().__init__(name)
        self.label("Replicate").icon("heroicon-o-plus").color("gray")
        self._exclude_attributes: list[str] = []
        self._replicate_using: Callable[..., Any] | None = None
        self._before_replica_saved: Callable[..., Any] | None = None
        self._after_replica_saved: Callable[..., Any] | None = None

    def exclude_attributes(self, names: Sequence[str]) -> Self:
        self._exclude_attributes = list(names)
        return self

    def get_exclude_attributes(self) -> list[str]:
        return list(self._exclude_attributes)

    def replicate_using(self, callback: Callable[..., Any]) -> Self:
        self._replicate_using = callback
        return self

    def before_replica_saved(self, callback: Callable[..., Any]) -> Self:
        self._before_replica_saved = callback
        return self

    def after_replica_saved(self, callback: Callable[..., Any]) -> Self:
        self._after_replica_saved = callback
        return self

    def _default_replica(self, record: Any) -> dict[str, Any]:
        excluded = set(self._exclude_attributes) | {"id"}
        if isinstance(record, dict):
            return {k: v for k, v in record.items() if k not in excluded}
        data: dict[str, Any] = {}
        for key, value in vars(record).items() if hasattr(record, "__dict__") else []:
            if key.startswith("_") or key in excluded:
                continue
            data[key] = value
        return data

    def call(self, *args: Any, **kwargs: Any) -> Any:
        record = kwargs.get("record")
        if record is None and args:
            record = args[0]
            args = args[1:]

        if record is None:
            return super().call(*args, **kwargs)

        if self._replicate_using is not None:
            rest = {k: v for k, v in kwargs.items() if k != "record"}
            replica = self._replicate_using(record, **rest)
        else:
            replica = self._default_replica(record)

        kwargs = {**kwargs, "record": record, "replica": replica}

        self._halted = False
        self._cancelled = False
        if self._before is not None:
            self._before(**kwargs)
        if self._halted or self._cancelled:
            return None

        if self._before_replica_saved is not None:
            self._before_replica_saved(**kwargs)
        if self._halted or self._cancelled:
            return None

        result: Any = None
        if self._using is not None:
            result = self._using(**kwargs)
        elif self._action is not None:
            result = self._action(**kwargs)

        if self._halted or self._cancelled:
            return result

        if self._after_replica_saved is not None:
            self._after_replica_saved(**kwargs)
        if self._halted or self._cancelled:
            return result

        if self._after is not None:
            self._after(**kwargs)
        return result

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["exclude_attributes"] = list(self._exclude_attributes)
        d["has_replicate_using"] = self._replicate_using is not None
        return d


class ForceDeleteAction(Action):
    def __init__(self, name: str | None = "force_delete") -> None:
        super().__init__(name)
        self.label("Force delete").icon("heroicon-o-trash").color("danger").requires_confirmation()
        self.modal_heading("Force delete?")
        self.modal_description("This permanently removes the record and cannot be undone.")


class ForceDeleteBulkAction(BulkAction):
    def __init__(self, name: str | None = "force_delete_bulk") -> None:
        super().__init__(name)
        self.label("Force delete selected").icon("heroicon-o-trash").color("danger").requires_confirmation()
        self.modal_heading("Force delete selected?")
        self.modal_description("This permanently removes the selected records and cannot be undone.")


class RestoreAction(Action):
    def __init__(self, name: str | None = "restore") -> None:
        super().__init__(name)
        self.label("Restore").icon("heroicon-o-check").color("success")
        self.requires_confirmation()
        self.modal_heading("Restore?")
        self.modal_description("Restore this soft-deleted record.")


class RestoreBulkAction(BulkAction):
    def __init__(self, name: str | None = "restore_bulk") -> None:
        super().__init__(name)
        self.label("Restore selected").icon("heroicon-o-check").color("success")
        self.requires_confirmation()
        self.modal_heading("Restore selected?")
        self.modal_description("Restore the selected soft-deleted records.")


class ActionGroup(Action):
    """Dropdown / button group wrapping nested actions."""

    def __init__(self, name: str | None = "actions") -> None:
        super().__init__(name)
        self.label("Actions").icon("heroicon-o-cog-6-tooth").color("gray")
        self._actions: list[Action] = []
        self._dropdown = True
        self._button_group_style = False
        self._dropdown_placement: str | None = None
        self._dropdown_width: str | None = None
        self._dropdown_offset: int | None = None
        self._dropdown_max_height: str | int | None = None

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

    def dropdown_placement(self, placement: str) -> Self:
        self._dropdown_placement = placement
        return self

    def dropdown_width(self, width: str) -> Self:
        self._dropdown_width = width
        return self

    def dropdown_offset(self, offset: int) -> Self:
        self._dropdown_offset = offset
        return self

    def dropdown_max_height(self, height: str | int) -> Self:
        self._dropdown_max_height = height
        return self

    def flat_actions(self) -> list[Action]:
        out: list[Action] = []
        for action in self._actions:
            if isinstance(action, ActionGroup):
                out.extend(action.flat_actions())
            else:
                out.append(action)
        return out

    def _dropdown_data_attrs(self) -> str:
        parts: list[str] = []
        if self._dropdown_placement:
            parts.append(f' data-dropdown-placement="{e(self._dropdown_placement)}"')
        if self._dropdown_width:
            parts.append(f' data-dropdown-width="{e(self._dropdown_width)}"')
        if self._dropdown_offset is not None:
            parts.append(f' data-dropdown-offset="{e(self._dropdown_offset)}"')
        if self._dropdown_max_height is not None:
            parts.append(f' data-dropdown-max-height="{e(self._dropdown_max_height)}"')
        return "".join(parts)

    def _render_section_children(self, state: Any = None, **ctx: Any) -> str:
        """Non-dropdown nested groups become labeled sections."""
        parts: list[str] = []
        for action in self._actions:
            if isinstance(action, ActionGroup) and not action._dropdown:
                label = e(action.get_label(**ctx) or action.get_name() or "Section")
                inner = "".join(a.render(state, **ctx) for a in action._actions)
                if not inner.strip():
                    continue
                parts.append(
                    f'<div class="or-action-section" role="group" aria-label="{label}">'
                    f'<div class="or-action-section-label">{label}</div>{inner}</div>'
                )
            else:
                parts.append(action.render(state, **ctx))
        return "".join(parts)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "actions": [a.to_dict() for a in self._actions],
                "dropdown": self._dropdown,
                "button_group": self._button_group_style,
                "dropdown_placement": self._dropdown_placement,
                "dropdown_width": self._dropdown_width,
                "dropdown_offset": self._dropdown_offset,
                "dropdown_max_height": self._dropdown_max_height,
            }
        )
        return d

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx) or not self.can(**ctx):
            return ""
        if self._button_group_style or not self._dropdown:
            children = self._render_section_children(state, **ctx)
            if not children.strip():
                return ""
            name = e(self.get_name() or "actions")
            return (
                f'<div class="or-action-group or-btn-group" data-action-group="{name}" role="group">'
                f"{children}</div>"
            )

        children = "".join(a.render(state, **ctx) for a in self._actions)
        if not children.strip():
            return ""
        name = e(self.get_name() or "actions")
        label = e(self.get_label(**ctx) or "Actions")
        icon_name = self.get_icon(**ctx)
        ic = render_icon(icon_name) if icon_name else ""
        color = e(self.get_color(**ctx))
        style = self.get_trigger_style()
        # Honor legacy icon_button() which sets _trigger_style, plus button/link
        btn_cls = f"or-btn or-btn-{color} or-btn-{e(self.get_size())}"
        if style == "link":
            btn_cls += " or-btn-link"
        elif style == "icon_button":
            btn_cls += " or-btn-icon or-icon-btn"
        elif style == "badge":
            btn_cls += " or-btn-badge or-badge"
        if self._outlined:
            btn_cls += " or-btn-outlined"
        tip = self.get_tooltip(**ctx)
        tip_attr = f' title="{e(tip)}"' if tip else ""
        icon_only = style == "icon_button"
        if icon_only:
            trigger_inner = ic or f"<span>{label}</span>"
            label_attr = f' aria-label="{label}"'
        elif self._icon_position == "after":
            trigger_inner = f"<span>{label}</span>{ic}"
            label_attr = ""
        else:
            trigger_inner = f"{ic}<span>{label}</span>"
            label_attr = ""
        menu_cls = "or-dropdown-menu"
        if icon_only:
            menu_cls += " or-dropdown-menu-end"
        dropdown_attrs = self._dropdown_data_attrs()
        return (
            f'<div class="or-action-group or-dropdown" data-action-group="{name}" '
            f'data-dropdown="true"{dropdown_attrs} x-data="orbitDropdown" '
            f'@click.outside="closeMenu()">'
            f'<button type="button" class="{btn_cls}"{label_attr}{tip_attr} '
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
