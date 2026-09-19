"""Extra coverage for Filament-parity APIs (render paths, evaluate branches, nav layouts)."""

from __future__ import annotations

from typing import Any

from almasix.orbit.actions.action import Action, EditAction, ViewAction
from almasix.orbit.forms.components import (
    Builder,
    CheckboxList,
    CodeEditor,
    KeyValue,
    MarkdownEditor,
    ModalTableSelect,
    MorphToSelect,
    RelationshipRepeater,
    Repeater,
    RichEditor,
    TableSelect,
    TagsInput,
    TextInput,
    ToggleButtons,
    ViewField,
)
from almasix.orbit.forms.form import Form
from almasix.orbit.infolists.components import RepeatableEntry, TextEntry
from almasix.orbit.infolists.infolist import Infolist
from almasix.orbit.panels.navigation import (
    NavigationGroup,
    NavigationItem,
    build_menu_layout,
    resolve_active_path,
)
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource, _iter_fields
from almasix.orbit.query_builder.builder import (
    NumberConstraint,
    QueryBuilder,
    SelectConstraint,
    TextConstraint,
)
from almasix.orbit.schemas.layouts import Section, Tabs, Wizard
from almasix.orbit.support.component import Component
from almasix.orbit.support.evaluate import evaluate
from almasix.orbit.tables.columns import (
    CheckboxColumn,
    ColumnGroup,
    IconColumn,
    SelectColumn,
    TextColumn,
    TextInputColumn,
    ToggleColumn,
    ViewColumn,
)
from almasix.orbit.tables.filters import SelectFilter
from almasix.orbit.tables.table import Table


def test_evaluate_positional_and_fallback_paths() -> None:
    assert evaluate(lambda x: x * 2, 21) == 42
    assert evaluate(lambda x, *, flag: (x, flag), 1, flag=True) == (1, True)

    def needs_nothing() -> str:
        return "ok"

    assert evaluate(needs_nothing, extra=1) == "ok"

    class Weird:
        def __call__(self, *a: Any, **k: Any) -> Any:
            raise TypeError("nope")

    weird = Weird()
    assert evaluate(weird, 1, a=2) is weird
    assert evaluate(weird) is weird

    # Builtins / C callables may reject inspect.signature — still evaluate.
    assert evaluate(len, [1, 2, 3]) == 3

    from unittest.mock import patch

    with patch("almasix.orbit.support.evaluate.inspect.signature", side_effect=ValueError("nope")):
        assert evaluate(lambda **kw: kw.get("record"), record="ok", noise=1) == "ok"
    with patch("almasix.orbit.support.evaluate.inspect.signature", side_effect=TypeError("nope")):
        assert evaluate(lambda **kw: kw.get("a"), a=2) == 2


def test_component_hint_helpers() -> None:
    bare = Component.make("x")
    assert bare.get_hint() is None
    assert bare.get_hint_icon() is None
    c = (
        Component.make("y")
        .hint(lambda **_: "tip")
        .hint_icon(lambda **_: "heroicon-o-information-circle")
    )
    assert c.get_hint() == "tip"
    assert c.get_hint_icon() == "heroicon-o-information-circle"
    assert Component.make("z").hint(lambda **_: None).get_hint() is None
    assert Component.make("w").hint_icon(lambda **_: None).get_hint_icon() is None


def test_form_field_readonly_placeholder_and_callable_rules() -> None:
    f = TextInput.make("name").readonly().placeholder(lambda **_: None)
    assert f.is_readonly()
    assert f.get_placeholder() is None
    assert TextInput.make("p").placeholder(lambda **_: "Pick").get_placeholder() == "Pick"

    form = Form.make().readonly().schema(
        [
            TextInput.make("a").rules(lambda value, **_: True),
            TextInput.make("b").rules(lambda value, **_: False),
            TextInput.make("c").rules(lambda value, **_: "bad c"),
            TextInput.make("d").rules(123),  # type: ignore[arg-type]
            TextInput.make("e").rules(lambda: "always"),  # no-arg callable via evaluate fallback
        ]
    )
    assert form.is_readonly()
    errors = form.validate({"a": "x", "b": "x", "c": "x", "d": "x", "e": "x"})
    assert "a" not in errors
    assert "b" in errors and "invalid" in errors["b"][0]
    assert errors["c"] == ["bad c"]
    assert "d" not in errors
    assert "e" in errors


