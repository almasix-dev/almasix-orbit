"""Default infolist mirrors the form layout and nested entries."""

from __future__ import annotations

from datetime import datetime

from almasix.orbit.forms import (
    Builder,
    Checkbox,
    DatePicker,
    DateTimePicker,
    FileUpload,
    Form,
    Hidden,
    KeyValue,
    MoneyInput,
    MorphToSelect,
    Placeholder,
    Repeater,
    RichEditor,
    Select,
    TagsInput,
    TextInput,
    TimePicker,
    Toggle,
    WeekPicker,
)
from almasix.orbit.forms.components import Block
from almasix.orbit.infolists import Infolist, TextEntry
from almasix.orbit.panels.infolist_from_form import _copy_common, components_from_form
from almasix.orbit.panels.resource import Resource
from almasix.orbit.schemas.layouts import (
    Callout,
    EmptyState,
    Fieldset,
    Flex,
    Grid,
    Group,
    Layout,
    Section,
    Split,
    Tabs,
    Wizard,
)


def _single_column_repeater() -> Repeater:
    field = Repeater.make("tags").schema([TextInput.make("label")])
    field._grid_columns = 1
    return field


def _repeater() -> Repeater:
    field = Repeater.make("links").schema([TextInput.make("url").label("URL")])
    field._grid_columns = 2
    return field


class _LayoutResource(Resource):
    model = type("Row", (), {})

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                Wizard.make("steps")
                .vertical()
                .skippable()
                .start_step(0)
                .steps(
                    {
                        "label": "Profile",
                        "description": "Who they are",
                        "schema": [
                            Grid.make("pair").columns(2).grid_container().schema(
                                [
                                    TextInput.make("name").label("Name").column_span(2),
                                    Hidden.make("secret"),
                                    Placeholder.make("hint").content("ignored"),
                                ]
                            )
                        ],
                    },
                    (
                        "Links",
                        [
                            Split.make("cols").from_("md").schema(
                                [
                                    Fieldset.make("presence")
                                    .label("Online presence")
                                    .schema(
                                        [
                                            _repeater(),
                                        ]
                                    ),
                                    KeyValue.make("meta")
                                    .label("Meta")
                                    .key_label("Attribute")
                                    .value_label("Detail"),
                                ]
                            )
                        ],
                    ),
                ),
                Tabs.make("more")
                .persist_tab()
                .active_tab(0)
                .tabs(
                    {
                        "label": "Notes",
                        "schema": [TextInput.make("bio")],
                        "icon": "heroicon-o-document",
                        "badge": "1",
                    }
                ),
                Section.make("extra")
                .heading("Extra")
                .description("More")
                .icon("heroicon-o-star")
                .collapsible()
                .compact()
                .aside()
                .secondary()
                .schema(
                    [
                        Flex.make("row").from_breakpoint("lg").schema(
                            [Group.make("g").columns(2).schema([TextInput.make("role")])]
                        )
                    ]
                ),
                Callout.make("note").label("Heads up").description("Saved").status("success"),
                Callout.make("rich")
                .label("Rich")
                .color("blue")
                .icon("heroicon-o-bell")
                .icon_color("amber")
                .footer_actions([TextInput.make("ack")])
                .footer_actions_alignment("end"),
                EmptyState.make("none").heading("Empty").description("Nothing").icon("heroicon-o-inbox"),
                EmptyState.make("bare").actions([TextInput.make("go")]),
                Section.make().column_span(2).dense().schema([TextInput.make("plain").label("")]),
                Grid.make().columns(1).schema([TextInput.make()]),
                Flex.make("tight").schema([TextInput.make("tight")]),
                Group.make("loose").schema([TextInput.make("loose")]),
                Split.make("even").schema([TextInput.make("left"), TextInput.make("right")]),
                Layout.make("box").schema([TextInput.make("boxed")]),
                Fieldset.make("bare").label("Bare").contained(False).schema([TextInput.make("site")]),
                Builder.make("blocks").blocks(
                    [
                        Block.make("hero").schema(
                            [TextInput.make("heading").label("Heading"), TextInput.make("type")]
                        ),
                        Block.make("note").schema(
                            [TextInput.make("heading"), TextInput.make("body").label("Body")]
                        ),
                    ]
                ),
                Builder.make("extras").blocks([Block.make("empty")]),
                _single_column_repeater(),
            ]
        )

    @classmethod
    def infolist(cls, infolist: Infolist) -> Infolist:
        return infolist


