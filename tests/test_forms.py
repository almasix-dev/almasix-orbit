"""Tests for almasix.orbit.forms."""

from __future__ import annotations

from almasix.orbit.forms.components import (
    Block,
    Builder,
    Checkbox,
    CheckboxList,
    CodeEditor,
    ColorPicker,
    DatePicker,
    DateTimePicker,
    Field,
    FileUpload,
    Hidden,
    KeyValue,
    MarkdownEditor,
    ModalTableSelect,
    MorphToSelect,
    MultiSelect,
    OneTimeCodeInput,
    Placeholder,
    Radio,
    RelationshipRepeater,
    Repeater,
    RichEditor,
    Select,
    Slider,
    TableSelect,
    TagsInput,
    Textarea,
    TextInput,
    TimePicker,
    Toggle,
    ToggleButtons,
    ViewField,
)
from almasix.orbit.forms.form import Form


def test_form_validation_rules() -> None:
    form = Form.make().schema(
        [
            TextInput.make("email").required().email(),
            TextInput.make("age").numeric().integer(),
            TextInput.make("site").url().max_length(20).min_length(5),
            TextInput.make("note"),
        ]
    )
    errors = form.validate({})
    assert "email" in errors
    errors2 = form.validate(
        {
            "email": "bad",
            "age": "x",
            "site": "ftp://x",
            "note": "ok",
        }
    )
    assert any("email" in m for m in errors2["email"])
    assert "age" in errors2
    assert "site" in errors2
    ok = form.validate(
        {
            "email": "a@b.com",
            "age": "3",
            "site": "https://example.com",
            "note": "hello",
        }
    )
    assert "email" not in ok
    # max length fail
    assert "site" in form.validate({"email": "a@b.com", "site": "https://" + "x" * 30})
    # min length fail
    assert "site" in form.validate({"email": "a@b.com", "site": "http"})
    # numeric empty ok
    assert "age" not in form.validate({"email": "a@b.com", "age": ""})
    # state path from form state
    form.state({"email": ""})
    assert "email" in form.validate()


def test_validation_catalog_confirmed_same_in_dates_unique_exists() -> None:
    Form.unique_using(lambda value, table=None, column=None, **_: value != "taken")
    Form.exists_using(lambda value, table=None, column=None, **_: value == "exists")
    try:
        form = Form.make().schema(
            [
                TextInput.make("password").rules("confirmed"),
                TextInput.make("password_confirmation"),
                TextInput.make("email").rules("same:email_confirm"),
                TextInput.make("email_confirm"),
                Select.make("status").rules("in:draft,published"),
                DatePicker.make("starts_at").rules("date", "after:2020-01-01", "before:ends_at"),
                DatePicker.make("ends_at"),
                TextInput.make("slug").rules("unique:posts,slug"),
                TextInput.make("author_id").rules("exists:users,id"),
            ]
        )
        assert "password" in form.validate({"password": "a", "password_confirmation": "b"})
        assert "password" not in form.validate({"password": "a", "password_confirmation": "a"})
        assert "email" in form.validate({"email": "x", "email_confirm": "y"})
        assert "status" in form.validate({"status": "archived"})
        assert "status" not in form.validate({"status": "draft"})
        assert "starts_at" in form.validate({"starts_at": "not-a-date"})
        assert "starts_at" in form.validate({"starts_at": "2019-01-01", "ends_at": "2021-01-01"})
        assert "starts_at" in form.validate({"starts_at": "2022-01-01", "ends_at": "2021-01-01"})
        assert "starts_at" not in form.validate({"starts_at": "2020-06-01", "ends_at": "2021-01-01"})
        assert "slug" in form.validate({"slug": "taken"})
        assert "slug" not in form.validate({"slug": "free"})
        assert "author_id" in form.validate({"author_id": "missing"})
        assert "author_id" not in form.validate({"author_id": "exists"})
    finally:
        Form.unique_using(None)
        Form.exists_using(None)


def test_validation_attribute_and_custom_messages() -> None:
    form = Form.make().schema(
        [
            TextInput.make("email")
            .required()
            .validation_attribute("Email address")
            .validation_messages({"required": ":attribute is mandatory"}),
        ]
    )
    errors = form.validate({})
    assert errors["email"] == ["Email address is mandatory"]


