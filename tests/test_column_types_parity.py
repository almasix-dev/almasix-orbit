"""Column type depth, editable host, danger confirm, grouping, modal forms."""

from __future__ import annotations

from almasix.orbit.actions.action import Action, CreateAction, DeleteAction, EditAction
from almasix.orbit.forms.components import Select, TextInput
from almasix.orbit.tables import (
    BooleanColumn,
    CheckboxColumn,
    ColorColumn,
    ColumnGroup,
    Grid,
    Group,
    IconColumn,
    ImageColumn,
    Panel,
    SelectColumn,
    Split,
    Stack,
    Table,
    TagsColumn,
    TextColumn,
    TextInputColumn,
    ToggleColumn,
    View,
    ViewColumn,
)


def test_layout_grid_and_view_render() -> None:
    rec = {"a": "1", "b": "2"}
    grid = Grid.make([TextColumn.make("a"), TextColumn.make("b")]).columns(2)
    assert "or-layout-grid" in grid.render_cell(rec)
    assert "or-cols-2" in grid.render_cell(rec)
    view = View.make([TextColumn.make("a")]).content("<section>{children}</section>")
    html = view.render_cell(rec)
    assert "or-layout-view" in html
    assert "<section>" in html


def test_text_column_copyable_weight_wrap_markdown_icon() -> None:
    rec = {"title": "Hello **world**"}
    html = (
        TextColumn.make("title")
        .copyable()
        .weight("bold")
        .wrap()
        .markdown()
        .icon("heroicon-o-star")
        .render_cell(rec)
    )
    assert "or-copyable" in html
    assert "or-font-bold" in html
    assert "or-cell-wrap" in html
    assert "<strong>" in html
    assert "or-cell-icon" in html


def test_icon_boolean_and_image_options() -> None:
    assert "or-color-success" in BooleanColumn.make("on").render_cell({"on": True})
    assert "or-color-danger" in IconColumn.make("on").boolean().render_cell({"on": False})
    img = (
        ImageColumn.make("avatars")
        .circular()
        .stacked()
        .limit(1)
        .size(32)
        .render_cell({"avatars": ["http://a", "http://b"]})
    )
    assert "or-avatar-stack" in img
    assert "or-avatar-circle" in img
    assert "+1" in img


def test_color_copyable_and_editable_attrs() -> None:
    assert "or-copyable" in ColorColumn.make("c").copyable().render_cell({"c": "#fff"})
    rec = {"id": 9, "status": "a", "title": "T", "on": True, "done": False}
    sel = SelectColumn.make("status").options({"a": "A"}).render_cell(rec)
    assert 'data-orbit-column-edit="select"' in sel
    assert 'data-record-id="9"' in sel
    assert "wire:model" not in sel
    assert 'data-orbit-column-edit="text"' in TextInputColumn.make("title").render_cell(rec)
    assert 'data-orbit-column-edit="toggle"' in ToggleColumn.make("on").render_cell(rec)
    assert 'data-orbit-column-edit="checkbox"' in CheckboxColumn.make("done").render_cell(rec)


def test_column_group_dual_header_and_filament_make() -> None:
    group = ColumnGroup.make("Meta", [TextColumn.make("a").label("A"), TextColumn.make("b").label("B")])
    html = (
        Table.make()
        .columns([TextColumn.make("title"), group])
        .records([{"title": "t", "a": "1", "b": "2"}])
        .render()
    )
    assert "or-tr-group-headers" in html
    assert "or-tr-column-headers" in html
    assert "Meta" in html


def test_grouped_rows_render_headers() -> None:
    html = (
        Table.make()
        .columns([TextColumn.make("title"), TextColumn.make("status")])
        .default_group(Group.make("status").collapsible())
        .records(
            [
                {"id": 1, "title": "A", "status": "draft"},
                {"id": 2, "title": "B", "status": "draft"},
                {"id": 3, "title": "C", "status": "published"},
            ]
        )
        .render()
    )
    assert "or-group-header" in html
    assert "or-group-member" in html
    assert "data-collapsible=\"true\"" in html


def test_danger_actions_always_confirm() -> None:
    delete = DeleteAction.make().render({"id": 1}, record={"id": 1})
    assert 'data-confirm="true"' in delete
    assert 'data-record-id="1"' in delete
    danger = Action.make("wipe").label("Wipe").color("danger").render()
    assert 'data-confirm="true"' in danger
    opted = Action.make("wipe").color("danger").without_confirmation().render()
    assert 'data-confirm="false"' in opted


def test_modal_form_action_embeds_template() -> None:
    action = (
        CreateAction.make()
        .modal()
        .modal_heading("New task")
        .form([TextInput.make("title"), Select.make("status").options({"a": "A"})])
    )
    html = action.render()
    assert 'data-has-form="true"' in html
    assert "or-action-form-tpl" in html
    assert 'name="title"' in html
    edit = (
        EditAction.make()
        .modal()
        .form([TextInput.make("title")])
        .render({"id": 3, "title": "Hi"}, record={"id": 3, "title": "Hi"})
    )
    assert 'data-record-id="3"' in edit
    assert "Hi" in edit


def test_list_host_update_column_and_delete() -> None:
    from almasix.orbit.panels.conduit.hosts import ListRecordsHost
    from almasix.orbit.panels.panel import Panel
    from almasix.orbit.panels.resource import Resource

    class Demo(Resource):
        model = type("X", (), {})
        records_mutable = True
        records = [
            {"id": 1, "title": "A", "status": "draft"},
            {"id": 2, "title": "B", "status": "draft"},
        ]

        @classmethod
        def get_records(cls):
            return list(cls.records)

        @classmethod
        def table(cls, table):
            return table.columns([TextColumn.make("title"), TextColumn.make("status")])

    panel = Panel.make("test-cols").path("/test-cols")
    Host = ListRecordsHost.bind(panel=panel, resource=Demo)
    host = Host()
    host.mount()
    host.update_column_state("1", "status", "published")
    assert host.records[0]["status"] == "published"
    host.mountAction("delete", record_id="1")
    assert [r["id"] for r in host.records] == [2]
    host.mountAction("create", data={"title": "C", "status": "todo"})
    assert any(r.get("title") == "C" for r in host.records)


def test_tags_split_stack_panel_view_column() -> None:
    rec = {"title": "T", "sub": "S", "tags": ["a", "b"], "note": "N"}
    assert "or-badge" in TagsColumn.make("tags").render_cell(rec)
    assert "or-split" in Split.make([TextColumn.make("title"), TextColumn.make("sub")]).render_cell(rec)
    assert "or-stack" in Stack.make([TextColumn.make("title")]).render_cell(rec)
    assert "or-panel" in Panel.make([TextColumn.make("note")]).render_cell(rec)
    assert "custom" in ViewColumn.make("note").content(lambda **_: "custom").render_cell(rec)