def test_default_infolist_keeps_form_arrangement_and_nested_entries() -> None:
    info = _LayoutResource.get_infolist()
    html = info.render(
        {
            "name": "Ada",
            "links": [{"url": "https://example.test"}],
            "meta": {"colour": "blue"},
            "bio": "First",
            "role": "admin",
            "blocks": [{"type": "hero", "heading": "Welcome"}],
        }
    )
    assert "or-wizard" in html
    assert 'data-linear="false"' in html
    assert "or-grid-cols-2" in html
    assert "or-fieldset" in html
    assert "Online presence" in html
    assert "or-schema-split-from-md" in html
    assert "or-tabs" in html
    assert "or-section" in html
    assert "Extra" in html
    assert "or-callout" in html
    assert "or-repeatable-item" in html
    assert "https://example.test" in html
    assert "<th>colour</th>" in html
    assert "<td>blue</td>" in html
    assert "Welcome" in html
    assert "hero" in html
    assert "secret" not in html

    explicit = Infolist.make("infolist").schema([TextEntry.make("name")])

    class Custom(_LayoutResource):
        @classmethod
        def infolist(cls, infolist: Infolist) -> Infolist:
            return explicit

    assert Custom.get_infolist() is explicit
    _copy_common(TextInput.make("n"), TextEntry.make("n"))


def test_relationship_entries_show_the_related_record(monkeypatch) -> None:
    import almasix.orbit.forms.select_relationship as rel

    class Team:
        pass

    monkeypatch.setattr(
        rel,
        "load_relationship_options",
        lambda **kwargs: {"1": "Platform"} if kwargs.get("keys") else {},
    )
    manager = Select.make("manager_id").label("Manager").relationship("manager", "name", model=Team)
    manager.resolve_relationship_options = lambda state=None, **ctx: {"1": "Ada Lovelace", "2": "Sam"}
    owner = (
        MorphToSelect.make("owner")
        .label("Owner")
        .title_attribute("title")
        .types(
            [
                "ignored",
                {"type": "other", "label": "Other"},
                {"type": "team", "label": "Team", "model": Team, "title_attribute": "name"},
            ]
        )
        .options_using(lambda type, search: {"9": "Fallback"} if type == "note" else {})
    )
    bare = MorphToSelect.make("bare").types([{"type": "note", "label": ""}]).options_using(
        lambda type, search: {"9": "Fallback"}
    )
    broken = MorphToSelect.make("broken").types([{"type": "note", "label": "Note"}])
    broken.get_options_for_type = lambda morph_type, search="": ["nope"]
    boom = MorphToSelect.make("boom").types([{"type": "note", "label": "Note"}])
    boom.get_options_for_type = lambda morph_type, search="": (_ for _ in ()).throw(RuntimeError("nope"))
    components = components_from_form([manager, owner, bare, broken, boom, Select.make("role")])
    html = Infolist.make("infolist").schema(components).render(
        {
            "manager_id": ["1", "2"],
            "owner": {"type": "team", "id": "1"},
            "bare": '{"type": "note", "id": "9"}',
            "broken": {"type": "note", "id": ""},
            "boom": {"type": "note", "id": "3"},
            "role": "admin",
        }
    )
    assert "Ada Lovelace, Sam" in html
    assert "Team · Platform" in html
    assert "Fallback" in html
    assert "{&#x27;type&#x27;" not in html
    empty = Infolist.make("infolist").schema(components).render(
        {
            "manager_id": "1",
            "owner": "team-1",
            "bare": {"type": "missing", "id": "4"},
            "broken": {"type": "note", "id": "8"},
            "boom": None,
        }
    )
    assert "Ada Lovelace" in empty
    assert "team-1" in empty
    blank = Infolist.make("infolist").schema(components).render({"manager_id": None})
    assert "Ada Lovelace" not in blank


