"""Exhaustive forms depth coverage — chrome, validation, nested walk, hosts."""

from __future__ import annotations

from enum import Enum

from almasix.orbit.forms import (
    Block,
    Builder,
    CodeEditor,
    FileUpload,
    Form,
    Repeater,
    Select,
    Slider,
    Textarea,
    TextInput,
    ToggleButtons,
)
from almasix.orbit.forms.walk import iter_fields
from almasix.orbit.schemas import Section, Tabs
from almasix.orbit.schemas.layouts import Flex
from almasix.orbit.support.component import Component


class Color(Enum):
    RED = "red"
    BLUE = "blue"


def test_nested_section_flex_render_keeps_field_state() -> None:
    """Layouts must receive the full state bag so nested fields populate."""
    form = (
        Form.make()
        .schema(
            [
                Section.make("basics")
                .heading("Basics")
                .schema(
                    [
                        Flex.make().schema(
                            [
                                TextInput.make("name").label("Name"),
                                Select.make("role").options({"a": "Admin"}).label("Role"),
                            ]
                        ),
                        Textarea.make("bio").label("Bio"),
                    ]
                ),
            ]
        )
        .fill({"name": "Ada", "role": "a", "bio": "Hello"})
    )
    html = form.render()
    assert 'value="Ada"' in html
    assert "Hello" in html
    assert "selected" in html or 'value="a"' in html

    form = (
        Form.make("post")
        .operation("create")
        .schema(
            [
                Section.make("meta").schema(
                    [
                        TextInput.make("title").required(),
                        TextInput.make("slug")
                        .rules("alpha_dash")
                        .dehydrate_state_using(lambda v, **_: (v or "").lower()),
                    ]
                ),
                Tabs.make().tabs(("More", [TextInput.make("body").min_length(3)])),
            ]
        )
    )
    form.fill({"title": "", "slug": "Hello_World", "body": "ab"})
    errors = form.validate()
    assert "title" in errors and "body" in errors
    assert form.get_operation() == "create"
    out = form.fill({"title": "T", "slug": "Hello_World", "body": "abcd"}).dehydrate()
    assert out["slug"] == "hello_world"
    fields = iter_fields(form.get_components())
    assert {f.get_name() for f in fields} >= {"title", "slug", "body"}


def test_field_chrome_prefix_hint_live_wire() -> None:
    field = (
        TextInput.make("amount")
        .label("Amount")
        .helper_text("USD")
        .hint("Net")
        .hint_icon("heroicon-o-home")
        .hint_action("help")
        .prefix("$")
        .suffix("USD")
        .prefix_icon("heroicon-o-home")
        .suffix_icon("heroicon-o-cog-6-tooth")
        .autocomplete("off")
        .autofocus()
        .input_mode("decimal")
        .step(0.01)
        .min_value(0)
        .max_value(100)
        .extra_input_attributes({"data-x": "1"})
        .extra_field_wrapper_attributes({"data-wrap": "y"})
        .extra_attributes({"data-extra": "z"})
        .after_state_updated(lambda **_: None)
        .after_state_updated_js("console.log(1)")
        .live(on_blur=True)
        .inline_label()
        .hidden_label()
        .saved(True)
        .unique("users", "email", ignore=1)
        .exists("posts", "id")
        .distinct()
        .regex(r"^\d+$")
        .between(1, 9)
        .revealable()
        .copyable()
        .mask("999")
        .datalist(["10", "20"])
        .password()
    )
    html = field.render("12")
    assert "or-hint" in html and "or-input-prefix" in html and "or-input-suffix" in html
    assert 'autocomplete="off"' in html and "autofocus" in html
    assert "wire:model.blur" in html
    assert "data-mask=" in html and "datalist" in html
    assert field.wire_model_directive() == "model.blur"
    assert TextInput.make("x").live(debounce=300).wire_model_directive() == "model.live.debounce.300ms"
    assert TextInput.make("x").live().wire_model_directive() == "model.live"
    assert Component.make("c").saved(False).is_dehydrated() is False


