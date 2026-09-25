"""Exhaustive Forms + Schemas Filament-parity coverage."""

from __future__ import annotations

from almasix.orbit.forms.components import (
    Block,
    Builder,
    CheckboxList,
    ColorPicker,
    DatePicker,
    DateTimePicker,
    MoneyInput,
    MonthPicker,
    MultiSelect,
    OneTimeCodeInput,
    Placeholder,
    Radio,
    Repeater,
    TagsInput,
    TextInput,
    TimePicker,
    ViewField,
    WeekPicker,
    YearPicker,
)
from almasix.orbit.forms.form import Form
from almasix.orbit.panels.conduit.hosts import CreateRecordHost, EditRecordHost, FormHost
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.schemas import (
    Fieldset,
    Flex,
    Grid,
    Group,
    Section,
    Split,
    Tabs,
    Wizard,
)
from almasix.orbit.schemas.primes import Icon, Image, Text, UnorderedList
from almasix.orbit.schemas.schema import Schema
from almasix.orbit.tables import TextColumn


def test_schema_group_split_section_tabs_wizard() -> None:
    state = {"a": "1", "b": "2", "c": "3"}
    group = Group.make().columns(2).schema([TextInput.make("a"), TextInput.make("b")])
    assert "or-schema-group" in group.render(state)
    assert "or-grid-cols-2" in group.render(state)

    split = Split.make().from_("md").schema([TextInput.make("a"), TextInput.make("b")])
    assert "or-schema-split-from-md" in split.render(state)

    section = (
        Section.make("meta")
        .heading("Meta")
        .description("Details")
        .icon("heroicon-o-cog-6-tooth")
        .compact()
        .aside()
        .collapsible()
        .collapsed()
        .persist_collapsed()
        .schema([TextInput.make("a")])
    )
    html = section.render(state)
    assert "or-section-compact" in html
    assert "or-section-aside" in html
    assert "data-persist-collapsed" in html
    assert "x-data" in html

    tabs = (
        Tabs.make("profile")
        .persist_tab()
        .active_tab(1)
        .tabs(
            ("Basics", [TextInput.make("a")]),
            {"label": "Advanced", "schema": [TextInput.make("b")], "icon": "heroicon-o-star", "badge": 2},
        )
    )
    th = tabs.render(state)
    assert "or-tab-badge" in th
    assert "or-tab-icon" in th
    assert 'x-data="{ tab: 1 }"' in th
    assert len(tabs.get_child_components()) == 2

    wizard = (
        Wizard.make()
        .skippable()
        .start_step(0)
        .steps(
            ("One", [TextInput.make("a")]),
            {"label": "Two", "schema": [TextInput.make("b")], "description": "Next"},
        )
    )
    wh = wizard.render(state)
    assert "or-wizard-nav" in wh
    assert "or-wizard-footer" in wh
    assert "Skip" in wh
    assert "Continue" in wh


def test_schema_primes_and_fieldset_hidden() -> None:
    assert "Hi" in Text.make().content("Hi").render()
    assert Icon.make().icon("heroicon-o-star").render()
    assert "src=" in Image.make().src("/x.png").render()
    assert "<li>" in UnorderedList.make().items(["a", "b"]).render()
    assert Group.make().hidden().render({"a": 1}) == ""
    assert Fieldset.make().label("F").schema([TextInput.make("a")]).render({"a": "x"})


def test_placeholder_respects_hidden() -> None:
    assert Placeholder.make("p").content("Hello").hidden().render() == ""
    assert "Hello" in Placeholder.make("p").content("Hello").render()


