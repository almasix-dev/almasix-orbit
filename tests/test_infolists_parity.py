"""Filament 5 parity coverage for almasix.orbit.infolists."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from datetime import time as dt_time

from almasix.orbit.infolists.components import (
    CodeEntry,
    ColorEntry,
    Entry,
    IconEntry,
    ImageEntry,
    KeyValueEntry,
    RepeatableEntry,
    TextEntry,
    ViewEntry,
    _attrs_to_html,
    _copyable_wrap,
    _relative_time,
    _simple_markdown,
    _truncate_words,
    dot_get,
)
from almasix.orbit.infolists.infolist import Infolist
from almasix.orbit.schemas.layouts import Section


def test_dot_get_and_helpers() -> None:
    assert dot_get({"author": {"name": "Ada"}}, "author.name") == "Ada"
    assert dot_get(type("R", (), {"author": type("A", (), {"name": "Bob"})()})(), "author.name") == "Bob"
    assert dot_get({"a": None}, "a.b") is None
    assert "**hi**" in _simple_markdown("**hi**") or "<strong>hi</strong>" in _simple_markdown("**hi**")
    assert _truncate_words("one two three", 2, "…") == "one two…"
    assert _truncate_words("one", 5, "…") == "one"
    wrap = _copyable_wrap("<b>x</b>", "x", message="Copied!", duration=1500)
    assert "or-copyable" in wrap and "or-copy-btn" in wrap and "Copied!" in wrap
    assert "ago" in _relative_time(datetime(2000, 1, 1)) or "just now" in _relative_time(datetime.now())
    # date (not datetime), invalid parse, just-now, second-scale past/future
    assert "ago" in _relative_time(date(2000, 1, 1))
    assert _relative_time("not-a-timestamp") == "not-a-timestamp"
    assert _relative_time(datetime.now()) == "just now"
    past_secs = _relative_time(datetime.now() - timedelta(seconds=50))
    assert "second" in past_secs and "ago" in past_secs
    future_secs = _relative_time(datetime.now() + timedelta(seconds=50))
    assert "in" in future_secs and "second" in future_secs
    assert "in" in _relative_time(datetime.now() + timedelta(days=2))
    # Singular unit via year boundary (count == 1)
    assert "1 year ago" in _relative_time(datetime.now() - timedelta(days=400)) or "year" in _relative_time(
        datetime.now() - timedelta(days=400)
    )
    assert 'disabled' in _attrs_to_html({"disabled": True, "hidden": False, "skip": None, "data-x": "1"})
    assert 'data-x="1"' in _attrs_to_html({"disabled": True, "hidden": False, "skip": None, "data-x": "1"})


def test_dot_state_placeholder_vs_default() -> None:
    record = {"author": {"name": "Ada"}}
    assert TextEntry.make("author.name").resolve_state(record) == "Ada"
    assert TextEntry.make("missing").default("fallback").resolve_state({}) == "fallback"
    empty = TextEntry.make("missing").placeholder("n/a").render(record={})
    assert "or-entry-placeholder" in empty and "n/a" in empty
    # Placeholder must not become Image/Color real state
    img = ImageEntry.make("photo").placeholder("no photo").render(record={})
    assert "or-entry-placeholder" in img and "<img" not in img
    color = ColorEntry.make("hex").placeholder("none").render(record={})
    assert "or-entry-placeholder" in color and "or-color-swatch" not in color
    custom = TextEntry.make("x").state(lambda record: "custom").resolve_state({"x": "ignored"})
    assert custom == "custom"


def test_copyable_markdown_html_prose_formatters() -> None:
    record = {
        "slug": "hello-world",
        "md": "**bold**",
        "raw": "<em>hi</em>",
        "body": "long prose",
        "when": "2024-06-15T12:30:00",
        "price": 1999,
        "qty": 3.5,
        "bio": "abcdefghij",
    }
    copy = TextEntry.make("slug").copyable().copy_message("Copied").copy_message_duration(2000)
    html = copy.render(record=record)
    assert "or-copyable" in html and "or-copy-btn" in html and 'data-copy="hello-world"' in html

    assert "<strong>bold</strong>" in TextEntry.make("md").markdown().render(record=record)
    assert "<em>hi</em>" in TextEntry.make("raw").html().render(record=record)
    assert "or-prose" in TextEntry.make("body").prose().render(record=record)

    dt = TextEntry.make("when").date_time("%Y/%m/%d %H:%M").render(record=record)
    assert "2024/06/15 12:30" in dt
    assert "USD 19.99" in TextEntry.make("price").money("USD", divide_by=100).render(record=record)
    assert "3.50" in TextEntry.make("qty").numeric(2).render(record=record)
    assert "abc…" in TextEntry.make("bio").limit(3).render(record=record)
    assert "or-line-clamp-2" in TextEntry.make("bio").line_clamp(2).render(record=record)
    assert "or-font-bold" in TextEntry.make("slug").weight("bold").render(record=record)
    assert "or-text-size-lg" in TextEntry.make("slug").size("lg").render(record=record)
    assert 'target="_blank"' in TextEntry.make("slug").url("/x").open_url_in_new_tab().render(record=record)


def test_badge_list_separator_and_slots() -> None:
    record = {"tags": ["a", "b"], "csv": "x,y"}
    listed = TextEntry.make("tags").separator(", ").badge().render(record=record)
    assert "or-badge-list" in listed and "or-badge" in listed
    bullets = TextEntry.make("tags").bulleted().render(record=record)
    assert "• a" in bullets or "<br" in bullets
    joined = TextEntry.make("tags").separator(" | ").render(record=record)
    assert "a | b" in joined
    chrome = (
        TextEntry.make("tags")
        .helper_text("help")
        .hint("tip")
        .hint_icon("heroicon-o-information-circle")
        .above_label("AL")
        .below_content("BC")
        .prefix_action("edit")
        .suffix_action("more")
        .align_end()
        .tooltip("hover")
        .extra_attributes({"data-x": "1"})
        .extra_entry_wrapper_attributes({"data-y": "2"})
        .hidden_label()
        .render(record=record)
    )
    assert "or-helper" in chrome and "or-hint" in chrome
    assert "or-above-label" in chrome and "or-below-content" in chrome
    assert 'wire:click="mountAction(\'edit\')"' in chrome
    assert "or-align-end" in chrome and 'title="hover"' in chrome
    assert 'data-x="1"' in chrome and 'data-y="2"' in chrome
    assert "or-sr-only" in chrome


def test_icon_entry_boolean() -> None:
    yes = IconEntry.make("active").boolean().true_icon("heroicon-o-check").render(record={"active": True})
    no = IconEntry.make("active").boolean().false_color("warning").render(record={"active": False})
    assert "or-icon-entry" in yes and "or-color-success" in yes
    assert "or-color-warning" in no
    sized = IconEntry.make("icon").size("lg").render(record={"icon": "heroicon-o-star"})
    assert "or-icon-size-lg" in sized


def test_image_entry_circular_stacked() -> None:
    single = (
        ImageEntry.make("photo")
        .circular()
        .width(40)
        .height(40)
        .alt("Avatar")
        .extra_img_attributes({"loading": "lazy"})
        .render(record={"photo": "/a.png"})
    )
    assert "or-entry-image" in single and "or-avatar-circle" in single
    assert 'alt="Avatar"' in single and 'loading="lazy"' in single
    stacked = (
        ImageEntry.make("photos")
        .stacked()
        .limit(2)
        .overlap(8)
        .ring(2)
        .render(record={"photos": ["/a.png", "/b.png", "/c.png"]})
    )
    assert "or-avatar-stack" in stacked and "+1" in stacked
    defaulted = ImageEntry.make("photo").default_image_url("/fallback.png").render(record={})
    assert "/fallback.png" in defaulted


def test_code_entry_grammar_json() -> None:
    code = CodeEntry.make("src").grammar("python").copyable().render(record={"src": "print(1)"})
    assert 'data-language="python"' in code and "or-code" in code and "or-copyable" in code
    payload = CodeEntry.make("meta").render(record={"meta": {"a": 1, "b": [2]}})
    assert "&quot;a&quot;: 1" in payload and "\n" in payload


def test_key_value_labels() -> None:
    html = (
        KeyValueEntry.make("meta")
        .key_label("Property")
        .value_label("Content")
        .render(record={"meta": {"k": "v"}})
    )
    assert "Property" in html and "Content" in html and "<thead>" in html


def test_repeatable_columns_and_view_entry() -> None:
    rep = (
        RepeatableEntry.make("items")
        .columns(2)
        .contained(False)
        .schema([TextEntry.make("name")])
        .render(record={"items": [{"name": "A"}, {"name": "B"}]})
    )
    assert "or-repeatable-cols-2" in rep and "or-repeatable-bare" in rep
    assert "A" in rep and "B" in rep

    view = ViewEntry.make("custom").content(lambda record, state: f"<b>{state}</b>").render(
        record={"custom": "X"}
    )
    assert "<b>X</b>" in view and "or-entry" in view
    view2 = ViewEntry.make("custom").view("<i>static</i>").hidden_label().render(record={})
    assert "<i>static</i>" in view2 and "or-sr-only" in view2


def test_infolist_columns_and_layouts() -> None:
    html = (
        Infolist.make()
        .columns(2)
        .schema(
            [
                TextEntry.make("name"),
                Section.make("meta").schema([TextEntry.make("role")]),
                TextEntry.make("hidden").hidden(),
            ]
        )
        .render({"name": "Ada", "role": "dev", "hidden": "no"})
    )
    assert "or-infolist or-infolist-cols-2" in html
    assert "Ada" in html and "dev" in html
    assert "no" not in html or "hidden" not in html.lower()


def test_entry_date_time_time_since_words() -> None:
    assert "14:30" in TextEntry.make("t").time().render(record={"t": "14:30:00"})
    assert "ago" in TextEntry.make("t").since().render(record={"t": "2000-01-01T00:00:00"}) or "just now" in TextEntry.make(
        "t"
    ).since().render(record={"t": datetime.now().isoformat()})
    assert "one two…" in TextEntry.make("w").words(2).render(record={"w": "one two three four"})
    assert Entry.make("name").resolve_state(type("R", (), {"name": "X"})()) == "X"


def test_text_entry_format_edge_cases() -> None:
    assert TextEntry.make("x").money()._format_display_value(None) == ""
    assert TextEntry.make("x").bulleted()._format_display_value("solo") == "solo"
    assert "abc" in TextEntry.make("p").money().render(record={"p": "abc"})
    assert "xyz" in TextEntry.make("n").numeric().render(record={"n": "xyz"})
    assert "5" in TextEntry.make("n").numeric().render(record={"n": 5})
    assert "3.5" in TextEntry.make("n").numeric().render(record={"n": 3.5})
    assert "2024-06-15" in TextEntry.make("d").date().render(record={"d": datetime(2024, 6, 15, 12, 0)})
    assert "2024-01-02" in TextEntry.make("d").date().render(record={"d": date(2024, 1, 2)})
    assert "14:30" in TextEntry.make("t").time("%H:%M").render(record={"t": dt_time(14, 30)})
    assert "nope" in TextEntry.make("t").time().render(record={"t": "nope"})


def test_text_entry_chrome_callables_and_slots() -> None:
    record = {"name": "Ada", "tags": "a, b", "bio": "hello"}
    html = (
        TextEntry.make("name")
        .badge(lambda record, state: True)
        .color(lambda record, state: "danger")
        .icon(lambda record, state: "heroicon-o-star")
        .icon_position("after")
        .icon_color(lambda record, state: "warning")
        .wrap()
        .font_family("Georgia")
        .align("start")
        .align_start()
        .align_center()
        .below_label("BL")
        .before_label("BeL")
        .after_label("AfL")
        .above_content("AC")
        .before_content("BC")
        .after_content("AfC")
        .below_label(lambda record, state: "")
        .hint_icon("heroicon-o-information-circle")
        .copyable()
        .copy_message(lambda record, state: "copied!")
        .render(record=record)
    )
    assert "or-badge" in html and "or-color-danger" in html
    assert "or-entry-icon-after" in html and "or-color-warning" in html
    assert "or-entry-wrap" in html and "or-font-family-georgia" in html
    assert "or-align-center" in html
    assert "or-before-label" in html and "or-after-label" in html
    assert "or-above-content" in html and "or-before-content" in html and "or-after-content" in html
    assert "or-hint" in html and "or-copyable" in html and "copied!" in html

    badges = TextEntry.make("tags").separator(",").badge().render(record=record)
    assert "or-badge-list" in badges and "or-badge" in badges

    empty_icon = TextEntry.make("name").icon(lambda record, state: "").render(record=record)
    assert "or-entry-icon" not in empty_icon


def test_icon_entry_edges() -> None:
    falsy = (
        IconEntry.make("active")
        .boolean()
        .false_icon("heroicon-o-x-circle")
        .true_color("info")
        .false_color(lambda record, state: "gray")
        .render(record={"active": False})
    )
    assert "or-color-gray" in falsy
    truthy = (
        IconEntry.make("active")
        .boolean()
        .true_color(lambda record, state: "primary")
        .render(record={"active": True})
    )
    assert "or-color-primary" in truthy
    placeholder = IconEntry.make("missing").placeholder("none").render(record={})
    assert "or-entry-placeholder" in placeholder and "none" in placeholder
    from_icon = IconEntry.make("flag").icon("heroicon-o-flag").render(record={"flag": True})
    assert "or-icon-entry" in from_icon


def test_image_entry_edges() -> None:
    squared = (
        ImageEntry.make("photo")
        .square()
        .size(48)
        .image_size("lg")
        .extra_img_attributes({"draggable": False, "data-ready": True, "data-skip": None})
        .render(record={"photo": "/a.png"})
    )
    assert "or-avatar-square" in squared and "or-avatar-lg" in squared
    assert "data-ready" in squared

    sized_int = ImageEntry.make("photo").size(32).render(record={"photo": "/a.png"})
    assert "width:32px" in sized_int

    stacked_no_overlap = (
        ImageEntry.make("photos")
        .stacked()
        .limit(2)
        .render(record={"photos": ["/a.png", "/b.png", "/c.png"]})
    )
    assert "or-avatar-stack" in stacked_no_overlap and "+1" in stacked_no_overlap
    assert "--or-avatar-overlap" not in stacked_no_overlap


def test_color_code_view_and_infolist_operation() -> None:
    empty_color = ColorEntry.make("hex").render(record={})
    assert "#000000" in empty_color and "or-color-swatch" in empty_color
    copy_color = (
        ColorEntry.make("hex")
        .copyable()
        .copy_message(lambda record, state: "swatch!")
        .render(record={"hex": "#ff0000"})
    )
    assert "or-copyable" in copy_color and "swatch!" in copy_color
    static_copy = ColorEntry.make("hex").copyable().copy_message("static").render(record={"hex": "#00ff00"})
    assert "or-copyable" in static_copy and "static" in static_copy

    empty_code = CodeEntry.make("src").render(record={"src": None})
    assert "or-code" in empty_code
    copy_code = (
        CodeEntry.make("src")
        .copyable()
        .copy_message(lambda record, state: "code!")
        .render(record={"src": "x = 1"})
    )
    assert "or-copyable" in copy_code and "code!" in copy_code

    none_view = ViewEntry.make("custom").view(lambda record, state: None).render(record={"custom": "x"})
    assert "or-entry" in none_view
    bare_view = ViewEntry.make("custom").render(record={"custom": "x"})
    assert "or-entry" in bare_view

    seen: list[str] = []

    def _capture_op(record=None, operation=None, **_kwargs):
        if operation is not None:
            seen.append(str(operation))
        return True

    html = (
        Infolist.make()
        .operation("view")
        .schema([TextEntry.make("name").visible(_capture_op)])
        .render({"name": "Ada"})
    )
    assert "Ada" in html and "view" in seen


def test_remaining_infolist_branches() -> None:
    # format_state_using
    formatted = TextEntry.make("n").format_state_using(lambda v: f"#{v}").render(record={"n": 7})
    assert "#7" in formatted

    # date string with T / bare date / invalid
    assert "2024-06-15" in TextEntry.make("d").date().render(record={"d": "2024-06-15T12:30:00"})
    assert "2024-06-15" in TextEntry.make("d").date().render(record={"d": "2024-06-15"})
    assert "bad-date" in TextEntry.make("d").date().render(record={"d": "bad-date"})

    # hint text without icon (497→499 false branch)
    hint_only = TextEntry.make("name").hint("tip only").render(record={"name": "A"})
    assert "or-hint" in hint_only and "tip only" in hint_only

    # empty state without placeholder (text="")
    empty = TextEntry.make("missing").render(record={})
    assert "or-entry" in empty

    # icon with static (non-callable) icon_color
    iconed = TextEntry.make("name").icon("heroicon-o-star").icon_color("primary").render(record={"name": "A"})
    assert "or-entry-icon" in iconed and "or-color-primary" in iconed

    # IconEntry empty without placeholder
    bare_icon = IconEntry.make("missing").render(record={})
    assert "or-icon-entry" in bare_icon

    # ImageEntry square(False) keeps circular; empty with no placeholder/default
    not_square = ImageEntry.make("photo").circular().square(False).render(record={"photo": "/a.png"})
    assert "or-avatar-circle" in not_square
    empty_img = ImageEntry.make("photo").render(record={})
    assert "or-entry" in empty_img and "<img" not in empty_img

    # KeyValueEntry non-dict state
    kv = KeyValueEntry.make("meta").render(record={"meta": "not-a-dict"})
    assert "or-key-value" in kv

    # using_placeholder with text=None path inside _render_formatted_value
    ph = TextEntry.make("x")._render_formatted_value({}, None, using_placeholder=True, text=None)
    assert "or-entry-placeholder" in ph