def test_scalar_fields_render_as_formatted_readonly_values() -> None:
    bare_money = MoneyInput.make("budget")
    bare_money._prefix = None
    odd_money = MoneyInput.make("odd").currency("ZZZ")
    odd_money._prefix = lambda: "x"
    components = components_from_form(
        [
            MoneyInput.make("amount").currency("USD"),
            bare_money,
            odd_money,
            MoneyInput.make("bad"),
            TagsInput.make("tags").tag_prefix("#").tag_suffix("!"),
            TagsInput.make("csv"),
            Checkbox.make("terms"),
            Toggle.make("active"),
            DatePicker.make("joined"),
            DateTimePicker.make("reviewed_at").seconds(),
            DateTimePicker.make("opens_on"),
            TimePicker.make("opens_at"),
            TimePicker.make("closes_at").seconds(),
            DatePicker.make("when"),
            WeekPicker.make("sprint"),
            RichEditor.make("body"),
        ]
    )
    html = Infolist.make("infolist").schema(components).render(
        {
            "amount": -1250.5,
            "budget": 10,
            "odd": 3,
            "bad": "nope",
            "tags": ["math", "", "poetry"],
            "csv": "alpha, beta",
            "terms": True,
            "active": "off",
            "joined": "2024-01-05",
            "reviewed_at": "2024-01-05 15:04:09",
            "opens_on": datetime(2024, 3, 2, 9, 5),
            "opens_at": "09:05",
            "closes_at": "21:08:03",
            "when": "soon",
            "sprint": "2024-W02",
            "body": (
                '<p>Hello <a href="https://orbit.test" onclick="alert(1)">there</a></p>'
                "<script><em>hidden</em></script></script><style>x</style>"
                '<img src="javascript:alert(1)" alt="bad">'
                '<img alt src="data:text/html,hi">'
                '<img src="https://cdn.test/a.png" alt="pic"><div>Keep</div>'
            ),
        }
    )
    assert "-$1,250.50" in html
    assert "$10.00" in html
    assert "ZZZ 3.00" in html
    assert "nope" in html
    assert 'class="or-tag-label">math</span>' in html
    assert 'class="or-tag-prefix">#</span>' in html
    assert "alpha" in html and "beta" in html
    assert "or-color-success" in html and ">Yes<" in html
    assert "or-color-danger" in html and ">No<" in html
    assert "January 5, 2024" in html
    assert "03:04:09 PM" in html
    assert "March 2, 2024 09:05 AM" in html
    assert "09:05 AM" in html
    assert "09:08:03 PM" in html
    assert "soon" in html
    assert "2024-W02" in html
    assert 'href="https://orbit.test"' in html
    assert "onclick" not in html and "<script>" not in html and "hidden" not in html
    assert "javascript:" not in html
    assert 'src="https://cdn.test/a.png"' in html
    assert 'alt="pic"' in html

    empty = Infolist.make("infolist").schema(components).render(
        {
            "tags": "[]",
            "terms": None,
            "active": "yes",
            "joined": "   ",
            "opens_at": "03:05 PM",
            "body": None,
            "csv": "",
        }
    )
    assert "or-tag" not in empty
    assert ">No<" in empty and ">Yes<" in empty


def test_color_picker_mirrors_to_color_entry() -> None:
    from almasix.orbit.forms import ColorPicker

    components = components_from_form([ColorPicker.make("accent").label("Accent")])
    html = Infolist.make("infolist").schema(components).render({"accent": "#f1511b"})
    assert "or-color-swatch" in html
    assert "#f1511b" in html
    assert "Accent" in html


