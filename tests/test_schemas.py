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


def test_layout_skips_hidden_children() -> None:
    hidden = TextInput.make("secret").hidden()
    visible = TextInput.make("public")
    grid = Grid.make().schema([hidden, visible])
    html = grid.render({"public": "ok", "secret": "no"})
    assert "public" in html
    assert 'data-field="secret"' not in html