def test_validation_catalog_breadth() -> None:
    form = Form.make()
    cases = [
        ("nullable", None, True),
        ("filled", "", False),
        ("accepted", "yes", True),
        ("accepted", "no", False),
        ("boolean", "maybe", False),
        ("boolean", "true", True),
        ("array", [1], True),
        ("array", "x", False),
        ("json", '{"a":1}', True),
        ("json", "{", False),
        ("uuid", "550e8400-e29b-41d4-a716-446655440000", True),
        ("uuid", "nope", False),
        ("ip", "127.0.0.1", True),
        ("ip", "bad", False),
        ("alpha", "abc", True),
        ("alpha_num", "a1", True),
        ("alpha_dash", "a-1_b", True),
        ("digits:3", "123", True),
        ("digits:3", "12", False),
        ("between:2,4", "abc", True),
        ("between:2,4", 3, True),
        ("between:2,4", 9, False),
        ("gt:age", 20, True),
        ("gte:age", 18, True),
        ("lt:age", 10, True),
        ("lte:age", 18, True),
        ("different:other", "a", True),
        ("not_in:x,y", "z", True),
        ("not_in:x,y", "x", False),
        ("starts_with:http", "https://a", True),
        ("ends_with:.com", "a.com", True),
        ("regex:^a+$", "aaa", True),
        ("mimes:png,jpg", "photo.png", True),
        ("mimes:png", "doc.pdf", False),
        ("max:2", [1, 2, 3], False),
        ("min:2", [1], False),
        ("max:5", 6, False),
        ("min:5", 3, False),
        ("distinct", "dup", False),
    ]
    state = {"age": 18, "other": "b"}
    for rule, value, ok in cases:
        field = TextInput.make("v").rules(rule)
        form.schema([field]).fill({"v": value, **state})
        from almasix.orbit.forms.form import _check_rule

        msg = _check_rule(
            rule,
            value,
            "v",
            attr="v",
            field=field,
            state={**state, "v": value},
            siblings=["dup", "dup"] if rule == "distinct" else None,
        )
        if ok:
            assert msg is None, (rule, value, msg)
        else:
            assert msg is not None, (rule, value)


def test_unique_exists_with_checkers() -> None:
    Form.unique_using(lambda value, table, column, ignore=None, **_: value != "taken")
    Form.exists_using(lambda value, table, column, **_: value == "ok")
    form = Form.make().schema(
        [
            TextInput.make("email").rules("unique:users,email,9"),
            TextInput.make("ref").rules("exists:posts,id"),
        ]
    )
    assert form.fill({"email": "taken", "ref": "no"}).validate()
    assert not form.fill({"email": "free", "ref": "ok"}).validate()
    Form.unique_using(None)
    Form.exists_using(None)


def test_select_file_repeater_builder_depth_render() -> None:
    sel = (
        Select.make("role")
        .enum(Color)
        .searchable()
        .native(False)
        .options_limit(10)
        .allow_html()
        .search_prompt("Find…")
        .no_search_results_message("None")
        .loading_message("…")
        .searching_message("…")
        .search_debounce(150)
        .get_search_results_using(lambda **_: {})
        .get_option_label_using(lambda **_: "x")
        .create_option_using(lambda **_: None)
        .create_option_form(Form.make())
        .edit_option_action(True)
        .min_items(1)
        .max_items(3)
        .reorderable()
        .selectable_placeholder()
        .relationship("roles", "name", search_columns=["name"], preload=True)
    )
    assert "orbitSearchableSelect" in sel.render("red")
    assert "data-ajax-search" in sel.render()

    fu = (
        FileUpload.make("avatar")
        .disk("s3")
        .directory("avatars")
        .visibility("private")
        .downloadable()
        .openable()
        .previewable()
        .move_files()
        .store_files(False)
        .fetch_file_information(False)
        .preserve_filenames()
        .image_editor()
        .image_editor_aspect_ratios(["16:9", "1:1"])
        .max_files(3)
        .min_files(1)
        .panel_layout()
        .image_preview_height(120)
        .prevent_file_path_tampering()
        .avatar()
        .image_size(min_width=10, max_width=100, min_height=10, max_height=100)
        .min_size(1)
        .max_size(500)
    )
    html = fu.render()
    assert "data-image-editor" in html and "data-disk=" in html and "or-file-avatar" in html

    rep = (
        Repeater.make("members")
        .simple(TextInput.make("email").email())
        .default_items(2)
        .addable()
        .deletable()
        .add_action_label("Add member")
        .grid(2)
        .table(["Email"])
        .relationship("members")
        .cloneable()
        .collapsible()
        .reorderable()
        .item_label(lambda index, **_: f"#{index}")
        .min_items(1)
        .max_items(5)
        .mutate_relationship_data_before_create(lambda d, **_: {**d, "x": 1})
        .mutate_relationship_data_before_fill(lambda d, **_: d)
        .mutate_relationship_data_before_save(lambda d, **_: d)
    )
    assert "or-repeater-simple" in rep.render()
    assert rep.apply_mutate_before_create({})["x"] == 1
    assert rep.apply_mutate_before_fill({"a": 1}) == {"a": 1}
    assert rep.apply_mutate_before_save({"a": 1}) == {"a": 1}

    builder = (
        Builder.make("content")
        .blocks(
            [
                Block.make("heading").label("Heading").icon("heroicon-o-home").schema(
                    [TextInput.make("text")]
                ).max_items(2),
                Block.make("paragraph").schema([Textarea.make("body")]),
            ]
        )
        .block_picker_columns(2)
    )
    bhtml = builder.render([{"type": "heading", "text": "Hi"}, {"type": "paragraph", "body": "P"}])
    assert "or-builder-picker" in bhtml and "Heading" in bhtml

    assert "data-pips" in Slider.make("vol").pips().min_value(0).max_value(10).step(1).render(5)
    assert "data-language" in CodeEditor.make("src").language("python").render("x=1")
    assert "or-toggle-buttons" in ToggleButtons.make("s").options({"a": "A"}).render("a")
    assert "data-autosize" in Textarea.make("t").autosize().cols(40).render("hi")


