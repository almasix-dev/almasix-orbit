"""Drive almasix.orbit.forms statement + branch coverage to 100%."""

from __future__ import annotations

import builtins
from enum import Enum
from unittest import mock

from almasix.orbit.forms.components import (
    Block,
    Builder,
    DatePicker,
    Field,
    MoneyInput,
    MorphToSelect,
    RelationshipRepeater,
    Repeater,
    Select,
    Slider,
    TextInput,
    _flatten_options,
    _option_groups,
)
from almasix.orbit.forms.form import _check_rule
from almasix.orbit.forms.walk import iter_fields
from almasix.orbit.support.component import Component


class Color(Enum):
    RED = "red"
    BLUE = "blue"


def test_flatten_and_option_group_false_branches() -> None:
    # Sequence item with non-mapping options → skip update (32→29)
    assert _flatten_options([{"options": [1, 2, 3]}]) == {}
    # Mapping without options/value keys → skip (34→29)
    assert _flatten_options([{"label": "x"}, 42, "str"]) == {}
    # option_groups: mapping without options/value → skip (54→49)
    assert _option_groups([{"label": "orphan"}, "skip"]) == [(None, {})]


def test_field_fluent_and_chrome_gaps() -> None:
    assert TextInput.make("p").prohibited(False).get_rules() == []
    assert "unique:users" in TextInput.make("e").unique("users").get_rules()

    # enum TypeError path (275-276)
    real_issubclass = builtins.issubclass

    def _raise_for_enum(a: object, b: object) -> bool:
        if b is Enum:
            raise TypeError("forced")
        return real_issubclass(a, b)  # type: ignore[arg-type]

    builtins.issubclass = _raise_for_enum  # type: ignore[assignment]
    try:
        assert TextInput.make("e").enum(Color).get_options() == {}
    finally:
        builtins.issubclass = real_issubclass

    attrs = Field.make("a")._attrs_to_html(
        {"disabled": True, "hidden": False, "skip": None, "data-x": "1"}
    )
    assert "disabled" in attrs and "data-x=" in attrs and "hidden" not in attrs

    assert 'wire:model=""' in Field.make("x")._wire_binding("")
    assert 'wire:model="data.y"' in Field.make("x")._wire_binding("data.y")

    # hint without icon; hint without action
    hint_text = TextInput.make("a").hint("Net").render("1")
    assert "or-hint" in hint_text and "mountAction" not in hint_text
    hint_icon = TextInput.make("a").hint_icon("heroicon-o-home").render("1")
    assert "or-hint" in hint_icon and "mountAction" not in hint_icon

    # affix with only suffix (skip prefix span)
    suf = TextInput.make("a").suffix("USD").render("1")
    assert "or-input-suffix" in suf and "or-input-prefix" not in suf

    # after_state_updated callback without JS
    after = TextInput.make("a").after_state_updated(lambda **_: None).render("1")
    assert 'data-after-state-updated="true"' in after

    assert Field.make("h").hidden().render() == ""
    assert DatePicker.make("d").hidden().render() == ""

    # copyable alone adds x-ref (617)
    copy = TextInput.make("c").copyable().render("v")
    assert 'x-ref="input"' in copy and "data-copy" in copy

    # MoneyInput without locale (1324→1326)
    money = MoneyInput.make("amt").currency("USD").render(12)
    assert "or-field-MoneyInput" in money and "data-locale" not in money

    # Slider without pips (1748)
    slider = Slider.make("v").render(3)
    assert "or-slider" in slider and "data-pips" not in slider

    # options_limit break (754) — placeholder option may still appear
    limited = Select.make("s").options({"a": "A", "b": "B", "c": "C"}).options_limit(1).render("a")
    assert 'value="a"' in limited and 'value="b"' not in limited and 'value="c"' not in limited


