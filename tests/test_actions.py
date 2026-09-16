"""Tests for almasix.orbit.actions."""

from __future__ import annotations

from almasix.orbit.actions.action import (
    Action,
    CreateAction,
    DeleteAction,
    DeleteBulkAction,
    EditAction,
    ViewAction,
)
from almasix.orbit.forms.components import TextInput


def test_action_authorize_call_and_render() -> None:
    called: list[int] = []
    action = (
        Action.make("save")
        .label("Save")
        .color("primary")
        .icon("heroicon-o-check")
        .requires_confirmation()
        .modal_heading("Confirm")
        .modal_description("Sure?")
        .form([TextInput.make("reason")])
        .url("/go")
        .authorize(lambda user=None: user == "admin")
        .success_notification("Saved")
        .action(lambda *a, **k: called.append(1) or "ok")
    )
    assert not action.can(user="guest")
    assert action.can(user="admin")
    assert action.call() == "ok"
    assert called == [1]
    assert Action.make("noop").get_action() is None
    assert action.get_action() is not None
    assert Action.make("open").authorize(True).can()
    assert not Action.make("closed").authorize(False).can()
    d = action.to_dict()
    assert d["requires_confirmation"] is True
    assert d["has_form"] is True
    html = action.render(user="admin")
    assert "or-btn-primary" in html and "data-confirm=\"true\"" in html
    assert action.render(user="guest") == ""
    assert Action.make("h").hidden().render() == ""
    assert Action.make("noicon").label("X").render()  # no icon branch


def test_preset_actions() -> None:
    create = CreateAction.make()
    assert create.get_label() == "Create"
    assert create._color == "primary"
    edit = EditAction.make()
    assert edit.get_label() == "Edit"
    view = ViewAction.make()
    assert view._color == "gray"
    delete = DeleteAction.make()
    assert delete._requires_confirmation is True
    assert delete._color == "danger"
    bulk = DeleteBulkAction.make()
    assert bulk.get_label() == "Delete selected"
    assert "or-btn" in create.render()
