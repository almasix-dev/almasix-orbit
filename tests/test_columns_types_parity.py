"""Filament 5 column-type parity APIs (feat/columns-types-parity).

Covers the new column APIs added across every Orbit table column type:
shared Column/TextColumn extras, IconColumn true/false colors, ImageColumn
avatar polish, ColorColumn copy messages, editable-column before/after hooks,
Select/TextInput affix + option controls, TagsColumn limit/separator/color,
ViewColumn url wrapping, and ColumnGroup header alignment/wrap.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Any

import pytest
from almasix.orbit.panels.conduit.hosts import ListRecordsHost
from almasix.orbit.tables import (
    ColorColumn,
    Column,
    ColumnGroup,
    IconColumn,
    ImageColumn,
    SelectColumn,
    Table,
    TagsColumn,
    TextColumn,
    TextInputColumn,
    ViewColumn,
)


@pytest.fixture(autouse=True)
def _clear_configure_using() -> None:
    Column._configure_using.clear()
    yield
    Column._configure_using.clear()


# ---------------------------------------------------------------------------
# Shared Column / TextColumn extras
# ---------------------------------------------------------------------------


def test_icon_position_and_icon_color() -> None:
    before = TextColumn.make("n").icon("heroicon-o-star").render_cell({"n": "x"})
    assert "or-cell-icon-after" not in before

    after = (
        TextColumn.make("n")
        .icon("heroicon-o-star")
        .icon_position("after")
        .icon_color("warning")
        .render_cell({"n": "x"})
    )
    assert "or-cell-icon-after" in after
    assert "or-color-warning" in after
    # Icon renders after the body text when position is "after".
    assert after.index("x") < after.index("or-cell-icon-after")

    callable_color = (
        TextColumn.make("n")
        .icon("heroicon-o-star")
        .icon_color(lambda **_: "danger")
        .render_cell({"n": "x"})
    )
    assert "or-color-danger" in callable_color


def test_size_and_font_family() -> None:
    html = TextColumn.make("n").size("lg").font_family("Fira Code").render_cell({"n": "x"})
    assert "or-text-size-lg" in html
    assert "or-font-family-fira-code" in html
    assert "font-family:Fira Code" in html


def test_limit_custom_end_and_words() -> None:
    col = TextColumn.make("n").limit(4, end="~")
    assert col.resolve_state({"n": "LongValue"}) == "Long~"

    words_col = TextColumn.make("n").words(2)
    assert words_col.resolve_state({"n": "one two three four"}) == "one two…"
    short = TextColumn.make("n").words(5)
    assert short.resolve_state({"n": "one two"}) == "one two"


def test_line_clamp_class() -> None:
    html = TextColumn.make("n").line_clamp(3).render_cell({"n": "hello"})
    assert "or-line-clamp" in html
    assert "or-line-clamp-3" in html


def test_description_position_above_and_below() -> None:
    below = TextColumn.make("n").description("desc note").render_cell({"n": "ZVAL"})
    assert "or-cell-description" in below
    assert "or-cell-description-above" not in below
    assert below.index("ZVAL") < below.index('or-cell-description">')

    above = TextColumn.make("n").description("desc note", position="above").render_cell(
        {"n": "ZVAL"}
    )
    assert "or-cell-description-above" in above
    assert above.index("or-cell-description-above") < above.index("ZVAL")


def test_separator_badge_list_from_list_state() -> None:
    html = (
        TextColumn.make("tags")
        .separator(",")
        .badge()
        .color("success")
        .render_cell({"tags": ["a", "b", "c"]})
    )
    assert html.count("or-badge") == 4  # 1x or-badge-list marker text doesn't count as badge span
    assert "or-badge-list" in html
    assert "or-color-success" in html
    assert ">a<" in html and ">b<" in html and ">c<" in html


def test_separator_badge_list_from_csv_string() -> None:
    html = TextColumn.make("tags").separator(",").badge().render_cell({"tags": "a, b, c"})
    assert "or-badge-list" in html
    assert ">a<" in html and ">b<" in html and ">c<" in html


def test_separator_badge_list_empty_falls_back_to_placeholder() -> None:
    html = (
        TextColumn.make("tags")
        .separator(",")
        .badge()
        .placeholder("None")
        .render_cell({"tags": ""})
    )
    assert "None" in html
    assert "or-cell-placeholder" in html


def test_separator_join_without_badge() -> None:
    html = TextColumn.make("tags").separator(" | ").render_cell({"tags": ["a", "b"]})
    assert "a | b" in html
    assert "or-badge-list" not in html


def test_bulleted_alias_and_default_bullets() -> None:
    bulleted = TextColumn.make("tags").bulleted().render_cell({"tags": ["a", "b"]})
    assert "• a" in bulleted
    assert "<br />" in bulleted

    not_bulleted = TextColumn.make("tags").bulleted(False).render_cell({"tags": ["a", "b"]})
    # Without list_with_line_breaks or separator, falls back to plain str(list).
    assert "or-cell-text" in not_bulleted


def test_time_formatting_variants() -> None:
    col = TextColumn.make("t").time("%H:%M")
    assert col.render_cell({"t": time(13, 45, 30)}).find("13:45") != -1
    assert "13:45" in col.render_cell({"t": "13:45:30"})
    assert "13:45" in col.render_cell({"t": "13:45"})
    # Unparseable text falls back to the raw string.
    assert "not-a-time" in col.render_cell({"t": "not-a-time"})


def test_since_relative_time() -> None:
    col = TextColumn.make("t").since()
    assert "just now" in col.render_cell({"t": datetime.now()})
    five_min_ago = datetime.now() - timedelta(minutes=5)
    assert "minutes ago" in col.render_cell({"t": five_min_ago})
    two_days_ago = datetime.now() - timedelta(days=2)
    assert "days ago" in col.render_cell({"t": two_days_ago.date()})
    in_future = (datetime.now() + timedelta(days=3, hours=2)).isoformat()
    assert "in 3 days" in col.render_cell({"t": in_future})
    assert "bad-timestamp" in col.render_cell({"t": "bad-timestamp"})
    one_hour_ago = datetime.now() - timedelta(hours=1)
    assert "hour" in col.render_cell({"t": one_hour_ago})
    one_week_ago = datetime.now() - timedelta(weeks=1)
    assert "week" in col.render_cell({"t": one_week_ago})
    one_month_ago = datetime.now() - timedelta(days=31)
    assert "month" in col.render_cell({"t": one_month_ago})
    one_year_ago = datetime.now() - timedelta(days=366)
    assert "year" in col.render_cell({"t": one_year_ago})
    fifty_sec_ago = datetime.now() - timedelta(seconds=50)
    assert "second" in col.render_cell({"t": fifty_sec_ago})


def test_copy_message_static_and_callable() -> None:
    static = (
        TextColumn.make("n")
        .copyable()
        .copy_message("Copied!")
        .copy_message_duration(1500)
        .render_cell({"n": "value"})
    )
    assert 'data-copy-message="Copied!"' in static
    assert 'data-copy-message-duration="1500"' in static

    dynamic = (
        TextColumn.make("n")
        .copyable()
        .copy_message(lambda **_: "Dynamic!")
        .render_cell({"n": "value"})
    )
    assert 'data-copy-message="Dynamic!"' in dynamic

    no_message = TextColumn.make("n").copyable().render_cell({"n": "value"})
    assert "data-copy-message=" not in no_message


def test_money_decimal_places() -> None:
    col = TextColumn.make("price").money("USD", decimal_places=0)
    assert "USD 12" in col.render_cell({"price": 12.4})
    precise = TextColumn.make("price").money("USD", decimal_places=3)
    assert "12.500" in precise.render_cell({"price": 12.5})


def test_badge_callable_condition() -> None:
    col = TextColumn.make("status").badge(lambda record: record.get("status") == "on")
    on_html = col.render_cell({"status": "on"})
    assert "or-badge" in on_html
    off_html = col.render_cell({"status": "off"})
    assert 'class="or-cell-text' in off_html
    d = col.to_dict()
    assert d["badge"] is True


# ---------------------------------------------------------------------------
# IconColumn
# ---------------------------------------------------------------------------


def test_icon_column_true_false_color() -> None:
    col = IconColumn.make("on").boolean().true_color("info").false_color("gray")
    assert "or-color-info" in col.render_cell({"on": True})
    assert "or-color-gray" in col.render_cell({"on": False})

    callable_col = IconColumn.make("on").boolean().true_color(lambda **_: "success")
    assert "or-color-success" in callable_col.render_cell({"on": True})

    # Explicit .color() still wins over true/false color.
    overridden = IconColumn.make("on").boolean().true_color("info").color("danger")
    assert "or-color-danger" in overridden.render_cell({"on": True})


# ---------------------------------------------------------------------------
# ImageColumn
# ---------------------------------------------------------------------------


def test_image_column_alt_square_dimensions_ring_overlap_extra_attrs() -> None:
    single = (
        ImageColumn.make("avatar")
        .alt(lambda **_: "Profile photo")
        .square()
        .image_width(40)
        .image_height("3rem")
        .ring(2)
        .extra_img_attributes({"loading": "lazy"})
        .render_cell({"avatar": "http://x/1.png"})
    )
    assert 'alt="Profile photo"' in single
    assert "or-avatar-square" in single
    assert "width:40px" in single
    assert "height:3rem" in single
    assert "--or-avatar-ring:2px" in single
    assert 'loading="lazy"' in single

    stacked = (
        ImageColumn.make("avatars")
        .stacked()
        .overlap("0.6rem")
        .limit(1)
        .alt("Team")
        .render_cell({"avatars": ["http://a", "http://b"]})
    )
    assert "--or-avatar-overlap:0.6rem" in stacked
    assert 'alt="Team"' in stacked
    assert "+1" in stacked


def test_image_column_static_alt_and_no_extra_attrs() -> None:
    html = ImageColumn.make("avatar").alt("Static").render_cell({"avatar": "http://x"})
    assert 'alt="Static"' in html


def test_image_column_square_false_keeps_previous_shape() -> None:
    col = ImageColumn.make("avatar").circular().square(False)
    html = col.render_cell({"avatar": "http://x"})
    assert "or-avatar-circle" in html


# ---------------------------------------------------------------------------
# ColorColumn
# ---------------------------------------------------------------------------


def test_color_column_copy_message() -> None:
    html = (
        ColorColumn.make("c")
        .copyable()
        .copy_message("Color copied")
        .copy_message_duration(900)
        .render_cell({"c": "#123456"})
    )
    assert 'data-copy-message="Color copied"' in html
    assert 'data-copy-message-duration="900"' in html

    dynamic = (
        ColorColumn.make("c")
        .copyable()
        .copy_message(lambda **_: "Dynamic color")
        .render_cell({"c": "#123456"})
    )
    assert 'data-copy-message="Dynamic color"' in dynamic


# ---------------------------------------------------------------------------
# Editable column before/after hooks (wired through ListRecordsHost)
# ---------------------------------------------------------------------------


def test_before_after_state_updated_hooks_via_host() -> None:
    from almasix.orbit.panels.panel import Panel
    from almasix.orbit.panels.resource import Resource

    calls: list[tuple[str, Any]] = []  # type: ignore[name-defined]

    def before(record, state, old):
        calls.append(("before", record.get("id"), old, state))

    def after(record, state, old):
        calls.append(("after", record.get("id"), old, state))

    status_col = (
        TextColumn.make("status").before_state_updated(before).after_state_updated(after)
    )

    class Demo(Resource):
        model = type("X", (), {})
        records_mutable = True
        records = [{"id": 1, "status": "draft"}]

        @classmethod
        def get_records(cls):
            return list(cls.records)

        @classmethod
        def table(cls, table):
            return table.columns([status_col])

    panel = Panel.make("hooks-test").path("/hooks-test")
    Host = ListRecordsHost.bind(panel=panel, resource=Demo)
    host = Host()
    host.mount()
    host.update_column_state("1", "status", "published")

    assert host.records[0]["status"] == "published"
    assert calls == [
        ("before", 1, "draft", "published"),
        ("after", 1, "draft", "published"),
    ]


def test_update_column_state_without_matching_table_column_still_persists() -> None:
    from almasix.orbit.panels.panel import Panel
    from almasix.orbit.panels.resource import Resource

    class Demo(Resource):
        model = type("X", (), {})
        records_mutable = True
        records = [{"id": 1, "title": "A"}]

        @classmethod
        def get_records(cls):
            return list(cls.records)

        @classmethod
        def table(cls, table):
            return table.columns([TextColumn.make("title")])

    panel = Panel.make("hooks-test-2").path("/hooks-test-2")
    Host = ListRecordsHost.bind(panel=panel, resource=Demo)
    host = Host()
    host.mount()
    # "unmapped" isn't a table column -> no hooks fire, but the value still writes.
    host.update_column_state("1", "unmapped", "value")
    assert host.records[0]["unmapped"] == "value"


def test_table_column_for_returns_none_when_resource_unbound() -> None:
    host = ListRecordsHost()
    assert host._table_column_for("anything") is None


# ---------------------------------------------------------------------------
# SelectColumn
# ---------------------------------------------------------------------------


def test_select_column_selectable_placeholder_and_disable_option_when() -> None:
    with_placeholder = (
        SelectColumn.make("status").options({"a": "A", "b": "B"}).render_cell({"status": "a"})
    )
    assert '<option value="">' in with_placeholder

    without_placeholder = (
        SelectColumn.make("status")
        .options({"a": "A", "b": "B"})
        .selectable_placeholder(False)
        .render_cell({"status": "a"})
    )
    assert '<option value="">' not in without_placeholder

    disabled = (
        SelectColumn.make("status")
        .options({"a": "A", "b": "B"})
        .disable_option_when(lambda value, **_: value == "b")
        .render_cell({"status": "a"})
    )
    assert '<option value="b" disabled>' in disabled
    assert '<option value="a" selected>' in disabled


# ---------------------------------------------------------------------------
# TextInputColumn
# ---------------------------------------------------------------------------


def test_text_input_column_type_mode_step_prefix_suffix() -> None:
    html = (
        TextInputColumn.make("amount")
        .type("number")
        .input_mode("decimal")
        .step("0.01")
        .prefix("$")
        .suffix(lambda **_: "USD")
        .render_cell({"amount": "10"})
    )
    assert 'type="number"' in html
    assert 'inputmode="decimal"' in html
    assert 'step="0.01"' in html
    assert "or-input-affix" in html
    assert "or-input-prefix" in html and "$" in html
    assert "or-input-suffix" in html and "USD" in html


def test_text_input_column_callable_prefix_and_suffix() -> None:
    html = (
        TextInputColumn.make("amount")
        .prefix(lambda **_: "€")
        .suffix(lambda **_: None)
        .render_cell({"amount": "10"})
    )
    assert "or-input-prefix" in html and "€" in html
    assert "or-input-suffix" not in html


def test_text_input_column_default_type_omits_type_attr() -> None:
    html = TextInputColumn.make("title").render_cell({"title": "x"})
    assert 'type="' not in html
    assert "or-input-affix" not in html


# ---------------------------------------------------------------------------
# TagsColumn
# ---------------------------------------------------------------------------


def test_tags_column_separator_limit_and_color() -> None:
    html = (
        TagsColumn.make("tags")
        .separator(";")
        .limit(2)
        .color("info")
        .render_cell({"tags": "a;b;c;d"})
    )
    assert "or-color-info" in html
    assert ">a<" in html and ">b<" in html
    assert ">c<" not in html
    assert "+2" in html
    assert "or-badge-more" in html


def test_tags_column_default_separator_and_no_overflow() -> None:
    html = TagsColumn.make("tags").render_cell({"tags": ["a", "b"]})
    assert "or-badge-more" not in html
    assert ">a<" in html and ">b<" in html


# ---------------------------------------------------------------------------
# ViewColumn
# ---------------------------------------------------------------------------


def test_view_column_url_wrap_and_new_tab() -> None:
    html = (
        ViewColumn.make("note")
        .content(lambda **_: "custom")
        .url("/notes/1")
        .open_url_in_new_tab()
        .render_cell({"note": "n"})
    )
    assert '<a class="or-cell-link" href="/notes/1" target="_blank"' in html
    assert "custom" in html

    no_url = ViewColumn.make("note").content(lambda **_: "plain").render_cell({"note": "n"})
    assert "<a " not in no_url

    empty_href = (
        ViewColumn.make("note")
        .content(lambda **_: "plain")
        .url(lambda **_: "")
        .render_cell({"note": "n"})
    )
    assert "<a " not in empty_href


# ---------------------------------------------------------------------------
# ColumnGroup
# ---------------------------------------------------------------------------


def test_column_group_alignment_and_wrap_header() -> None:
    group = (
        ColumnGroup.make("Meta", [TextColumn.make("a"), TextColumn.make("b")])
        .align_end()
        .wrap_header()
    )
    assert group.get_alignment() == "end"
    html = (
        Table.make()
        .columns([TextColumn.make("title"), group])
        .records([{"title": "t", "a": "1", "b": "2"}])
        .render()
    )
    assert "or-th-group or-align-end or-th-wrap" in html


def test_column_group_align_center_default_start() -> None:
    group = ColumnGroup.make("G", [TextColumn.make("a")]).align_center()
    assert group.get_alignment() == "center"
    default_group = ColumnGroup.make("G2", [TextColumn.make("b")])
    assert default_group.get_alignment() == "start"
    assert group.align_start().get_alignment() == "start"


def test_icon_column_icon_callback_maps_state() -> None:
    col = IconColumn.make("status").icon(
        lambda state=None, **_: {
            "ok": "heroicon-o-check",
            "bad": "heroicon-o-x-mark",
        }.get(state, "heroicon-o-question-mark-circle")
    )
    html = col.render_cell({"status": "ok"})
    assert "or-icon-column" in html
    assert "<svg" in html
