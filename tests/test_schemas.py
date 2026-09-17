"""Tests for almasix.orbit.schemas."""

from __future__ import annotations

from almasix.orbit.forms.components import TextInput
from almasix.orbit.schemas.layouts import Fieldset, Grid, Section, Tabs, Wizard
from almasix.orbit.schemas.schema import Schema


def test_schema_state_fill_dehydrate_and_render() -> None:
    name = TextInput.make("name").default("Anon")
    bio = TextInput.make("bio").dehydrated(False)
    schema = (
        Schema.make("user")
        .schema([name, bio])
        .columns(2)
        .state({"name": "Ada"})
        .fill({"extra": 1})
    )
    assert schema.get_state()["name"] == "Ada"
    assert schema.get_state()["extra"] == 1
    dehydrated = schema.dehydrate()
    assert dehydrated == {"name": "Ada"}
    schema2 = Schema.make().components([TextInput.make("x").default("d")])
    assert schema2.dehydrate() == {"x": "d"}
    # no path / no default → skipped
    assert Schema.make().components([TextInput.make(None)]).dehydrate() == {}
    html = schema.render({"name": "Grace"})
    assert "or-schema-cols-2" in html
    assert "Grace" in html
    d = schema.to_dict()
    assert d["columns"] == 2
    assert len(d["components"]) == 2


def test_grid_section_fieldset() -> None:
    field = TextInput.make("title")
    grid = Grid.make().columns(3).schema([field])
    assert len(grid.get_child_components()) == 1
    assert "or-grid-cols-3" in grid.render({"title": "T"})
    assert "schema" in grid.to_dict()

    section = (
        Section.make("meta")
        .heading("Meta")
        .description("About")
        .collapsible()
        .collapsed()
        .schema([field])
    )
    html = section.render({"title": "X"})
    assert 'data-collapsible="true"' in html
    assert "About" in html

    fieldset = Fieldset.make("contact").label("Contact").schema([field])
    assert "<fieldset" in fieldset.render({"title": "Y"})
    assert "Contact" in fieldset.render({"title": "Y"})


def test_tabs_and_wizard() -> None:
    a = TextInput.make("a")
    b = TextInput.make("b")
    tabs = Tabs.make().tabs(("One", [a]), ("Two", [b]))
    th = tabs.render({"a": "1", "b": "2"})
    assert "or-tabs" in th and "or-tab is-active" in th

    wizard = Wizard.make().steps(("Step 1", [a]), ("Step 2", [b]))
    wh = wizard.render({"a": "1"})
    assert "or-wizard-step" in wh
    assert "Step 1" in wh


def test_flex_callout_empty_state_and_primes() -> None:
    from almasix.orbit.actions.action import Action
    from almasix.orbit.schemas.layouts import Callout, EmptyState, Flex
    from almasix.orbit.schemas.primes import Icon, Image, Text, UnorderedList

    field = TextInput.make("title")
    flex = Flex.make().grow().from_breakpoint("md").dense().schema([field])
    assert "or-flex" in flex.render({"title": "T"})
    assert "or-flex-from-md" in flex.render({"title": "T"})

    callout = (
        Callout.make("note")
        .label("Heads up")
        .description("Read me")
        .warning()
        .icon("heroicon-o-bell")
        .footer_actions([Action.make("ok").label("OK").url("#")])
    )
    ch = callout.render()
    assert "or-callout" in ch and "Heads up" in ch and "or-callout-footer" in ch
    assert "or-callout" in Callout.make().danger().render()
    assert "or-callout" in Callout.make().success().render()
    assert Callout.make().hidden().render() == ""

    empty = (
        EmptyState.make()
        .heading("No posts")
        .description("Create one")
        .icon("heroicon-o-plus")
        .actions([Action.make("create").label("Create").url("/create")])
    )
    eh = empty.render()
    assert "or-schema-empty" in eh and "No posts" in eh
    assert EmptyState.make().hidden().render() == ""

    assert "or-prime-text" in Text.make().content("Hello").badge().color("primary").size("lg").weight("bold").render()
    assert "<strong>" in Text.make().content("**Hi**").markdown().render()
    assert "<b>" in Text.make().content("<b>X</b>").html().render()
    assert Text.make().hidden().render() == ""
    assert "or-prime-icon" in Icon.make().icon("heroicon-o-home").color("success").tooltip("Home").render()
    assert Icon.make().hidden().render() == ""
    assert "or-prime-img" in Image.make().src("/a.png").image_size(48).alignment("center").render()
    assert Image.make().src("").render() == ""
    assert Image.make().hidden().render() == ""
    assert "<li>A</li>" in UnorderedList.make().items(["A", "B"]).bullet_size("sm").render()
    assert "Ada" in UnorderedList.make().items([Text.make().content("Ada")]).render()
    assert UnorderedList.make().hidden().render() == ""
    assert "or-grid-container" in Grid.make().grid_container().gap(False).schema([field]).render()
    assert "or-gap-sm" in Grid.make().gap("sm").defer_loading().schema([field]).render()
    assert Callout.make().info().color("info").icon_color("primary").footer_actions_alignment("end").render()
    assert "or-callout" in Callout.make().schema([field]).render({"title": "x"})
    t = Text.make().content(lambda **_: "Dyn").tooltip("t").icon("heroicon-o-check").render()
    assert "Dyn" in t
    assert Icon.make().size("sm").render()
    assert "width:40px" in Image.make().src("/x.png").width(40).height(40).tooltip("pic").render()
    assert UnorderedList.make().items(lambda **_: ["Z"]).render()