def test_avatar_upload_renders_as_an_image() -> None:
    components = components_from_form(
        [
            FileUpload.make("avatar").avatar(),
            FileUpload.make("attachment"),
        ]
    )
    html = Infolist.make("infolist").schema(components).render(
        {
            "avatar": "kitchen-avatars/ada.png",
            "attachment": "notes/readme.txt",
        }
    )
    assert 'class="or-entry-image or-avatar or-avatar-circle"' in html
    assert 'src="/storage/kitchen-avatars/ada.png"' in html
    assert 'data-lightbox="/storage/kitchen-avatars/ada.png"' in html
    assert "width:96px" in html
    assert "notes/readme.txt" in html
    assert html.count("or-avatar-circle") == 1

    linked = Infolist.make("infolist").schema(components).render(
        {
            "avatar": {"url": "https://cdn.test/ada.png"},
            "attachment": "",
        }
    )
    assert 'src="https://cdn.test/ada.png"' in linked
    stored = Infolist.make("infolist").schema(components).render(
        {"avatar": [{"path": "/orbit-uploads/pic.webp"}]}
    )
    assert 'src="/orbit-uploads/pic.webp"' in stored
    blank = Infolist.make("infolist").schema(components).render(
        {"avatar": {"path": ""}, "attachment": None}
    )
    assert "<img" not in blank
    empty_list = Infolist.make("infolist").schema(components).render({"avatar": []})
    assert "<img" not in empty_list


def test_image_upload_renders_and_styled_steps_mirror() -> None:
    from almasix.orbit.schemas.layouts import Tab, WizardStep

    components = components_from_form(
        [
            FileUpload.make("cover").image(),
            FileUpload.make("shots").image(),
            FileUpload.make("preview").image_preview(),
            FileUpload.make("mixed")
            .image_preview()
            .accepted_file_types(["image/png", "text/plain"]),
            FileUpload.make("any_image").image_preview().accepted_file_types(["image/*"]),
            Tabs.make("tabs").tabs(
                Tab.make("account")
                .icon("heroicon-o-user")
                .badge("3")
                .badge_color("success")
                .extra_attributes({"data-k": "v"})
                .schema([TextInput.make("email")]),
                ("Plain", [TextInput.make("plain")]),
            ),
            Wizard.make("wiz").steps(
                WizardStep.make("profile")
                .description("Bio")
                .icon("heroicon-o-user")
                .completed_icon("heroicon-o-check")
                .extra_attributes({"data-s": "1"})
                .schema([TextInput.make("name")])
            ),
        ]
    )
    html = Infolist.make("infolist").schema(components).render(
        {
            "cover": "covers/a.png",
            "shots": ["", "covers/a.png", "covers/b.png"],
            "preview": "files/a.bin",
            "mixed": "files/b.bin",
            "any_image": "covers/c.png",
            "email": "a@b.c",
            "name": "Ada",
        }
    )
    assert 'data-lightbox="/storage/covers/a.png"' in html
    assert "or-entry-gallery" in html
    assert 'src="/storage/covers/b.png"' in html
    assert 'src="/storage/covers/c.png"' in html
    assert "files/a.bin" in html and "files/b.bin" in html
    assert "or-avatar-circle" not in html
    assert "or-tab-icon" in html and "or-nav-badge-success" in html
    assert 'data-k="v"' in html and 'data-s="1"' in html
    assert "Bio" in html


def test_nested_entries_accept_json_strings() -> None:
    components = components_from_form(
        [
            KeyValue.make("meta"),
            Repeater.make("links").schema([TextInput.make("url")]),
        ]
    )
    html = Infolist.make("infolist").schema(components).render(
        {
            "meta": '{"team": "core"}',
            "links": '[{"url": "https://orbit.test"}]',
        }
    )
    assert "team" in html and "core" in html
    assert "https://orbit.test" in html

    blank = Infolist.make("infolist").schema(components).render({"meta": "  ", "links": "hello"})
    assert "or-key-value" in blank
    broken = Infolist.make("infolist").schema(components).render(
        {"meta": "{not-json", "links": "nope"}
    )
    assert "or-key-value" in broken
    assert "No items" in broken