def test_advanced_field_renders() -> None:
    assert "or-field-CheckboxList" in CheckboxList.make("roles").options({"a": "A"}).render(["a"])
    assert CheckboxList.make("h").hidden().render() == ""
    assert "or-tag" in TagsInput.make("tags").render(["x", "y"])
    assert "or-tags" in TagsInput.make("tags").render("one, two")
    assert TagsInput.make("h").hidden().render() == ""

    assert "or-editor-rich" in RichEditor.make("body").render("hi")
    assert "or-editor-markdown" in MarkdownEditor.make("md").render("# x")
    assert "or-editor-code" in CodeEditor.make("src").render("print(1)")

    assert "or-key-value-editor" in KeyValue.make("meta").render({"a": "1"})
    assert "Add row" in KeyValue.make("empty").render({})
    assert KeyValue.make("h").hidden().render() == ""

    rep = Repeater.make("items").schema([TextInput.make("name")])
    assert "or-repeater-item" in rep.render([{"name": "Ada"}])
    assert "Add item" in rep.render([])
    assert rep.hidden().render() == ""
    assert "or-field-Builder" in Builder.make("blocks").schema([TextInput.make("t")]).render([{}])
    assert "or-field-RelationshipRepeater" in (
        RelationshipRepeater.make("rels").schema([TextInput.make("n")]).render([{}])
    )

    tb = ToggleButtons.make("status").options({"a": "A", "b": "B"}).render("a")
    assert "or-toggle-buttons" in tb and "is-active" in tb
    assert ToggleButtons.make("h").hidden().render() == ""

    assert "or-view-field" in ViewField.make("info").content("<b>Hi</b>").render()
    assert "state" in ViewField.make("plain").render("state")
    assert ViewField.make("h").hidden().render() == ""

    assert "or-select-morph" in MorphToSelect.make("owner").options({"u": "User"}).render("u")
    assert "or-select-table" in TableSelect.make("post").options({"1": "P"}).render("1")
    assert "mountTableSelect" in ModalTableSelect.make("pick").render(3)
    assert ModalTableSelect.make("h").hidden().render() == ""


def test_table_inline_columns_groups_filters_and_urls() -> None:
    rec = {"icon": "heroicon-o-home", "status": "a", "on": True, "title": "T", "view": "X"}
    assert "<svg" in IconColumn.make("icon").render_cell(rec)
    sel = SelectColumn.make("status").options({"a": "A", "b": "B"}).render_cell(rec)
    assert "<select" in sel and "selected" in sel
    assert SelectColumn.make("status").options(lambda **_: "bad").render_cell(rec)  # type: ignore[arg-type]
    assert "checked" in CheckboxColumn.make("on").render_cell(rec)
    assert 'value="T"' in TextInputColumn.make("title").render_cell(rec)
    assert "or-toggle" in ToggleColumn.make("on").render_cell(rec)
    assert "or-view-column" in ViewColumn.make("view").render_cell(rec)
    assert "custom" in ViewColumn.make("view").content(lambda **_: "custom").render_cell(rec)
    assert ColumnGroup.make("g").columns([TextColumn.make("title")]).get_columns()[0].get_name() == "title"

    f = SelectFilter.make("status").options(lambda **_: {"a": "A"}).query(
        lambda q, v: [r for r in q if r["status"] == v]
    )
    assert f.get_options() == {"a": "A"}
    table = (
        Table.make()
        .columns(
            [
                ColumnGroup.make("meta")
                .label("Meta")
                .columns([TextColumn.make("title"), TextColumn.make("status")]),
            ]
        )
        .filters([f])
        .filter_state({"status": "a"})
        .records([rec, {"icon": "", "status": "b", "on": False, "title": "Other", "view": None}])
        .record_url(lambda record, **_: f"/r/{record['title']}")
        .actions([EditAction.make().url(lambda record, **_: f"/edit/{record['title']}")])
    )
    html = table.render()
    assert "or-th-group" in html and "Meta" in html
    assert table.get_total() == 1
    assert len(table.get_records()) == 1
    assert table.flat_columns()


def test_infolist_repeatable_and_query_builder_render() -> None:
    rep = RepeatableEntry.make("items").schema([TextEntry.make("name")])
    html = rep.render(record={"items": [{"name": "Ada"}, {"name": "Bob"}]})
    assert "or-repeatable-item" in html and "Ada" in html
    empty = RepeatableEntry.make("items").schema([TextEntry.make("name")]).render(record={"items": []})
    assert "No items" in empty

    qb = (
        QueryBuilder.make()
        .constraints(
            [
                TextConstraint.make("name"),
                NumberConstraint.make("age"),
                SelectConstraint.make("role").options({"admin": "Admin"}),
            ]
        )
    )
    rendered = qb.render()
    assert "or-query-builder" in rendered and "or-qb-row" in rendered
    assert "<select" in rendered and "Admin" in rendered
    assert QueryBuilder.make().hidden().render() == ""