def test_form_callable_rule_and_readonly() -> None:
    form = Form.make().readonly().schema(
        [TextInput.make("n").rules(lambda value, **_: False if value == "bad" else True)]
    )
    assert form.is_readonly()
    assert "n" in form.fill({"n": "bad"}).validate()
    assert form.fill({"n": "ok"}).validate() == {}
    # string message from callable
    form2 = Form.make().schema([TextInput.make("n").rules(lambda value, **_: "nope")])
    assert form2.fill({"n": "x"}).validate()["n"] == ["nope"]


def test_walk_wizard_blocks_and_schema_edges() -> None:
    from almasix.orbit.forms.components import RelationshipRepeater
    from almasix.orbit.schemas import Wizard
    from almasix.orbit.schemas.schema import Schema

    wiz = Wizard.make().steps(("One", [TextInput.make("a")]), ("Two", [TextInput.make("b")]))
    names = {f.get_name() for f in iter_fields([wiz])}
    assert names == {"a", "b"}

    builder = Builder.make("c").blocks(
        [Block.make("h").schema([TextInput.make("t")]), Block.make("p").schema([TextInput.make("u")])]
    )
    assert {f.get_name() for f in iter_fields([builder])} >= {"c", "t", "u"}

    # Layout with get_schema / _schema
    class Nested(Component):
        def __init__(self) -> None:
            super().__init__("nest")
            self._schema = [TextInput.make("nested")]

        def get_schema(self):
            return self._schema

    assert "nested" in {f.get_name() for f in iter_fields([Nested()])}

    # dehydrate skip undehyrated / empty path / mutate
    s = Schema.make().components(
        [
            TextInput.make("x").default("dx"),
            TextInput.make("y").dehydrated(False),
            TextInput.make(None),  # type: ignore[arg-type]
        ]
    )
    # Component.make(None) uses default name None — get_state_path None skipped
    out = s.fill({}).dehydrate()
    assert out.get("x") == "dx"
    assert "y" not in out

    # enum TypeError path
    assert TextInput.make("e").enum("not-enum").get_options() == {}

    # Form skips invisible
    form = Form.make().schema([TextInput.make("h").hidden().required()])
    assert form.fill({}).validate() == {}

    # RelationshipRepeater render sets relationship name
    html = RelationshipRepeater.make("items").schema([TextInput.make("n")]).render([{"n": "a"}])
    assert "or-field-RelationshipRepeater" in html

    # Builder without addable (no add button) still shows picker
    b = Builder.make("b").addable(False).blocks([Block.make("h").schema([TextInput.make("t")])])
    assert "or-builder-picker" in b.render([{"type": "h", "t": "x"}])

    # confirmed / same / after / before / unique without checker
    from almasix.orbit.forms.form import _check_rule

    f = TextInput.make("password")
    assert _check_rule("confirmed", "x", "password", attr="password", field=f, state={"password_confirmation": "y"})
    assert _check_rule("same:other", "a", "password", attr="p", field=f, state={"other": "b"})
    assert _check_rule("after:2020-01-01", "2019-01-01", "d", attr="d", field=f, state={})
    assert _check_rule("before:2020-01-01", "2021-01-01", "d", attr="d", field=f, state={})
    assert _check_rule("unique:t,c", "v", "e", attr="e", field=f, state={}) is None
    assert _check_rule("exists:t,c", "v", "e", attr="e", field=f, state={}) is None
    assert _check_rule("gt:z", "1", "n", attr="n", field=f, state={"z": "no"}) is None
    assert _check_rule("alpha", "a1", "n", attr="n", field=f, state={})
    assert _check_rule("alpha_num", "a!", "n", attr="n", field=f, state={})
    assert _check_rule("alpha_dash", "a!", "n", attr="n", field=f, state={})
    assert _check_rule("starts_with:x", "y", "n", attr="n", field=f, state={})
    assert _check_rule("ends_with:x", "y", "n", attr="n", field=f, state={})
    assert _check_rule("regex:^a$", "b", "n", attr="n", field=f, state={})
    assert _check_rule("between:1,2", "zzz", "n", attr="n", field=f, state={})
    assert _check_rule("json", [1, 2], "n", attr="n", field=f, state={}) is None
    from datetime import date, datetime

    assert _check_rule("date", date.today(), "d", attr="d", field=f, state={}) is None
    assert _check_rule("date", datetime.now(), "d", attr="d", field=f, state={}) is None
    assert _check_rule("after:start", "2020-02-01", "d", attr="d", field=f, state={"start": "2020-01-01"}) is None

    # Repeater mutate None callbacks
    r = Repeater.make("r")
    assert r.apply_mutate_before_create(1) == 1
    assert r.apply_mutate_before_fill(1) == 1
    assert r.apply_mutate_before_save(1) == 1