def test_unique_exists_via_validate_ctx_callbacks() -> None:
    form = Form.make().schema([TextInput.make("code").rules("unique:t,c", "exists:t,c")])
    errors = form.validate(
        {"code": "x"},
        unique=lambda value, **_: False,
        exists=lambda value, **_: False,
    )
    assert "code" in errors
    assert len(errors["code"]) == 2


def test_field_helpers_and_options() -> None:
    f = (
        Field.make("role")
        .required()
        .placeholder("Pick")
        .autocomplete("off")
        .options(lambda **_: {"a": "Admin"})
        .multiple()
        .searchable()
        .relationship("roles", "name")
        .password()
        .tel()
    )
    assert f.is_required()
    assert "required" in f.get_rules()
    assert f.get_options() == {"a": "Admin"}
    d = f.to_dict()
    assert d["multiple"] is True
    assert d["relationship"] == ("roles", "name")
    # callable rule name in to_dict
    f2 = Field.make("x").rules(lambda v: v)
    assert "lambda" in f2.to_dict()["rules"][0] or f2.to_dict()["rules"]

    rich_rel = Select.make("author_id").relationship(
        "author",
        "name",
        search_columns=["name", "email"],
        preload=True,
        modify_query=lambda q: q,
        get_option_label=lambda r: r["name"],
    )
    rel = rich_rel.get_relationship()
    assert rel is not None
    assert rel["search_columns"] == ["name", "email"]
    assert rel["preload"] is True
    assert callable(rel["modify_query"])


def test_select_searchable_groups_create_edit() -> None:
    grouped = Select.make("city").options(
        {"Europe": {"berlin": "Berlin", "paris": "Paris"}, "Asia": {"tokyo": "Tokyo"}}
    )
    html = grouped.render("berlin")
    assert "<optgroup label=\"Europe\">" in html
    assert "selected" in html
    assert grouped.get_options()["berlin"] == "Berlin"

    list_groups = Select.make("t").options(
        [{"label": "A", "options": {"1": "One"}}, {"label": "B", "options": {"2": "Two"}}]
    )
    assert "optgroup" in list_groups.render()

    searchable = (
        Select.make("tag")
        .options({"a": "Alpha", "b": "Beta"})
        .searchable()
        .create_option_form(Form.make())
        .edit_option_action("editTag")
    )
    shtml = searchable.render()
    assert "data-searchable" in shtml
    assert "orbitSearchableSelect" in shtml
    assert "mountCreateOption" in shtml
    assert "mountAction('editTag')" in shtml
    assert "data-relationship" in (
        Select.make("x").relationship("posts", "title", preload=True).render()
    )


def test_text_input_variants_render() -> None:
    assert "type=\"email\"" in TextInput.make("e").email().render("a@b.c")
    assert "type=\"password\"" in TextInput.make("p").password().render()
    assert "type=\"number\"" in TextInput.make("n").numeric().render(1)
    assert "type=\"tel\"" in TextInput.make("t").tel().render()
    assert "type=\"url\"" in TextInput.make("u").url().render("https://x")
    live = TextInput.make("l").live().helper_text("h").required().render("v")
    assert "wire:model.live" in live and "or-required" in live and "or-helper" in live
    assert TextInput.make("h").hidden().render() == ""
    assert "disabled" in TextInput.make("d").disabled().render()


def test_textarea_select_checkbox_toggle() -> None:
    ta = Textarea.make("bio").rows(6).render("hi")
    assert "or-textarea" in ta and "rows=\"6\"" in ta
    assert Textarea.make("x").hidden().render() == ""

    sel = Select.make("c").options({"a": "A", "b": "B"}).multiple().render("a")
    assert "<select" in sel and "selected" in sel and "multiple" in sel
    assert Select.make("h").hidden().render() == ""

    assert "checked" in Checkbox.make("on").render(True)
    assert Checkbox.make("h").hidden().render() == ""
    tog = Toggle.make("flag").render(False)
    assert "or-field-Toggle" in tog and "or-toggle" in tog


def test_morph_to_select_types() -> None:
    morph = (
        MorphToSelect.make("notable")
        .types(
            [
                {"type": "post", "label": "Post", "options": {"1": "Hello"}},
                {"type": "user", "label": "User", "options": {"2": "Ada"}},
            ]
        )
        .searchable()
    )
    html = morph.render({"type": "post", "id": "1"})
    assert "or-field-MorphToSelect" in html
    assert "or-select-morph-type" in html
    assert "or-select-morph-id" in html
    assert "selected" in html
    assert morph.get_types()[0]["type"] == "post"

    simple = MorphToSelect.make("m").types(["App\\Models\\User", "App\\Models\\Post"])
    assert "User" in simple.render()