def test_action_modal_url_and_call_none() -> None:
    link = ViewAction.make().url("/posts/1")
    assert 'href="/posts/1"' in link.render()
    modal = ViewAction.make().url("/posts/1").modal()
    assert modal.is_modal()
    assert "mountAction" in modal.render() and "href=" not in modal.render()
    assert Action.make("noop").call() is None
    colored = Action.make("go").label(lambda **_: "Go").color(lambda **_: "success").icon(
        lambda **_: "heroicon-o-check"
    )
    assert "or-btn-success" in colored.render()


def test_navigation_layouts_and_resolve_path() -> None:
    items = [
        {"label": "Posts", "url": "/admin/posts", "group": "Content", "subgroup": "Blog", "sort": 1, "icon": None},
        {"label": "Pages", "url": "/admin/pages", "group": "Content", "subgroup": "Blog", "sort": 2},
        {"label": "Reports", "url": "/admin/reports", "group": "Content", "sort": 3},
        {"label": "Users", "url": "/admin/users", "group": "People", "sort": 1, "icon": "heroicon-o-users"},
        {"label": "Home", "url": "/admin", "group": None, "sort": 0},
    ]
    meta = {
        "Content": NavigationGroup.make("Content").icon("heroicon-o-folder").sort(1).items(
            [NavigationItem.make("x").label("X").url("/x")]
        ),
        "People": NavigationGroup.make("People").sort(2),
    }
    split = build_menu_layout(items, group_meta=meta, active_path="/admin/posts", layout="sidebar_topbar")
    assert split.menu_roots and split.menu_secondary
    side = build_menu_layout(items, group_meta=meta, active_path="/admin/users", layout="sidebar")
    assert side.menu_roots and side.menu_secondary == []
    top = build_menu_layout(items, group_meta=meta, active_path="/admin", layout="top")
    assert top.menu_roots == [] and top.menu_secondary
    assert resolve_active_path("/x") == "/x"
    assert resolve_active_path(None) is None
    assert resolve_active_path(None, active_path=lambda **_: "/y") == "/y"

    panel = (
        Panel.make("admin")
        .path("admin")
        .navigation_layout("top")
        .navigation_items(
            [
                NavigationItem.make("dash").label("Dash").url("/admin").icon("heroicon-o-home").sort(0),
                NavigationItem.make("posts")
                .label("Posts")
                .url("/admin/posts")
                .group("Content")
                .subgroup("Blog")
                .sort(1),
            ]
        )
        .navigation_groups([NavigationGroup.make("Content").icon("heroicon-o-folder").sort(0)])
    )
    shell_top = panel.render_shell("x", active_path="/admin/posts")
    assert "or-app-top" in shell_top
    assert panel._render_sidebar(panel.menu_layout_context("/admin"), False) == ""

    side_panel = (
        Panel.make("admin")
        .path("admin")
        .navigation_layout("sidebar")
        .sidebar_collapsible()
        .navigation_items(
            [
                NavigationItem.make("a").label("A").url("/admin/a").group("G").sort(1),
                NavigationItem.make("b").label("B").url("/admin/b").group("G").sort(2),
                NavigationItem.make("c").label("C").url("/admin/c").sort(3),
            ]
        )
    )
    shell_side = side_panel.render_shell("x", active_path="/admin/a")
    assert "or-sidebar-collapse" in shell_side or "or-nav-group" in shell_side
    assert "or-nav-group" in shell_side


def test_resource_nested_fields_and_explicit_infolist() -> None:
    class NestedResource(Resource):
        model = type("M", (), {"id": 1})

        @classmethod
        def form(cls, form: Form) -> Form:
            return form.schema(
                [
                    Section.make("main").schema([TextInput.make("title")]),
                    Tabs.make("tabs").tabs(("Meta", [TextInput.make("slug")])),
                    Wizard.make("wiz").steps(("One", [TextInput.make("body")])),
                    type("HasSchema", (), {"_schema": [TextInput.make("extra")], "get_name": lambda self: None})(),
                ]
            )

        @classmethod
        def infolist(cls, infolist: Infolist) -> Infolist:
            return infolist.schema([TextEntry.make("title")])

    names = [f.get_name() for f in _iter_fields(NestedResource.get_form().get_components())]
    assert "title" in names and "slug" in names and "body" in names and "extra" in names
    assert NestedResource.get_infolist().get_components()[0].get_name() == "title"
    assert NestedResource.page_url("view", {"id": 9}) == "/nesteds/9"
    assert NestedResource.page_url("edit", type("R", (), {"id": 3})()) == "/nesteds/3/edit"
    assert NestedResource.page_url("missing") == ""
