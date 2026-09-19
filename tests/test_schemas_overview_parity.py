"""Filament-parity coverage for schemas overview + layout/prime APIs."""

from __future__ import annotations

from almasix.orbit.forms.components import TextInput
from almasix.orbit.schemas.layouts import Fieldset, Section
from almasix.orbit.schemas.primes import Image, Text
from almasix.orbit.schemas.schema import Schema


def test_schema_operation_defer_and_configure_using() -> None:
    Schema._configure_using.clear()
    Schema.configure_using(lambda s: s.columns(3))
    schema = (
        Schema.make("user")
        .operation("edit")
        .defer_loading()
        .schema(
            [
                TextInput.make("name").visible(
                    lambda operation=None, **_: operation == "edit"
                )
            ]
        )
        .state({"name": "Ada"})
    )
    assert schema.get_operation() == "edit"
    assert schema._columns == 3
    html = schema.render()
    assert 'data-defer="true"' in html
    assert "Ada" in html
    assert "or-schema-cols-3" in html
    d = schema.to_dict()
    assert d["operation"] == "edit" and d["defer_loading"] is True
    Schema._configure_using.clear()


def test_section_secondary_and_fieldset_contained() -> None:
    section = (
        Section.make("meta")
        .heading("Meta")
        .secondary()
        .schema([TextInput.make("x")])
    )
    assert "or-section-secondary" in section.render({"x": "1"})

    bare = Fieldset.make("c").label("Contact").contained(False).schema([TextInput.make("y")])
    assert "or-fieldset-bare" in bare.render({"y": "2"})
    wrapped = Fieldset.make("c").label("Contact").schema([TextInput.make("y")])
    assert "or-fieldset-bare" not in wrapped.render({"y": "2"})


def test_prime_font_family_and_image_align() -> None:
    text = Text.make().content("Hi").font_family("Georgia, serif").weight("bold")
    assert "font-family:Georgia" in text.render()
    img = (
        Image.make()
        .src("/a.png")
        .align_center()
        .image_size(48)
    )
    html = img.render()
    assert "or-align-center" in html
    assert Image.make().src("/a.png").align_start().render()
    assert "or-align-end" in Image.make().src("/a.png").align_end().render()
