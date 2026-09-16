"""Tests for almasix.orbit.forms."""

from __future__ import annotations

from almasix.orbit.forms.components import (
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
    assert FileUpload.make("h").hidden().render() == ""
    assert "or-file" in FileUpload.make("plain").render()  # no accept attr

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
        assert isinstance(inst, Field)