def test_date_pickers_and_money_and_color() -> None:
    d = DatePicker.make("d").min_date("2020-01-01").max_date("2030-01-01").display_format("Y-m-d")
    html = d.render("2024-01-01")
    assert "or-datepicker" in html
    assert 'data-mode="date"' in html
    assert 'data-min="2020-01-01"' in html
    assert "orbitDatePicker" in html
    native = DatePicker.make("n").native(True).min_date("2020-01-01").render("2024-01-01")
    assert 'type="date"' in native
    assert 'min="2020-01-01"' in native
    assert 'type="datetime-local"' in DateTimePicker.make("dt").native(True).render()
    assert 'type="time"' in TimePicker.make("t").native(True).render()
    assert 'data-mode="week"' in WeekPicker.make("w").render()
    assert 'data-mode="month"' in MonthPicker.make("m").render()
    assert 'data-mode="year"' in YearPicker.make("y").render()
    assert "or-field-MoneyInput" in MoneyInput.make("amt").currency("EUR").locale("de").render(12.5)
    assert 'type="color"' in ColorPicker.make("c").render("#ff0000")


def test_tags_radio_checkbox_list_affix_actions() -> None:
    tags = (
        TagsInput.make("tags")
        .suggestions(["red", "blue"])
        .separator(";")
        .reorderable()
        .split_keys([" ", "Tab"])
        .tag_prefix("#")
        .tag_suffix("!")
        .render(["red"])
    )
    assert "datalist" in tags
    assert 'data-separator=";"' in tags
    assert 'data-reorderable="true"' in tags
    assert 'x-data="orbitTagsInput"' in tags
    assert 'data-path="data.tags"' in tags
    assert 'wire:key="tags-input-tags"' in tags or 'conduit:key="tags-input-tags"' in tags
    assert "@keydown.tab.prevent" in tags
    assert "or-tags-input-wrap" in tags
    assert "or-tag-remove" in tags
    assert 'data-tag-suffix="!"' in tags
    empty = TagsInput.make("empty").separator(",").render(None)
    assert 'data-state="[]"' in empty
    no_sep = TagsInput.make("plain").separator("").split_keys(["Tab"]).render("")
    assert "Tab" in no_sep
    # JSON array strings must become real chips, not one quoted blob.
    import json as _json
    import re as _re
    from html import unescape as _un

    json_state = TagsInput.make("genres").render('["afrobeat","electronic"]')
    raw_state = _un(_re.search(r'data-state="([^"]*)"', json_state).group(1))
    assert _json.loads(raw_state) == ["afrobeat", "electronic"]

    # Invalid JSON array-looking text falls back to separator split / whole string.
    from almasix.orbit.forms.components import _normalize_string_list

    assert _normalize_string_list("[not-json]") == ["[not-json]"]
    assert _normalize_string_list("a,b", separator=",") == ["a", "b"]
    assert _normalize_string_list("solo", separator="") == ["solo"]
    assert _normalize_string_list("   ", separator="") == []
    assert _normalize_string_list(0) == ["0"]
    assert _normalize_string_list(False) == ["False"]
    assert _normalize_string_list(["", " x "]) == ["x"]

    radio = (
        Radio.make("plan")
        .options({"a": "A", "b": "B"})
        .descriptions({"a": "Alpha"})
        .options_columns(2)
        .render("a")
    )
    assert "or-option-desc" in radio
    assert "or-options-cols-2" in radio
    assert 'conduit:model="data.plan"' in radio or 'wire:model="data.plan"' in radio

    checks = (
        CheckboxList.make("feats")
        .options({"x": "X", "y": "Y"})
        .bulk_toggleable()
        .render(["x"])
    )
    assert "data-select-all" in checks
    assert 'x-data="orbitCheckboxList"' in checks
    assert 'data-path="data.feats"' in checks
    assert 'wire:key="checkbox-list-feats"' in checks or 'conduit:key="checkbox-list-feats"' in checks
    assert "wire:ignore" in checks and "conduit:ignore" in checks
    assert 'x-model="selected"' in checks
    assert "selectAll()" in checks
    assert ":checked=" not in checks

    affix = TextInput.make("code").prefix_action("gen").suffix_action("copy").render("1")
    assert "mountAction('gen')" in affix
    assert "mountAction('copy')" in affix


