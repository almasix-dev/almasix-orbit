"""Combobox Select parity — searchable / multiple / custom search / relationship."""

from __future__ import annotations

from almasix.orbit.forms import MultiSelect, Select
from almasix.orbit.schemas import Schema


def test_native_select_stays_plain() -> None:
    html = Select.make("status").options({"a": "A", "b": "B"}).render("a")
    assert "or-combobox" not in html
    assert '<select class="or-select"' in html
    assert "orbitCombobox" not in html


def test_searchable_select_renders_combobox() -> None:
    html = (
        Select.make("author")
        .options({"1": "Ada", "2": "Grace"})
        .searchable()
        .search_prompt("Find author…")
        .no_search_results_message("Nobody matched.")
        .render("1")
    )
    assert 'x-data="orbitCombobox"' in html
    assert "or-combobox-trigger" in html
    assert "or-combobox-dropdown" in html
    assert "or-combobox-search" in html
    assert "Find author…" in html
    assert "Nobody matched." in html
    assert 'data-label="Ada"' in html
    assert "selected" in html


def test_native_false_and_multiple_use_combobox() -> None:
    native_false = Select.make("x").options({"a": "A"}).native(False).render("a")
    assert "or-combobox" in native_false
    assert 'data-native="false"' in native_false

    multi = MultiSelect.make("tags").options({"a": "A", "b": "B"}).render(["a"])
    assert "or-combobox" in multi
    assert 'data-multiple="true"' in multi
    assert "or-combobox-chip" in multi
    assert "multiple" in multi


def test_allow_html_forces_combobox() -> None:
    html = (
        Select.make("tone")
        .options({"ok": "<strong>OK</strong>"})
        .allow_html()
        .render("ok")
    )
    assert "or-combobox" in html
    assert 'data-allow-html="true"' in html
    assert "<strong>OK</strong>" in html


def test_get_search_results_using_is_invoked_on_render() -> None:
    field = (
        Select.make("user")
        .searchable()
        .get_search_results_using(
            lambda search, **_: {"ada": "Ada Lovelace"} if "ada" in (search or "").lower() else {}
        )
    )
    empty = field.render(None, select_search={})
    assert 'value="ada"' not in empty or "Ada" not in empty

    hit = field.render(None, select_search={"user": "ada"})
    assert 'value="ada"' in hit
    assert "Ada Lovelace" in hit
    assert 'data-ajax-search="true"' in hit


def test_combobox_clear_and_actions_markup() -> None:
    html = (
        Select.make("tag")
        .options({"x": "X"})
        .searchable()
        .create_option_using(lambda **_: "x")
        .edit_option_action(True)
        .render("x")
    )
    assert "or-combobox-clear" in html
    assert "Create option" in html
    assert "Edit option" in html


def test_schema_dehydrate_select_value() -> None:
    field = Select.make("status").options({"draft": "Draft"}).searchable()
    out = Schema.make().schema([field]).state({"status": "draft"}).dehydrate()
    assert out["status"] == "draft"


def test_callback_options_list_shapes_and_empty() -> None:
    bare = Select.make("x")
    assert bare._callback_options_for_render(None) == {}

    field = Select.make("user").searchable().get_search_results_using(
        lambda search, **_: [
            ("ada", "Ada"),
            {"value": "grace", "label": "Grace"},
            "ignored",
            {"nope": True},
        ]
        if search
        else "nope"
    )
    html = field.render(None, select_search={"user": "a"})
    assert 'value="ada"' in html and "Ada" in html
    assert 'value="grace"' in html and "Grace" in html
    empty = field.render(None, select_search={"user": ""})
    assert 'value="ada"' not in empty


def test_overlay_keeps_selected_label_from_static_options() -> None:
    field = (
        Select.make("user")
        .options({"1": "Ada", "2": "Grace"})
        .searchable()
        .get_search_results_using(lambda search, **_: {"2": "Grace"})
    )
    html = field.render("1", select_search={"user": "g"})
    assert 'value="1"' in html and "Ada" in html
    assert 'value="2"' in html

    # prior options not a dict → skip selected-label merge
    odd = Select.make("odd").searchable().get_search_results_using(lambda **_: {"a": "A"})
    odd._options = None
    assert "or-combobox" in odd.render(None, select_search={"odd": "a"})

    # selected already in overlay / unknown / empty → no merge branch taken
    same = (
        Select.make("same")
        .options({"1": "Ada"})
        .searchable()
        .get_search_results_using(lambda **_: {"1": "Ada"})
    )
    assert "Ada" in same.render("1", select_search={"same": "x"})
    assert "Ada" in same.render("99", select_search={"same": "x"})
    assert "or-combobox" in same.render("", select_search={"same": "x"})


def test_native_without_placeholder_option() -> None:
    html = (
        Select.make("status")
        .options({"a": "A"})
        .selectable_placeholder(False)
        .render("a")
    )
    assert "or-combobox" not in html
    assert '<option value="">—</option>' not in html