def test_coverage_micro_edges() -> None:
    from almasix.orbit.forms.form import _check_rule, _get_path
    from almasix.orbit.schemas.schema import Schema

    # validate skips empty state path
    empty = TextInput.make("tmp")
    empty._name = ""
    empty._state_path = ""
    assert Form.make().schema([empty]).fill({}).validate() == {}

    # dotted path into non-dict
    assert _get_path({"a": 1}, "a.b") is None

    # different: match fails
    f = TextInput.make("a")
    assert _check_rule("different:b", "same", "a", attr="a", field=f, state={"b": "same"})
    # distinct with unique siblings → None
    assert _check_rule("distinct", "x", "a", attr="a", field=f, state={}, siblings=["x", "y"]) is None
    # numeric compare failure message
    assert _check_rule("gt:n", "1", "a", attr="a", field=f, state={"n": 5})
    assert _check_rule("gte:n", "1", "a", attr="a", field=f, state={"n": 5})
    assert _check_rule("lt:n", "9", "a", attr="a", field=f, state={"n": 5})
    assert _check_rule("lte:n", "9", "a", attr="a", field=f, state={"n": 5})
    assert _check_rule("gt:n", None, "a", attr="a", field=f, state={"n": 5}) is None
    # filled / boolean empty skip
    assert _check_rule("filled", None, "a", attr="a", field=f, state={})
    assert _check_rule("boolean", "", "a", attr="a", field=f, state={}) is None
    # msg without format_validation_message
    assert _check_rule("required", None, "a", attr="a", field=None, state={})

    # dehydrate continue when no value/default
    assert Schema.make().components([TextInput.make("z")]).fill({}).dehydrate() == {}

    # walk steps branch via object with _steps
    class Stepped(Component):
        def __init__(self) -> None:
            super().__init__("s")
            self._steps = [("S", [TextInput.make("stepped")])]

    assert "stepped" in {x.get_name() for x in iter_fields([Stepped()])}

    # enum TypeError: issubclass on non-class after isinstance type check fails differently —
    # pass an Enum subclass instance path already covered; force options() with mapping groups
    from almasix.orbit.forms.components import _flatten_options, _option_groups

    assert _flatten_options([{"value": 1, "label": "One"}])[1] == "One"
    assert _flatten_options(None) == {}
    assert _option_groups([{"label": "G", "options": {"a": "A"}}])[0][0] == "G"