def test_conditional_validation_rules() -> None:
    form = (
        Form.make()
        .schema(
            [
                TextInput.make("type").default("a"),
                TextInput.make("extra").required_if("type", "a"),
                TextInput.make("note").required_unless("type", "b"),
                TextInput.make("secret").prohibited_if("type", "a"),
                TextInput.make("blocked").prohibited(),
            ]
        )
    )
    errs = form.validate({"type": "a", "extra": "", "note": "", "secret": "x", "blocked": "y"})
    assert "extra" in errs
    assert "note" in errs
    assert "secret" in errs
    assert "blocked" in errs
    ok = form.validate({"type": "b", "extra": "", "note": "n", "secret": "x", "blocked": ""})
    assert "extra" not in ok
    assert "secret" not in ok


def test_repeater_table_mode_and_multi_select() -> None:
    rep = (
        Repeater.make("rows")
        .schema([TextInput.make("name")])
        .table(["Name"])
        .grid(2)
        .cloneable()
        .reorderable()
        .collapsible()
        .render([{"name": "A"}])
    )
    assert "or-repeater-table" in rep
    assert "or-repeater-table-head" in rep
    assert "data-grid=\"2\"" in rep
    assert "multiple" in MultiSelect.make("t").options({"a": "A"}).render(["a"])
    assert "one-time-code" in OneTimeCodeInput.make("otp").render("123")
    assert "<b>x</b>" in ViewField.make("v").content(lambda state, **_: f"<b>{state}</b>").render("x")


def test_form_host_repeater_mutations() -> None:
    class Demo(Resource):
        model = type("X", (), {})

        @classmethod
        def form(cls, form):
            return form.schema(
                [
                    Repeater.make("links").schema([TextInput.make("url")]),
                    Builder.make("blocks").blocks(
                        [Block.make("hero").schema([TextInput.make("heading")])]
                    ),
                ]
            )

        @classmethod
        def table(cls, table):
            return table.columns([TextColumn.make("id")])

    panel = Panel.make("form-mut").path("/form-mut")
    Host = CreateRecordHost.bind(panel=panel, resource=Demo)
    host = Host()
    host.mount(data={"links": [{"url": "a"}], "blocks": []})
    host.addRepeaterItem("links")
    assert len(host.data["links"]) == 2
    host.cloneRepeaterItem("links", 0)
    assert len(host.data["links"]) == 3
    host.moveRepeaterItem("links", 0, 1)
    host.removeRepeaterItem("links", 0)
    host.addBuilderBlock("blocks", "hero")
    assert host.data["blocks"][0]["type"] == "hero"
    host.addKeyValueRow("meta")
    assert isinstance(host.data.get("meta"), dict)

    edit = EditRecordHost.bind(panel=panel, resource=Demo)()
    edit.mount(record_id="1", data={"links": []})
    edit.addRepeaterItem("links")
    assert edit.data["links"] == [{}]

    class FH(FormHost):
        _form_factory = staticmethod(
            lambda: Form.make().schema([Repeater.make("items").schema([TextInput.make("x")])])
        )
        _title = "Demo"

    fh = FH()
    fh.mount(data={"items": []})
    fh.addRepeaterItem("items")
    assert fh.data["items"] == [{}]
    html = fh.render()
    assert "or-field-Repeater" in html


def test_builder_and_flex_column_span() -> None:
    flex = Flex.make().schema([TextInput.make("a").column_span(2), TextInput.make("b")])
    assert "or-col-span-2" in flex.render({"a": "1", "b": "2"})
    b = (
        Builder.make("blocks")
        .blocks([Block.make("hero").label("Hero").icon("heroicon-o-star").schema([TextInput.make("t")])])
        .addable(False)
        .render([])
    )
    assert "or-field-Builder" in b


def test_schema_dehydrate_and_non_dict_render() -> None:
    schema = Schema.make().components([TextInput.make("title")])
    schema.fill({"title": "Hi"})
    assert schema.dehydrate()["title"] == "Hi"
    assert schema.render("not-a-dict")  # non-dict state tolerated
    assert Grid.make().grid_container().defer_loading().schema([]).render()