def test_file_upload_depth() -> None:
    fu = (
        FileUpload.make("avatar")
        .disk("s3")
        .directory("avatars")
        .multiple()
        .avatar()
        .reorderable()
        .max_size(100)
        .min_size(1)
        .image_size(min_width=32, max_width=512)
    )
    html = fu.render()
    assert 'data-disk="s3"' in html
    assert 'data-directory="avatars"' in html
    assert 'data-avatar="true"' in html
    assert "data-image-preview" in html
    assert "data-reorderable" in html
    assert "multiple" in html
    assert "or-file-preview" in html
    assert "image/" in FileUpload.make("img").image().render()
    assert FileUpload.make("h").hidden().render() == ""
    assert "or-file" in FileUpload.make("plain").render()


def test_repeater_builder_relationship_controls() -> None:
    rep = (
        Repeater.make("items")
        .schema([TextInput.make("name")])
        .cloneable()
        .collapsible()
        .reorderable()
        .item_label(lambda index, **_: f"Row {index + 1}")
        .min_items(1)
        .max_items(2)
    )
    html = rep.render([{"name": "a"}, {"name": "b"}])
    assert "cloneRepeaterItem" in html
    assert "data-collapse" in html
    assert "moveRepeaterItem" in html
    assert "Row 1" in html
    assert 'data-max-items="2"' in html
    assert "disabled" in html  # add button disabled at max

    block = Block.make("hero").label("Hero").icon("sparkles").schema([TextInput.make("title")]).max_items(1)
    builder = Builder.make("blocks").blocks([block, Block.make("quote").label("Quote").schema([Textarea.make("body")])])
    bhtml = builder.render([{"type": "hero", "title": "Hi"}])
    assert "or-field-Builder" in bhtml
    assert "or-builder-picker" in bhtml
    assert "addBuilderBlock" in bhtml
    assert "disabled" in bhtml  # hero max_items reached
    assert builder.get_blocks()[0].get_max_items() == 1

    rr = (
        RelationshipRepeater.make("comments")
        .schema([TextInput.make("body")])
        .mutate_relationship_data_before_create(lambda data: data)
        .mutate_relationship_data_before_fill(lambda data: data)
    )
    assert "or-field-RelationshipRepeater" in rr.render([{}])


def test_rich_editor_tiptap_attrs() -> None:
    ed = RichEditor.make("body").toolbar_buttons(["bold", "italic", "link", "strike"]).rows(8)
    html = ed.render("<p>Hi</p>")
    assert "or-editor-rich" in html
    assert "data-tiptap" in html
    assert 'data-toolbar="bold,italic,link,strike"' in html
    assert 'type="hidden"' in html
    assert "data-tiptap-input" in html
    assert ed.get_toolbar_buttons() == ["bold", "italic", "link", "strike"]


def test_hidden_placeholder_dates_file_radio_repeater() -> None:
    assert 'type="hidden"' in Hidden.make("id").render(3)
    ph = Placeholder.make("info").content("Hello").render()
    assert "Hello" in ph
    assert "state" in Placeholder.make("x").render("state")

    assert DatePicker.make("d").to_dict()["input_type"] == "date"
    assert DateTimePicker.make("dt")._input_type == "datetime-local"
    assert TimePicker.make("t")._input_type == "time"

    fu = FileUpload.make("avatar").accepted_file_types(["image/png"]).max_size(100).render()
    assert "or-file" in fu and "image/png" in fu

    radio = Radio.make("sex").options({"m": "M", "f": "F"}).render("m")
    assert 'type="radio"' in radio and "checked" in radio
    assert Radio.make("h").hidden().render() == ""

    rep = Repeater.make("items").schema([TextInput.make("name")])
    assert len(rep.get_schema()) == 1
    assert isinstance(Builder.make("b"), Repeater)


