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


def test_html_string_and_classes() -> None:
    from almasix.orbit.support import HtmlString, classes

    raw = HtmlString("<em>trusted</em>")
    assert e(raw) == "<em>trusted</em>"
    assert e("<em>no</em>") == "&lt;em&gt;no&lt;/em&gt;"

    class Markup:
        def __html__(self) -> str:
            return "<i>m</i>"

    assert e(Markup()) == "<i>m</i>"
    assert classes("or-btn", None, False, "", True, "or-btn-primary") == "or-btn or-btn-primary"
    assert classes({"or-grow": True, "or-hidden": False}, "  extra  ") == "or-grow extra"
    assert classes("   ") == ""
    assert classes() == ""


def test_component_key_grow_when_and_html_label() -> None:
    from almasix.orbit.support import HtmlString

    bare = Component.make("title")
    assert bare.get_key() == "title"
    keyed = Component.make("title").key("row-1")
    assert keyed.get_key() == "row-1"
    assert Component.make("title").key(lambda record=None, **_: record).get_key(record=None) is None
    grown = Component.make("title").grow()
    assert grown.is_grow()
    assert "or-grow" in grown.render()
    assert 'data-key="row-1"' in keyed.render()
    skipped = Component.make("x").when(False, lambda c: c.label("Nope"))
    assert skipped.get_label() == "X"
    applied = Component.make("x").when(True, lambda c: c.label("Yes")).when(
        lambda: True, lambda c: c.grow()
    )
    assert applied.get_label() == "Yes"
    assert applied.is_grow()
    html_label = Component.make("x").label(HtmlString("<b>Hi</b>"))
    assert "<b>Hi</b>" in html_label.render()
    assert Component.make("x").label(lambda: None).get_label() == ""
    helper = Component.make("x").helper_text(HtmlString("<em>help</em>"))
    assert e(helper.get_helper_text()) == "<em>help</em>"
    assert Component.make("x").helper_text(lambda: None).get_helper_text() is None
    hint = Component.make("x").hint(HtmlString("<i>tip</i>"))
    assert e(hint.get_hint()) == "<i>tip</i>"
    assert Component.make("x").hint(lambda: None).get_hint() is None
    assert Component.make("x").get_helper_text() is None
    assert Component.make("x").get_hint() is None
    assert Component.make("x").get_hint_icon() is None
    assert Component.make("x").hint_icon(lambda: None).get_hint_icon() is None
    live = Component.make("email").live(on_blur=True)
    assert live.wire_model_directive() == "model.blur"
    assert "conduit:model.blur" in live.wire_model_attrs("email")
    debounce = Component.make("email").live(debounce=250)
    assert debounce.wire_model_directive() == "model.live.debounce.250ms"
    assert Component.make("email").saved(False).is_dehydrated() is False
    assert Component.make("email").hidden_label().is_label_hidden()
    assert Component.make("email").inline_label().is_inline_label()
    callable_key = Component.make("n").key(lambda **_: "dyn").grow(lambda **_: False)
    dumped = callable_key.to_dict()
    assert dumped["key"] is None
    assert dumped["grow"] is None
    assert not callable_key.is_grow()


def test_color_palette_and_css_var() -> None:
    palette = Colors.palette(Color.PRIMARY)
    assert palette[500] == Colors.hex(Color.PRIMARY)
    assert set(palette) == {50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950}
    assert palette[50].startswith("#")
    short = Colors.palette("#abc")
    assert short[500] == "#aabbcc"
    assert Colors.palette("not-a-color") == {500: "not-a-color"}
    assert Colors.css_var(Color.DANGER) == "var(--or-danger-500)"
    assert Colors.css_var("info", 700) == "var(--or-info-700)"


def test_icon_aliases() -> None:
    from almasix.orbit.support import register_icon, reset_icon_aliases

    reset_icon_aliases()
    register_icon("actions::delete", "heroicon-o-trash")
    svg = icon("actions::delete")
    assert "<svg" in svg
    assert Heroicon.outline("actions::delete") == "heroicon-o-trash"
    Heroicon.alias("nav::home", "heroicon-o-home")
    assert "<svg" in Heroicon.render("nav::home")
    Heroicon.reset_aliases()
    missing = icon("actions::delete")
    assert 'data-missing-icon="actions::delete"' in missing


def test_evaluate_fallback_paths(monkeypatch) -> None:
    import inspect

    from almasix.orbit.support.evaluate import evaluate

    def needs_one(x: str) -> str:
        return x

    assert evaluate(needs_one) is needs_one
    assert evaluate(str.upper, "hi") == "HI"

    def boom(_candidate: object) -> None:
        raise ValueError("no signature")

    monkeypatch.setattr(inspect, "signature", boom)

    def grab(**kw: object) -> object:
        return kw.get("record")

    assert evaluate(grab, record="Ada", extra=1) == "Ada"

    def type_boom(_candidate: object) -> None:
        raise TypeError("no signature")

    monkeypatch.setattr(inspect, "signature", type_boom)
    assert evaluate(grab, record="Bea") == "Bea"
