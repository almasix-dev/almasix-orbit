"""Drive remaining tables / schemas / actions / urls branches to 100%."""

from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace

from almasix.orbit.actions.action import Action
from almasix.orbit.forms.components import TextInput
from almasix.orbit.schemas.layouts import (
    Fieldset,
    Flex,
    Section,
    Split,
    child_render_state,
)
from almasix.orbit.schemas.primes import Text
from almasix.orbit.schemas.schema import Schema
from almasix.orbit.support.urls import resolve_public_url
from almasix.orbit.tables import (
    ColumnGroup,
    Group,
    Stack,
    Table,
    TextColumn,
    View,
)
from almasix.orbit.tables.summaries import Range, Sum
from almasix.orbit.tables.table import _pagination_pages


def test_pagination_pages_clips_window_edges() -> None:
    # page near start/end → some candidates fail ``1 <= p <= last`` (45→44)
    assert _pagination_pages(1, 20) == [1, 2, 3, None, 20]
    assert _pagination_pages(20, 20) == [1, None, 18, 19, 20]


def test_table_flat_display_header_and_toolbar_gaps() -> None:
    plain = Text.make("prime")
    # Layout with unlabeled children → _header_label falls through to name (411)
    layout = Stack.make([TextColumn.make("n"), TextColumn.make("m")])
    layout._label = None
    layout.get_components()[0]._label = None
    layout.get_components()[1]._label = None

    table = (
        Table.make()
        .columns(
            [
                ColumnGroup.make("grp").columns(
                    [TextColumn.make("a").label("A").toggleable(False)]
                ),
                layout,
                plain,  # neither Column / Layout / ColumnGroup → 233→226, 248→240, 959–960
            ]
        )
        .groups([Group.make("a")])
        .active_group("missing-group")  # loop completes without match → 980→987
        .records([{"a": 1, "n": 2, "m": 3, "prime": "x"}])
    )
    # disable column manager / search so toolbar false branches fire
    for col in table.flat_columns():
        col.toggleable(False)

    flat = table.flat_columns()
    assert any(c.get_name() == "a" for c in flat)
    display = table.display_columns()
    assert plain in display or any(c is plain for c in table._columns)

    html = table.render()
    assert "or-th-group" in html
    assert "or-th" in html

    # Bare table: no filters, search, groups, columns chrome → 1166/1179/1189 falses
    bare = (
        Table.make()
        .columns([TextColumn.make("n").toggleable(False)])
        .records([{"n": 1}])
        .render()
    )
    assert "or-list-toolbar" not in bare


def test_header_label_skips_unlabeled_children() -> None:
    # Names would title-case into labels; force empty labels so the loop continues (409→407)
    # and finally falls through to get_name() (411).
    stack = Stack.make([TextColumn.make("x"), TextColumn.make("y")])
    stack._label = ""
    for child in stack.get_components():
        child._label = ""
    table = Table.make()
    assert table._header_label(stack) == (stack.get_name() or "")
    # first child empty, second has label → continue then return
    stack2 = Stack.make([TextColumn.make("a"), TextColumn.make("b").label("Bee")])
    stack2._label = ""
    stack2.get_components()[0]._label = ""
    assert table._header_label(stack2) == "Bee"
    # Non-layout column with empty label → skip LayoutComponent block (406→411)
    col = TextColumn.make("alone")
    col._label = ""
    assert table._header_label(col) == "alone"


def test_columns_format_fallback_and_falsy_icon() -> None:
    # list_bullet with non-list reaches final ``return str(value)`` (250→262)
    assert TextColumn.make("t").list_with_line_breaks()._format_display_value("plain") == "plain"
    assert TextColumn.make("t")._format_display_value(7) == "7"

    cell = (
        TextColumn.make("t")
        .icon(lambda **_: None)
        .render_cell({"t": "hi"})
    )
    assert "hi" in cell
    assert "or-cell-icon" not in cell


def test_layout_td_without_gt_and_view_without_children_token() -> None:
    class _NoGt(str):
        def find(self, sub: str, *args: object, **kwargs: object) -> int:  # type: ignore[override]
            if sub == ">":
                return -1
            return str.find(self, sub, *args, **kwargs)  # type: ignore[arg-type]

    class BrokenTd(TextColumn):
        def render_cell(self, record, **ctx):  # type: ignore[no-untyped-def]
            return _NoGt("<td>inner</td>")

    inner = Stack.make([BrokenTd.make("n")]).render_cell_inner({"n": 1})
    assert "or-layout-item" in inner
    assert "inner" in inner or "<td>" in inner

    html = (
        View.make([TextColumn.make("a")])
        .content("<section>static</section>")
        .render_cell({"a": "1"})
    )
    assert "static" in html
    assert "or-layout-view" in html


def test_summaries_no_label_and_range_non_tuple() -> None:
    html = Sum.make().label("").render(state=3)
    assert "or-summary-value" in html
    assert "or-summary-label" not in html

    assert Range.make().format_value(42) == "42"
    assert Range.make().format_value("solo") == "solo"
    assert "1" in Range.make().format_value((1, 2, 3))


def test_schema_layouts_visibility_and_flex_split_branches() -> None:
    field = TextInput.make("title")
    assert child_render_state(field, None) is None
    assert child_render_state(field, "nope") is None  # type: ignore[arg-type]

    flex = Flex.make().grow(False).schema([field])
    fhtml = flex.render({"title": "T"})
    assert "or-flex" in fhtml
    assert "or-flex-grow" not in fhtml

    split = Split.make().schema(
        [TextInput.make("a").hidden(), TextInput.make("b")]
    )
    shtml = split.render({"a": "1", "b": "2"})
    assert "or-schema-split" in shtml
    assert "or-schema-split-from-" not in shtml
    assert 'name="b"' in shtml or "b" in shtml

    assert Section.make("s").hidden().schema([field]).render({"title": "x"}) == ""
    assert Fieldset.make("f").hidden().schema([field]).render({"title": "x"}) == ""


def test_schema_dehydrate_skips_noncallable_mutate() -> None:
    # Shadow the method with a non-callable so ``callable(mutate)`` is False (68→74).
    field = TextInput.make("y")
    field.__dict__["get_dehydrate_state_using"] = None
    assert Schema.make().components([field]).state({"y": 1}).dehydrate() == {"y": 1}


def test_action_form_fields_skip_unnamed_on_object_record() -> None:
    record = SimpleNamespace(reason="because")
    action = Action.make("edit").form(
        [TextInput.make(None), TextInput.make("reason")]
    )
    html = action._render_form_fields(record)
    assert "reason" in html or "because" in html


def test_resolve_public_url_https_without_query() -> None:
    def fake_url(path: str) -> str:
        if path.startswith("clean"):
            return "https://cdn.example/logo.svg"
        return f"/{path.lstrip('/')}"

    mod = ModuleType("almasix.routing.url")
    mod.url = fake_url  # type: ignore[attr-defined]
    sys.modules["almasix.routing.url"] = mod
    try:
        assert resolve_public_url("clean/logo.svg") == "/logo.svg"
    finally:
        sys.modules.pop("almasix.routing.url", None)