def test_form_skips_non_fields_and_unknown_rules() -> None:
    from almasix.orbit.schemas.layouts import Section

    form = Form.make().schema(
        [
            Section.make("s"),
            TextInput.make("x").rules(lambda v: None, "unknown_rule", "required"),
        ]
    )
    errors = form.validate({"x": ""})
    assert "x" in errors
    assert form.validate({"x": "ok"}) == {}


def test_option_helpers_and_edge_renders() -> None:
    from datetime import date, datetime

    from almasix.orbit.forms.components import _flatten_options, _option_groups

    assert _flatten_options(None) == {}
    assert _flatten_options(lambda: None) == {}
    assert _flatten_options([{"value": "x", "label": "X"}, {"options": None}])["x"] == "X"
    assert _flatten_options("nope") == {}
    assert _option_groups(None) == [(None, {})]
    assert _option_groups([{"value": "1", "label": "One"}])[0][1]["1"] == "One"
    assert _option_groups([{"label": None, "options": {"a": "A"}}])[0][0] is None
    assert _option_groups(42) == [(None, {})]

    f = Field.make("r")
    f._relationship = ("roles", "name")
    assert f.get_relationship() == {"name": "roles", "title_attribute": "name"}
    assert Field.make("n").get_relationship() is None

    assert "editOption" in Select.make("s").edit_option_action(True).render()
    assert "data-search-columns" in (
        Select.make("a").relationship("author", "name", search_columns=["email"]).render()
    )
    assert Select.make("o").options(lambda **_: None).get_options() == {}

    fu = FileUpload.make("pic").accepted_file_types(["image/png"]).avatar()
    assert fu._accepted_file_types == ["image/png"]
    assert "image/png" in FileUpload.make("i").accepted_images().render()
    assert FileUpload.make("x").image_preview(False).avatar(False).render()

    assert RichEditor.make("h").hidden().render() == ""
    assert MorphToSelect.make("h").hidden().render() == ""
    morph = MorphToSelect.make("m").type_attribute("kind").id_attribute("ref").types(
        [{"name": "post", "options": {"1": "P"}}]
    )
    assert "post:1" in morph.render("post:1") or "selected" in morph.render("post:1")
    assert morph.render({"kind": "post", "ref": "1"})

    rep = Repeater.make("r").schema([TextInput.make("n")]).render(["not-a-dict"])
    assert "or-repeater-item" in rep
    assert Repeater.make("empty").schema([]).render([])  # empty list → one item

    b = Builder.make("b").schema([TextInput.make("t")]).blocks(
        [Block.make("hero").schema([TextInput.make("h")])]
    )
    assert b.get_schema()[0].get_name() == "t"  # existing schema preserved
    assert "or-builder-picker" in b.render([{"block": "hero"}])

    plain_builder = Builder.make("plain").schema([TextInput.make("x")])
    assert "or-field-Builder" in plain_builder.render()

    # Validation edges: callable returning callable, False; date/datetime; TypeError checkers
    form = Form.make().schema(
        [
            TextInput.make("a").rules(lambda **_: (lambda: None), lambda v: False),
            DatePicker.make("d").rules("date", "after:start"),
        ]
    )
    assert "a" in form.validate({"a": "x"})
    assert "d" not in form.validate({"d": date(2021, 1, 2), "start": datetime(2021, 1, 1)})

    def positional_only(value: str) -> bool:
        return False

    Form.unique_using(None)
    Form.exists_using(None)
    form2 = Form.make().schema([TextInput.make("u").rules("unique:t", "exists:t")])
    assert "u" in form2.validate({"u": "z"}, unique=positional_only, exists=positional_only)


def test_all_field_make() -> None:
    classes = [
        TextInput,
        Textarea,
        Select,
        Checkbox,
        Toggle,
        Hidden,
        Placeholder,
        DatePicker,
        DateTimePicker,
        TimePicker,
        FileUpload,
        Radio,
        CheckboxList,
        TagsInput,
        ColorPicker,
        RichEditor,
        MarkdownEditor,
        KeyValue,
        Repeater,
        Builder,
        Block,
        Slider,
        ToggleButtons,
        CodeEditor,
        MultiSelect,
        OneTimeCodeInput,
        ViewField,
        MorphToSelect,
        TableSelect,
        ModalTableSelect,
        RelationshipRepeater,
    ]
    for cls in classes:
        inst = cls.make("field")
        assert inst.get_name() == "field"
        if cls is not Block:
            assert isinstance(inst, Field)
