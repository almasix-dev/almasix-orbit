"""Tests for almasix.orbit.support."""

from __future__ import annotations

from almasix.orbit.support.colors import Color, Colors
from almasix.orbit.support.component import Component, schema_components
from almasix.orbit.support.html import e, tag
from almasix.orbit.support.icons import Heroicon, icon


def test_component_make_and_label() -> None:
    c = Component.make("first_name").label("Given name")
    assert c.get_name() == "first_name"
    assert c.get_label() == "Given name"
    assert Component.make("user_email").get_label() == "User Email"
    assert Component.make().get_label() == ""


def test_component_visibility_disabled_and_hidden() -> None:
    c = Component.make("x").hidden().visible(False)
    assert c.is_hidden()
    assert not c.is_visible()
    c2 = Component.make("y").visible(lambda **_: False)
    assert not c2.is_visible()
    c3 = Component.make("z").disabled(True)
    assert c3.is_disabled()
    c4 = Component.make("w").disabled(lambda user=None: user == "blocked")
    assert c4.is_disabled(user="blocked")
    assert not c4.is_disabled(user="ok")


def test_component_config_chain_and_to_dict() -> None:
    c = (
        Component.make("title")
        .extra_attributes({"data-x": "1"})
        .view("orbit::field")
        .column_span(2)
        .live()
        .dehydrated(False)
        .state_path("meta.title")
        .default("Hello")
        .helper_text("help")
        .hint("tip")
        .hint_icon("heroicon-o-information-circle")
        .configure(lambda self: self.label("Title"))
    )
    assert c.get_extra_attributes()["data-x"] == "1"
    assert c.get_view() == "orbit::field"
    assert not c.is_dehydrated()
    assert c.get_state_path() == "meta.title"
    assert c.get_default() == "Hello"
    d = c.to_dict()
    assert d["type"] == "Component"
    assert d["live"] is True
    assert d["helper_text"] == "help"


def test_component_render_and_schema_components() -> None:
    c = Component.make("name").label("Name")
    html = c.render("Ada")
    assert 'class="or-field"' in html
    assert 'value="Ada"' in html
    assert Component.make("h").hidden().render("x") == ""
    disabled = Component.make("d").disabled().render("")
    assert "disabled" in disabled
    items = schema_components([c])
    assert items[0]["name"] == "name"


def test_evaluate_and_callable_label() -> None:
    from almasix.orbit.support import evaluate

    assert evaluate("static") == "static"
    assert evaluate(lambda **_: "dynamic") == "dynamic"
    assert evaluate(lambda record: record["n"], record={"n": "Ada"}) == "Ada"
    # Extra utilities must not break single-parameter lambdas.
    assert (
        evaluate(
            lambda record: record["n"],
            record={"n": "Ada"},
            has_bulk=True,
            noise="x",
        )
        == "Ada"
    )
    c = Component.make("x").label(lambda user=None: f"Hi {user}")
    assert c.get_label(user="Sam") == "Hi Sam"
    c2 = Component.make("y").helper_text(lambda **_: "help me").default(lambda **_: 42)
    assert c2.get_helper_text() == "help me"
    assert c2.get_default() == 42
    c3 = Component.make("z").extra_attributes({"data-role": lambda user=None: user or "guest"})
    assert c3.get_extra_attributes(user="admin")["data-role"] == "admin"


def test_colors() -> None:
    assert Colors.hex(Color.PRIMARY) == "#f1511b"
    assert Colors.hex("danger") == "#ef4444"
    assert Colors.hex("#abc") == "#abc"
    assert Colors.css_class(Color.SUCCESS) == "or-color-success"
    assert Colors.css_class("info") == "or-color-info"


def test_html_helpers() -> None:
    assert e("<b>") == "&lt;b&gt;"
    assert e(None) == ""
    assert tag("div", "hi", attrs={"class": "x", "hidden": True, "skip": False}) == (
        '<div class="x" hidden>hi</div>'
    )
    assert tag("img", attrs={"src": "a.png"}, void=True) == '<img src="a.png" />'
    assert tag("span") == "<span></span>"


def test_icons() -> None:
    svg = icon("heroicon-o-home")
    assert "<svg" in svg and "or-icon" in svg
    missing = icon("heroicon-o-missing")
    assert 'data-missing-icon="heroicon-o-missing"' in missing
    assert Heroicon.outline("plus") == "heroicon-o-plus"
    assert Heroicon.outline("heroicon-o-check") == "heroicon-o-check"
    assert "<svg" in Heroicon.render("bell", size=16)
    assert "heroicon-o-home" in Heroicon.available()