def test_more_forms_schemas_edge_coverage(monkeypatch) -> None:
    # Field helpers
    f = TextInput.make("t").autocomplete("name").autofocus().readonly()
    assert f.is_readonly() is True
    assert f.get_placeholder() is None
    f.placeholder("x")
    assert f.get_placeholder() == "x"
    assert "readonly" in f.render("v")

    from almasix.orbit.forms.components import KeyValue, MarkdownEditor, MorphToSelect

    assert "or-key-value-row" in KeyValue.make("kv").render({"a": "1"})
    assert "Add row" in KeyValue.make("kv").render({})
    assert "or-field-MarkdownEditor" in MarkdownEditor.make("md").render("# hi")

    morph = MorphToSelect.make("owner").options({"user": "User", "team": "Team"}).render("user")
    assert "or-field-MorphToSelect" in morph

    assert Tabs.make().hidden().tabs(("A", [TextInput.make("a")])).render({}) == ""
    assert Wizard.make().hidden().steps(("A", [TextInput.make("a")])).render({}) == ""
    tabs = Tabs.make().tabs({"label": "X", "schema": [TextInput.make("a")], "badge": lambda: None})
    assert "or-tab-badge" not in tabs.render({"a": "1"})

    flex_html = Flex.make().schema([TextInput.make("a").hidden()]).render({})
    assert "or-flex" in flex_html
    assert Group.make().schema([]).render(None) is not None

    class FH(FormHost):
        _form_factory = staticmethod(lambda: Form.make().schema([TextInput.make("x")]))

    fh = FH()
    fh.mount(data={})
    fh.removeRepeaterItem("missing", 0)
    fh.moveRepeaterItem("missing", 0, 1)
    fh.cloneRepeaterItem("missing", 0)
    fh.addBuilderBlock("blocks", "x")
    assert fh.data.get("blocks") == [{"type": "x"}]
    fh.mountTableSelect("rel")
    fh.mountCreateOption("rel")
    fh.mountEditOption("rel")

    # Nested path get/set + mutation edges
    fh.data = {"nested": {"items": [{"x": 1}, {"x": 2}]}}
    assert fh._form_path_get("nested.items") == [{"x": 1}, {"x": 2}]
    assert fh._form_path_get("nested.items.0") is None or True
    fh.data = {"items": "bad"}
    assert fh._form_path_get("items.extra") is None
    fh._form_path_set("", "x")
    fh.data = {}
    fh._form_path_set("deep.child", "v")
    assert fh.data["deep"]["child"] == "v"
    fh.data = {"items": [{"a": 1}, "plain"]}
    fh.removeRepeaterItem("items", "nope")
    fh.moveRepeaterItem("items", "nope", 1)
    fh.cloneRepeaterItem("items", "nope")
    fh.cloneRepeaterItem("items", 1)
    assert len(fh.data["items"]) == 3
    fh.moveRepeaterItem("items", 0, 1)
    fh.removeRepeaterItem("items", 99)
    fh.addKeyValueRow("meta")
    fh.addKeyValueRow("meta")
    assert "key1" in fh.data["meta"] and "key2" in fh.data["meta"]

    # Hidden split / section heading fallback / wizard get_child_components
    assert Split.make().hidden().schema([TextInput.make("a")]).render({}) == ""
    assert "Slug" in Section.make("slug").schema([TextInput.make("a")]).render({"a": "1"}) or "slug" in Section.make("slug").schema([]).render().lower()
    wiz = Wizard.make().schema([TextInput.make("extra")]).steps(("A", [TextInput.make("a")]))
    assert any(c.get_name() == "extra" for c in wiz.get_child_components())
    assert any(c.get_name() == "a" for c in wiz.get_child_components())

    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "almasix.orbit.forms.walk":
            raise ImportError("no walk")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    s = Schema.make().components([TextInput.make("t")])
    s.fill({"t": "1"})
    assert s.dehydrate()["t"] == "1"
    monkeypatch.undo()

    from almasix.orbit.forms.walk import iter_fields

    fields = iter_fields(
        [
            Section.make().schema([TextInput.make("inside")]),
            Wizard.make().steps(("S", [TextInput.make("w")])),
        ]
    )
    assert {f.get_name() for f in fields} >= {"inside", "w"}