def test_repeater_builder_relationship_morph_gaps() -> None:
    # empty list + default_items 0 → force [{}] (1541); deletable false (1574→1579)
    rep = (
        Repeater.make("r")
        .default_items(0)
        .deletable(False)
        .schema([TextInput.make("n")])
    )
    html = rep.render([])
    assert "or-repeater-item" in html
    assert "removeRepeaterItem" not in html

    # Builder count loop: non-dict / empty type (1687/1689 → 1686)
    builder = Builder.make("b").blocks([Block.make("h").schema([TextInput.make("t")])])
    assert "or-builder-picker" in builder.render(["x", {"type": ""}, {"block": ""}])

    # add_marker found but no preceding <button> (1722)
    with mock.patch.object(
        Repeater,
        "render",
        return_value='x wire:click="addRepeaterItem(\'b\')" y',
    ):
        out = Builder.render(builder, [{}])
        assert "or-builder-picker" in out

    # no add_marker and html does not end with </div> (1723→1725)
    with mock.patch.object(Repeater, "render", return_value="or-field-Repeater bare"):
        out2 = Builder.render(builder, [{}])
        assert out2.endswith("bare") or "or-builder-picker" in out2

    # RelationshipRepeater with relationship already set (1801→1803)
    rr = (
        RelationshipRepeater.make("items")
        .relationship("comments")
        .schema([TextInput.make("n")])
    )
    assert rr._relationship_name == "comments"
    assert "or-field-RelationshipRepeater" in rr.render([{}])

    # MorphToSelect mapping type without options (1888→1883)
    morph = MorphToSelect.make("m").types([{"type": "post", "label": "Post"}]).render()
    assert "or-field-MorphToSelect" in morph
    assert "Post" in morph


def test_walk_get_components_and_schema_edges() -> None:
    class HasComponents(Component):
        def __init__(self) -> None:
            super().__init__("hc")

        def get_components(self) -> list:
            return [TextInput.make("via_gc")]

    assert {f.get_name() for f in iter_fields([HasComponents()])} == {"via_gc"}

    class Blockish:
        pass

    class FieldWithBlocks(Field):
        def get_blocks(self) -> list:  # type: ignore[override]
            return [Blockish()]

        def get_schema(self) -> list:
            return []

    assert {f.get_name() for f in iter_fields([FieldWithBlocks.make("ff")])} == {"ff"}

    class EmptySchemaAttr(Component):
        def __init__(self) -> None:
            super().__init__("es")
            self._schema: list = []

    assert iter_fields([EmptySchemaAttr()]) == []


def test_validation_rule_false_branches() -> None:
    f = TextInput.make("v")
    # filled when non-empty (162)
    assert _check_rule("filled", "ok", "v", attr="v", field=f, state={}) is None
    # empty value short-circuits for json / ip / between / mimes
    assert _check_rule("json", None, "v", attr="v", field=f, state={}) is None
    assert _check_rule("json", "", "v", attr="v", field=f, state={}) is None
    assert _check_rule("ip", None, "v", attr="v", field=f, state={}) is None
    assert _check_rule("between:1,3", None, "v", attr="v", field=f, state={}) is None
    assert _check_rule("between:1,3", "", "v", attr="v", field=f, state={}) is None
    assert _check_rule("mimes:png", None, "v", attr="v", field=f, state={}) is None
    assert _check_rule("mimes:png", "", "v", attr="v", field=f, state={}) is None
    # max/min success paths for collections and numbers
    assert _check_rule("max:3", [1, 2], "v", attr="v", field=f, state={}) is None
    assert _check_rule("max:5", 3, "v", attr="v", field=f, state={}) is None
    assert _check_rule("min:2", [1, 2, 3], "v", attr="v", field=f, state={}) is None
    assert _check_rule("min:2", 5, "v", attr="v", field=f, state={}) is None
    # distinct when siblings missing / not a sequence (402→405)
    assert _check_rule("distinct", "x", "v", attr="v", field=f, state={}) is None
    assert _check_rule("distinct", "x", "v", attr="v", field=f, state={}, siblings="nope") is None
    assert _check_rule("distinct", "", "v", attr="v", field=f, state={}, siblings=["a"]) is None
