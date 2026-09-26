"""Tests for almasix.orbit.infolists."""

from __future__ import annotations

from almasix.orbit.infolists.components import (
    CodeEntry,
    ColorEntry,
    Entry,
    IconEntry,
    ImageEntry,
    KeyValueEntry,
    RepeatableEntry,
    TextEntry,
)
from almasix.orbit.infolists.infolist import Infolist


def test_entries_and_infolist_render() -> None:
    record = {
        "name": "Ada",
        "icon": "heroicon-o-check",
        "photo": "/a.png",
        "color": "#f1511b",
        "code": "print(1)",
        "meta": {"a": 1},
    }
    entry = (
        TextEntry.make("name")
        .format_state_using(lambda v: v.upper())
        .url("/u")
        .copyable()
        .badge()
        .color("primary")
        .icon("heroicon-o-users")
        .date_time()
        .markdown()
        .prose()
    )
    assert entry.resolve_state(record) == "ADA"
    assert "or-badge" in entry.render(record=record)
    assert "or-entry" in IconEntry.make("icon").render(record=record)
    assert "or-entry-image" in ImageEntry.make("photo").render(record=record)
    stacked = ImageEntry.make("photo").stacked().lightbox().render(
        record={"photo": ["/a.png", "/b.png"]}
    )
    assert "data-lightbox-gallery" in stacked
    assert "/a.png" in stacked and "/b.png" in stacked
    static = ImageEntry.make("photo").lightbox(False).render(record={"photo": "/a.png"})
    assert "or-lightbox-trigger" not in static and "or-entry-image" in static
    plain_stack = ImageEntry.make("photo").stacked().lightbox(False).render(
        record={"photo": ["/a.png", "/b.png"]}
    )
    assert "or-avatar-stack" in plain_stack and "or-lightbox-trigger" not in plain_stack
    gallery = ImageEntry.make("photo").gallery().lightbox().render(
        record={"photo": ["/a.png", "/b.png"]}
    )
    assert "or-entry-gallery" in gallery and "data-lightbox-gallery" in gallery
    assert ImageEntry.make("photo").render(record={"photo": ""})
    assert "or-color-swatch" in ColorEntry.make("color").render(record=record)
    assert "<pre" in CodeEntry.make("code").render(record=record)
    assert "or-key-value" in KeyValueEntry.make("meta").render(record=record)
    assert KeyValueEntry.make("meta").render(record={"meta": None})
    rep = RepeatableEntry.make("items").schema([TextEntry.make("name")])
    assert len(rep._schema) == 1
    assert Entry.make("name").resolve_state(type("R", (), {"name": "X"})()) == "X"

    infolist = Infolist.make().schema([TextEntry.make("name"), TextEntry.make("missing").hidden()])
    html = infolist.render(record)
    assert "or-infolist" in html and "Ada" in html
    assert 'data-field' not in html or "missing" not in html
    assert "Ada" in Infolist.make().schema([TextEntry.make("name")]).state(record).render()
