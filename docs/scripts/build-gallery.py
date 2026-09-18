#!/usr/bin/env python3
"""Build a static HTML gallery from Orbit render() output for screenshot capture.

Shot IDs use ``{section}/{name}`` and become files under
``docs/public/examples/{light|dark}/{section}/{name}.png``.
"""

from __future__ import annotations

from pathlib import Path

from gallery_variants import build_form_variants, build_schema_variants

from almasix.orbit.actions.action import CreateAction, EditAction
from almasix.orbit.forms.components import (
    Block,
    Builder,
    Checkbox,
    CheckboxList,
    ColorPicker,
    DatePicker,
    DateTimePicker,
    FileUpload,
    KeyValue,
    MoneyInput,
    MorphToSelect,
    Radio,
    Repeater,
    RichEditor,
    Select,
    TagsInput,
    TextInput,
    Textarea,
    TimePicker,
    Toggle,
    ToggleButtons,
    ViewField,
)
from almasix.orbit.forms.form import Form
from almasix.orbit.panels.auth import Login
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.schemas.layouts import (
    Callout,
    EmptyState,
    Fieldset,
    Flex,
    Grid as SchemaGrid,
    Group as SchemaGroup,
    Section,
    Split as SchemaSplit,
    Tabs,
    Wizard,
)
from almasix.orbit.schemas.primes import Icon, Image, Text, UnorderedList
from almasix.orbit.tables.columns import (
    BooleanColumn,
    CheckboxColumn,
    ColorColumn,
    ColumnGroup,
    IconColumn,
    ImageColumn,
    SelectColumn,
    TagsColumn,
    TextColumn,
    TextInputColumn,
    ToggleColumn,
    ViewColumn,
)
from almasix.orbit.tables.filters import SelectFilter
from almasix.orbit.tables.grouping import Group
from almasix.orbit.tables.layout import Grid, Panel as LayoutPanel, Split, Stack, View
from almasix.orbit.tables.summaries import Average, Count, Sum
from almasix.orbit.tables.table import Table

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT.parent / "packages/panels/src/almasix/orbit/resources/css/orbit.css").read_text(
    encoding="utf-8"
)
OUT = ROOT / "public" / "examples" / "gallery.html"

# Canonical shot registry — keep capture scripts & docs in sync with these IDs.
SHOTS: list[tuple[str, str]] = [
    ("forms/overview", "Forms overview"),
    ("forms/text-input", "Text input"),
    ("forms/select", "Select"),
    ("forms/textarea", "Textarea"),
    ("forms/checkbox-toggle", "Checkbox + toggle"),
    ("forms/date-pickers", "Date pickers"),
    ("forms/file-upload", "File upload"),
    ("forms/radio-checkbox-list", "Radio + checkbox list"),
    ("forms/tags-input", "Tags input"),
    ("forms/color-money", "Color + money"),
    ("forms/rich-editor", "Rich editor"),
    ("forms/key-value", "Key-value"),
    ("forms/repeater", "Repeater"),
    ("forms/builder", "Builder"),
    ("forms/toggle-buttons", "Toggle buttons"),
    ("forms/morph-to-select", "Morph-to select"),
    # TextInput variants
    ("forms/text-input/basic", "Text input — basic"),
    ("forms/text-input/email", "Text input — email"),
    ("forms/text-input/password", "Text input — password"),
    ("forms/text-input/url", "Text input — url"),
    ("forms/text-input/tel", "Text input — tel"),
    ("forms/text-input/numeric", "Text input — numeric"),
    ("forms/text-input/prefix", "Text input — prefix"),
    ("forms/text-input/suffix", "Text input — suffix"),
    ("forms/text-input/prefix-icon", "Text input — prefix icon"),
    ("forms/text-input/suffix-icon", "Text input — suffix icon"),
    ("forms/text-input/required", "Text input — required"),
    ("forms/text-input/disabled", "Text input — disabled"),
    ("forms/text-input/readonly", "Text input — readonly"),
    ("forms/text-input/copyable", "Text input — copyable"),
    ("forms/text-input/mask", "Text input — mask"),
    ("forms/text-input/datalist", "Text input — datalist"),
    ("forms/text-input/with-hint", "Text input — with hint"),
    # Select / textarea / checkbox / toggle
    ("forms/select/basic", "Select — basic"),
    ("forms/select/searchable", "Select — searchable"),
    ("forms/select/multiple", "Select — multiple"),
    ("forms/textarea/basic", "Textarea — basic"),
    ("forms/textarea/rows", "Textarea — rows"),
    ("forms/checkbox/basic", "Checkbox — basic"),
    ("forms/toggle/basic", "Toggle — basic"),
    # Date / time pickers
    ("forms/date-picker/basic", "Date picker — basic"),
    ("forms/date-picker/min-max", "Date picker — min/max"),
    ("forms/date-time-picker/basic", "Date time picker — basic"),
    ("forms/date-time-picker/min-max", "Date time picker — min/max"),
    ("forms/time-picker/basic", "Time picker — basic"),
    ("forms/time-picker/min-max", "Time picker — min/max"),
    # File upload
    ("forms/file-upload/basic", "File upload — basic"),
    ("forms/file-upload/image", "File upload — image"),
    ("forms/file-upload/avatar", "File upload — avatar"),
    # Radio / checkbox list
    ("forms/radio/basic", "Radio — basic"),
    ("forms/radio/with-descriptions", "Radio — with descriptions"),
    ("forms/radio/columns", "Radio — columns"),
    ("forms/checkbox-list/basic", "Checkbox list — basic"),
    ("forms/checkbox-list/bulk-toggle", "Checkbox list — bulk toggle"),
    # Tags / color / money
    ("forms/tags-input/basic", "Tags input — basic"),
    ("forms/tags-input/suggestions", "Tags input — suggestions"),
    ("forms/color-picker/basic", "Color picker — basic"),
    ("forms/money-input/usd", "Money input — USD"),
    ("forms/money-input/eur", "Money input — EUR"),
    # Editors / key-value / repeater / builder
    ("forms/rich-editor/basic", "Rich editor — basic"),
    ("forms/markdown-editor/basic", "Markdown editor — basic"),
    ("forms/key-value/basic", "Key-value — basic"),
    ("forms/key-value/populated", "Key-value — populated"),
    ("forms/repeater/basic", "Repeater — basic"),
    ("forms/repeater/cloneable-reorderable", "Repeater — cloneable + reorderable"),
    ("forms/repeater/table", "Repeater — table layout"),
    ("forms/builder/basic", "Builder — basic"),
    ("forms/toggle-buttons/basic", "Toggle buttons — basic"),
    ("forms/morph-to-select/basic", "Morph-to select — basic"),
    ("forms/placeholder/basic", "Placeholder — basic"),
    ("forms/hidden/basic", "Hidden — note"),
    ("forms/one-time-code-input/basic", "One-time code — basic"),
    ("forms/view-field/basic", "View field — basic"),
    ("forms/slider/basic", "Slider — basic"),
    ("tables/overview", "Tables overview"),
    ("tables/money", "Money / currency"),
    ("tables/text-features", "Text column features"),
    ("tables/icon-boolean", "Icon + boolean"),
    ("tables/image-color", "Image + color"),
    ("tables/editable", "Editable columns"),
    ("tables/tags-view", "Tags + view"),
    ("tables/column-group", "Column group"),
    ("tables/layout", "Cell layouts"),
    ("tables/filters", "Filters chrome"),
    ("tables/summaries", "Summaries"),
    ("tables/grouping", "Grouped rows"),
    ("tables/actions", "Row actions"),
    ("tables/empty", "Empty state"),
    ("schemas/callout", "Callout"),
    ("schemas/empty-state", "Empty state"),
    ("schemas/primes-text", "Text prime"),
    ("schemas/section", "Section"),
    ("schemas/tabs", "Tabs"),
    ("schemas/wizard", "Wizard"),
    ("schemas/grid-flex", "Grid + flex"),
    ("schemas/group-split", "Group + split"),
    ("schemas/fieldset", "Fieldset"),
    ("schemas/primes-all", "All primes"),
    # Schema layout variants
    ("schemas/section/basic", "Section — basic"),
    ("schemas/section/collapsible", "Section — collapsible"),
    ("schemas/section/compact", "Section — compact"),
    ("schemas/tabs/basic", "Tabs — basic"),
    ("schemas/tabs/with-badges", "Tabs — with badges"),
    ("schemas/wizard/basic", "Wizard — basic"),
    ("schemas/grid/basic", "Grid — basic"),
    ("schemas/flex/basic", "Flex — basic"),
    ("schemas/group/basic", "Group — basic"),
    ("schemas/split/basic", "Split — basic"),
    ("schemas/fieldset/basic", "Fieldset — basic"),
    ("schemas/callout/info", "Callout — info"),
    ("schemas/callout/danger", "Callout — danger"),
    ("schemas/callout/success", "Callout — success"),
    ("schemas/empty-state/basic", "Empty state — basic"),
    ("schemas/primes/text", "Prime — text"),
    ("schemas/primes/icon", "Prime — icon"),
    ("schemas/primes/image", "Prime — image"),
    ("schemas/primes/list", "Prime — list"),
    ("panels/shell", "Panel shell"),
    ("users/login", "Login"),
]


class DemoResource(Resource):
    model = type("Post", (), {"id": 1, "title": "Hello"})
    navigation_label = "Posts"
    navigation_group = "Content"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title").required()])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title").searchable()])


def shot(shot_id: str, label: str, html: str) -> str:
    """One capturable frame. Title is outside the shot so PNGs stay clean."""
    return (
        f'<section class="gallery-section" data-section="{shot_id.split("/", 1)[0]}">'
        f'<p class="gallery-label">{label} <code>{shot_id}</code></p>'
        f'<div class="or-shot" data-shot="{shot_id}">{html}</div>'
        f"</section>"
    )


def shell_fragment(panel: Panel, content: str, *, active_path: str | None = None) -> str:
    """Panel chrome without full HTML document, scripts, or action modal host.

    Nesting a full ``render_shell()`` document inside the gallery loads Alpine from
    CDN while ``orbit.js`` 404s — the confirm modal then paints open over every shot.
    """
    ctx = panel.menu_layout_context(active_path=active_path)
    sidebar = panel._render_sidebar(ctx, panel._sidebar_collapsible)
    topbar = panel._render_topbar(ctx)
    app_class = "or-app"
    if ctx.layout == "sidebar_topbar":
        app_class += " or-app-split"
    if ctx.layout == "top":
        app_class += " or-app-top"
    return (
        f'<div class="{app_class} or-shot-shell" x-data="{{ sidebarOpen: true }}">'
        f"{sidebar}"
        f'<div class="or-main">{topbar}<main class="or-content">{content}</main></div>'
        f"</div>"
    )


def build() -> str:
    form_overview = (
        Form.make()
        .schema(
            [
                Callout.make().info().label("Tip").description("Fill these fields"),
                Section.make("basics")
                .heading("Basics")
                .schema(
                    [
                        Flex.make()
                        .from_breakpoint("md")
                        .schema(
                            [
                                TextInput.make("name")
                                .required()
                                .label("Name")
                                .default("Ada")
                                .prefix("Dr."),
                                Select.make("role")
                                .options({"a": "Admin", "e": "Editor"})
                                .label("Role")
                                .default("a"),
                            ]
                        ),
                        Textarea.make("bio").label("Bio").rows(3),
                        Toggle.make("active").label("Active").default(True),
                        Checkbox.make("terms").label("Accept terms"),
                    ]
                ),
                FileUpload.make("avatar").image().label("Avatar"),
                RichEditor.make("body").label("Body"),
                Repeater.make("links")
                .schema([TextInput.make("url").label("URL")])
                .default_items(1)
                .label("Links"),
                Builder.make("blocks")
                .blocks(
                    [
                        Block.make("hero")
                        .label("Hero")
                        .schema([TextInput.make("heading").label("Heading")])
                    ]
                )
                .label("Blocks"),
            ]
        )
    )
    form_state = {
        "name": "Ada",
        "role": "a",
        "bio": "Editor at Orbit.",
        "active": True,
        "body": "<p>Hello from Orbit.</p>",
        "links": [{"url": "https://orbit.almasix.com"}],
        "blocks": [{"type": "hero", "heading": "Welcome"}],
    }
    form_overview.fill(form_state)

    text_input = (
        TextInput.make("email")
        .email()
        .label("Email")
        .placeholder("you@acme.test")
        .helper_text("We never share this.")
        .required()
        .render("ada@orbit.test")
    )
    select = (
        Select.make("status")
        .label("Status")
        .options({"draft": "Draft", "published": "Published", "archived": "Archived"})
        .searchable()
        .render("published")
    )
    form_textarea = (
        Textarea.make("bio")
        .label("Bio")
        .rows(4)
        .helper_text("Brief summary for your profile.")
        .placeholder("Tell us about yourself…")
        .render("Editor at Orbit. Building tables without the SPA tax.")
    )
    form_checkbox_toggle = (
        Form.make()
        .schema(
            [
                Flex.make().from_breakpoint("md").schema(
                    [
                        Toggle.make("active").label("Active account"),
                        Checkbox.make("newsletter").label("Email newsletter"),
                    ]
                ),
            ]
        )
        .fill({"active": True, "newsletter": False})
        .render()
    )
    form_date_pickers = (
        Form.make()
        .schema(
            [
                Flex.make().from_breakpoint("md").schema(
                    [
                        DatePicker.make("starts")
                        .label("Starts on")
                        .min_date("2026-01-01")
                        .max_date("2026-12-31"),
                        DateTimePicker.make("published_at").label("Published at"),
                        TimePicker.make("remind_at").label("Remind at"),
                    ]
                ),
            ]
        )
        .fill(
            {
                "starts": "2026-09-18",
                "published_at": "2026-09-18T09:00",
                "remind_at": "09:00",
            }
        )
        .render()
    )
    form_file_upload = Form.make().schema(
        [
            Flex.make().from_breakpoint("md").schema(
                [
                    FileUpload.make("cover").image().label("Cover image"),
                    FileUpload.make("avatar").avatar().label("Avatar"),
                ]
            ),
        ]
    ).render()
    form_radio_checkbox_list = (
        Form.make()
        .schema(
            [
                Radio.make("plan")
                .label("Plan")
                .options(
                    {
                        "starter": "Starter",
                        "pro": "Pro",
                        "enterprise": "Enterprise",
                    }
                )
                .descriptions(
                    {
                        "starter": "For side projects",
                        "pro": "For growing teams",
                        "enterprise": "Custom SLA",
                    }
                )
                .options_columns(2),
                CheckboxList.make("features")
                .label("Features")
                .options(
                    {
                        "api": "API access",
                        "sso": "SSO",
                        "audit": "Audit logs",
                        "support": "Priority support",
                    }
                )
                .descriptions({"sso": "SAML + OIDC", "audit": "90-day retention"})
                .bulk_toggleable()
                .options_columns(2),
            ]
        )
        .fill({"plan": "pro", "features": ["api", "sso"]})
        .render()
    )
    form_tags_input = (
        TagsInput.make("tags")
        .label("Tags")
        .suggestions(["orbit", "tables", "forms", "panels"])
        .reorderable()
        .render(["orbit", "forms"])
    )
    form_color_money = (
        Form.make()
        .schema(
            [
                Flex.make().from_breakpoint("md").schema(
                    [
                        ColorPicker.make("brand").label("Brand color"),
                        MoneyInput.make("price").label("Price").currency("EUR"),
                    ]
                ),
            ]
        )
        .fill({"brand": "#286291", "price": 49.99})
        .render()
    )
    form_rich_editor = (
        RichEditor.make("body")
        .label("Body")
        .toolbar_buttons(["bold", "italic", "link", "heading"])
        .render("<p>Hello from <strong>Orbit</strong>.</p>")
    )
    form_key_value = KeyValue.make("meta").label("Metadata").render(
        {"version": "1.0", "env": "production"}
    )
    form_repeater = (
        Repeater.make("items")
        .label("Line items")
        .schema(
            [
                TextInput.make("name").label("Name"),
                TextInput.make("qty").label("Qty"),
            ]
        )
        .table(["Name", "Qty"])
        .reorderable()
        .collapsible()
        .cloneable()
        .default_items(2)
        .render([{"name": "Widget", "qty": "2"}, {"name": "Gadget", "qty": "1"}])
    )
    form_builder = (
        Builder.make("content")
        .label("Page blocks")
        .blocks(
            [
                Block.make("hero")
                .label("Hero")
                .icon("heroicon-o-star")
                .schema([TextInput.make("heading").label("Heading")]),
                Block.make("text")
                .label("Text")
                .icon("heroicon-o-document-text")
                .schema([Textarea.make("body").label("Body").rows(2)]),
            ]
        )
        .block_picker_columns(2)
        .render(
            [
                {"type": "hero", "heading": "Welcome to Orbit"},
                {"type": "text", "body": "Ship admin UIs without the SPA tax."},
            ]
        )
    )
    form_toggle_buttons = (
        ToggleButtons.make("visibility")
        .label("Visibility")
        .options({"public": "Public", "private": "Private", "draft": "Draft"})
        .render("public")
    )
    form_morph_to_select = (
        MorphToSelect.make("assignee")
        .label("Assignee")
        .searchable()
        .types(
            [
                {
                    "type": "user",
                    "label": "User",
                    "options": {"1": "Ada", "2": "Grace"},
                },
                {
                    "type": "team",
                    "label": "Team",
                    "options": {"10": "Engineering", "11": "Design"},
                },
            ]
        )
        .render({"type": "user", "id": "1"})
    )

    schema_section = (
        Form.make()
        .schema(
            [
                Section.make("profile")
                .heading("Profile")
                .icon("heroicon-o-user")
                .compact()
                .schema([TextInput.make("name").label("Name")]),
                Section.make("advanced")
                .heading("Advanced")
                .collapsible()
                .collapsed()
                .schema([Toggle.make("debug").label("Debug mode")]),
                Section.make("notes")
                .heading("Notes")
                .aside()
                .description("Optional context for reviewers")
                .schema([Textarea.make("notes").label("Notes").rows(2)]),
            ]
        )
        .fill({"name": "Ada", "debug": False, "notes": "Looks good."})
        .render()
    )
    schema_tabs = (
        Form.make()
        .schema(
            [
                Tabs.make("main")
                .tabs(
                    {
                        "label": "General",
                        "icon": "heroicon-o-cog-6-tooth",
                        "schema": [TextInput.make("title").label("Title")],
                    },
                    {
                        "label": "SEO",
                        "icon": "heroicon-o-magnifying-glass",
                        "badge": "3",
                        "schema": [TextInput.make("slug").label("Slug")],
                    },
                    {
                        "label": "Media",
                        "schema": [FileUpload.make("cover").image().label("Cover")],
                    },
                )
                .active_tab(0)
            ]
        )
        .fill({"title": "Launch Orbit", "slug": "launch-orbit"})
        .render()
    )
    schema_wizard = (
        Form.make()
        .schema(
            [
                Wizard.make("onboard")
                .steps(
                    {
                        "label": "Account",
                        "description": "Your login details",
                        "schema": [TextInput.make("email").email().label("Email")],
                    },
                    {
                        "label": "Profile",
                        "description": "How you appear in the app",
                        "schema": [TextInput.make("name").label("Display name")],
                    },
                    {
                        "label": "Review",
                        "description": "Confirm before submitting",
                        "schema": [
                            ViewField.make("summary")
                            .label("Summary")
                            .content("<p>You are ready to launch.</p>")
                        ],
                    },
                )
                .skippable()
                .start_step(0)
            ]
        )
        .fill({"email": "ada@orbit.test", "name": "Ada"})
        .render()
    )
    schema_grid_flex = (
        Form.make()
        .schema(
            [
                SchemaGrid.make()
                .columns(2)
                .schema(
                    [
                        TextInput.make("col_a").label("Column A"),
                        TextInput.make("col_b").label("Column B"),
                    ]
                ),
                Flex.make().from_breakpoint("md").schema(
                    [
                        TextInput.make("left").label("Left"),
                        TextInput.make("right").label("Right"),
                    ]
                ),
            ]
        )
        .fill({"col_a": "Alpha", "col_b": "Beta", "left": "Sidebar", "right": "Main"})
        .render()
    )
    schema_group_split = (
        Form.make()
        .schema(
            [
                SchemaGroup.make()
                .columns(2)
                .schema(
                    [
                        TextInput.make("sku").label("SKU"),
                        TextInput.make("qty").label("Quantity"),
                    ]
                ),
                SchemaSplit.make().from_breakpoint("md").schema(
                    [
                        Textarea.make("notes").label("Notes").rows(2),
                        FileUpload.make("attachment").label("Attachment"),
                    ]
                ),
            ]
        )
        .fill({"sku": "ORB-1", "qty": "12", "notes": "Handle with care."})
        .render()
    )
    schema_fieldset = (
        Form.make()
        .schema(
            [
                Fieldset.make("billing")
                .label("Billing address")
                .schema(
                    [
                        TextInput.make("line1").label("Line 1"),
                        Flex.make().from_breakpoint("md").schema(
                            [
                                TextInput.make("city").label("City"),
                                TextInput.make("postcode").label("Postcode"),
                            ]
                        ),
                    ]
                ),
            ]
        )
        .fill({"line1": "42 Orbit Way", "city": "Nairobi", "postcode": "00100"})
        .render()
    )
    schema_primes_all = Flex.make().from_breakpoint("md").schema(
        [
            Text.make().content("Published").badge().color("success"),
            Icon.make().icon("heroicon-o-check").color("success").size("lg"),
            Image.make()
            .src("https://api.dicebear.com/9.x/shapes/svg?seed=orbit")
            .image_size(48),
            UnorderedList.make().items(["Tables", "Forms", "Panels"]).bullet_size("sm"),
        ]
    ).render()

    table = (
        Table.make()
        .columns(
            [
                TextColumn.make("title").label("Title").searchable().sortable(),
                TextColumn.make("status").label("Status").badge().sortable(),
                TextColumn.make("amount").label("Amount").money("USD").align_end().sortable(),
            ]
        )
        .records(
            [
                {"id": 1, "title": "Launch Orbit", "status": "published", "amount": 1200},
                {"id": 2, "title": "Conduit hosts", "status": "draft", "amount": 340},
                {"id": 3, "title": "Mobile tables", "status": "review", "amount": 880},
            ]
        )
        .striped()
        .actions([EditAction.make().url(lambda record, **_: f"/edit/{record['id']}")])
        .header_actions([CreateAction.make().url("/create")])
        .paginate(page=1, per_page=10)
    )

    table_money = (
        Table.make()
        .columns(
            [
                TextColumn.make("sku").label("SKU"),
                TextColumn.make("price").label("Price").money("USD").align_end(),
                TextColumn.make("cents")
                .label("From cents")
                .money("EUR", divide_by=100)
                .align_end(),
            ]
        )
        .records(
            [
                {"sku": "ORB-1", "price": 49, "cents": 4999},
                {"sku": "ORB-2", "price": 12.5, "cents": 1299},
            ]
        )
        .striped()
    )

    table_text = (
        Table.make()
        .columns(
            [
                TextColumn.make("name")
                .weight("bold")
                .icon("heroicon-o-check")
                .description(lambda record=None, **_: (record or {}).get("role", "")),
                TextColumn.make("slug").copyable(),
                TextColumn.make("blurb").markdown().wrap().limit(48),
            ]
        )
        .records(
            [
                {
                    "name": "Orbit",
                    "role": "admin kit",
                    "slug": "orbit-admin",
                    "blurb": "Ship **tables** without the SPA tax.",
                },
                {
                    "name": "Conduit",
                    "role": "live morph",
                    "slug": "conduit",
                    "blurb": "Server truth, *snappy* browser.",
                },
            ]
        )
    )

    table_icons = (
        Table.make()
        .columns(
            [
                TextColumn.make("name"),
                IconColumn.make("icon").label("Icon"),
                BooleanColumn.make("active").label("On"),
            ]
        )
        .records(
            [
                {"name": "Ada", "icon": "heroicon-o-check", "active": True},
                {"name": "Grace", "icon": "heroicon-o-plus", "active": False},
            ]
        )
    )

    table_media = (
        Table.make()
        .columns(
            [
                TextColumn.make("name"),
                ImageColumn.make("avatar").circular().size(36),
                ImageColumn.make("team").stacked().limit(2).circular().size(28),
                ColorColumn.make("color").copyable(),
            ]
        )
        .records(
            [
                {
                    "name": "Ada",
                    "avatar": "https://api.dicebear.com/9.x/shapes/svg?seed=ada",
                    "team": [
                        "https://api.dicebear.com/9.x/shapes/svg?seed=a",
                        "https://api.dicebear.com/9.x/shapes/svg?seed=b",
                        "https://api.dicebear.com/9.x/shapes/svg?seed=c",
                    ],
                    "color": "#f1511b",
                },
                {
                    "name": "Grace",
                    "avatar": "https://api.dicebear.com/9.x/shapes/svg?seed=grace",
                    "team": [
                        "https://api.dicebear.com/9.x/shapes/svg?seed=d",
                        "https://api.dicebear.com/9.x/shapes/svg?seed=e",
                    ],
                    "color": "#286291",
                },
            ]
        )
    )

    table_editable = (
        Table.make()
        .columns(
            [
                TextInputColumn.make("title").label("Title"),
                SelectColumn.make("status").options(
                    {"draft": "Draft", "review": "Review", "published": "Published"}
                ),
                ToggleColumn.make("featured").label("Featured"),
                CheckboxColumn.make("done").label("Done"),
            ]
        )
        .records(
            [
                {
                    "id": 1,
                    "title": "Filters polish",
                    "status": "review",
                    "featured": True,
                    "done": False,
                },
                {
                    "id": 2,
                    "title": "Summaries",
                    "status": "published",
                    "featured": False,
                    "done": True,
                },
            ]
        )
    )

    table_tags = (
        Table.make()
        .columns(
            [
                TextColumn.make("title"),
                TagsColumn.make("tags"),
                ViewColumn.make("note").content(
                    lambda state=None, **_: f"<em>{state}</em>"
                ),
            ]
        )
        .records(
            [
                {"title": "Shell", "tags": ["nav", "chrome"], "note": "Sticky topbar"},
                {"title": "Tables", "tags": "list,ux", "note": "Filament vibes"},
            ]
        )
    )

    table_group_cols = (
        Table.make()
        .columns(
            [
                TextColumn.make("title"),
                ColumnGroup.make(
                    "Meta",
                    [
                        TextColumn.make("a").label("A"),
                        TextColumn.make("b").label("B"),
                    ],
                ),
            ]
        )
        .records([{"title": "Row", "a": "1", "b": "2"}, {"title": "Row 2", "a": "3", "b": "4"}])
    )

    table_layout = (
        Table.make()
        .columns(
            [
                Split.make(
                    [
                        Stack.make(
                            [
                                TextColumn.make("title").weight("semibold"),
                                TextColumn.make("subtitle").color("gray"),
                            ]
                        ),
                        TagsColumn.make("tags"),
                    ]
                ).label("Content"),
                LayoutPanel.make([TextColumn.make("note")]).label("Panel"),
                Grid.make([TextColumn.make("x"), TextColumn.make("y")]).columns(2).label("Grid"),
                View.make([TextColumn.make("subtitle")])
                .content('<div class="or-layout-view-demo">{children}</div>')
                .label("View"),
            ]
        )
        .records(
            [
                {
                    "title": "Orbit shell",
                    "subtitle": "Sidebar + topbar",
                    "tags": ["shell"],
                    "note": "Collapsible",
                    "x": "A",
                    "y": "B",
                }
            ]
        )
    )

    table_filters = (
        Table.make()
        .columns(
            [
                TextColumn.make("title").searchable(),
                TextColumn.make("status").badge(),
            ]
        )
        .filters(
            [
                SelectFilter.make("status")
                .label("Status")
                .options({"draft": "Draft", "published": "Published"})
            ]
        )
        .filter_state({"status": "published"})
        .records(
            [
                {"title": "Published one", "status": "published"},
                {"title": "Drafty", "status": "draft"},
            ]
        )
        .header_actions([CreateAction.make().url("/create")])
    )

    table_summaries = (
        Table.make()
        .columns(
            [
                TextColumn.make("title"),
                TextColumn.make("amount")
                .money("USD")
                .align_end()
                .summarize(Sum.make(), Average.make(), Count.make()),
            ]
        )
        .summaries(page=True)
        .records(
            [
                {"title": "A", "amount": 100},
                {"title": "B", "amount": 250},
                {"title": "C", "amount": 50},
            ]
        )
    )

    table_grouping = (
        Table.make()
        .columns(
            [
                TextColumn.make("title"),
                TextColumn.make("status").badge(),
            ]
        )
        .default_group(Group.make("status").label("Status").collapsible())
        .records(
            [
                {"id": 1, "title": "Launch", "status": "published"},
                {"id": 2, "title": "Hosts", "status": "draft"},
                {"id": 3, "title": "Branding", "status": "published"},
                {"id": 4, "title": "Widgets", "status": "draft"},
            ]
        )
    )

    table_actions = (
        Table.make()
        .columns([TextColumn.make("title"), TextColumn.make("status").badge()])
        .records(
            [
                {"id": 1, "title": "Editable row", "status": "draft"},
                {"id": 2, "title": "Another", "status": "published"},
            ]
        )
        .actions(
            [
                EditAction.make().url(lambda record=None, **_: f"/edit/{(record or {}).get('id')}"),
            ]
        )
        .actions_as_dropdown(False)
        .header_actions([CreateAction.make().url("/create")])
        .striped()
    )

    table_empty = (
        Table.make()
        .columns([TextColumn.make("title")])
        .records([])
        .empty_state_heading("No posts yet")
        .empty_state_description("Create your first post — the empty state is rooting for you.")
        .header_actions([CreateAction.make().url("/create")])
        .empty_state_actions([CreateAction.make().url("/create")])
    )

    panel = (
        Panel.make("admin")
        .brand_name("Orbit")
        .resources([DemoResource])
        .navigation_layout("sidebar_topbar")
        .sidebar_collapsible()
    )
    shell = shell_fragment(
        panel,
        table.render()
        + EmptyState.make().heading("No drafts").description("Create one when you are ready.").render(),
        active_path="/post",
    )

    form_variants = build_form_variants()
    schema_variants = build_schema_variants()

    parts = [
        shot("forms/overview", "Forms overview", form_overview.render()),
        shot("forms/text-input", "Text input", text_input),
        shot("forms/select", "Select", select),
        shot("forms/textarea", "Textarea", form_textarea),
        shot("forms/checkbox-toggle", "Checkbox + toggle", form_checkbox_toggle),
        shot("forms/date-pickers", "Date pickers", form_date_pickers),
        shot("forms/file-upload", "File upload", form_file_upload),
        shot("forms/radio-checkbox-list", "Radio + checkbox list", form_radio_checkbox_list),
        shot("forms/tags-input", "Tags input", form_tags_input),
        shot("forms/color-money", "Color + money", form_color_money),
        shot("forms/rich-editor", "Rich editor", form_rich_editor),
        shot("forms/key-value", "Key-value", form_key_value),
        shot("forms/repeater", "Repeater", form_repeater),
        shot("forms/builder", "Builder", form_builder),
        shot("forms/toggle-buttons", "Toggle buttons", form_toggle_buttons),
        shot("forms/morph-to-select", "Morph-to select", form_morph_to_select),
        *(
            shot(sid, label, html)
            for sid, (label, html) in form_variants.items()
        ),
        *(
            shot(sid, label, html)
            for sid, (label, html) in schema_variants.items()
        ),
        shot("tables/overview", "Tables overview", table.render()),
        shot("tables/money", "Money / currency", table_money.render()),
        shot("tables/text-features", "Text column features", table_text.render()),
        shot("tables/icon-boolean", "Icon + boolean", table_icons.render()),
        shot("tables/image-color", "Image + color", table_media.render()),
        shot("tables/editable", "Editable columns", table_editable.render()),
        shot("tables/tags-view", "Tags + view", table_tags.render()),
        shot("tables/column-group", "Column group", table_group_cols.render()),
        shot("tables/layout", "Cell layouts", table_layout.render()),
        shot("tables/filters", "Filters chrome", table_filters.render()),
        shot("tables/summaries", "Summaries", table_summaries.render()),
        shot("tables/grouping", "Grouped rows", table_grouping.render()),
        shot("tables/actions", "Row actions", table_actions.render()),
        shot("tables/empty", "Empty state", table_empty.render()),
        shot(
            "schemas/callout",
            "Callout",
            Callout.make().info().label("Tip").description("Fill these fields").render(),
        ),
        shot(
            "schemas/empty-state",
            "Empty state",
            EmptyState.make().heading("No drafts").description("Create one when you are ready.").render(),
        ),
        shot(
            "schemas/primes-text",
            "Text prime",
            Text.make().content("Published").badge().color("success").render(),
        ),
        shot("schemas/section", "Section", schema_section),
        shot("schemas/tabs", "Tabs", schema_tabs),
        shot("schemas/wizard", "Wizard", schema_wizard),
        shot("schemas/grid-flex", "Grid + flex", schema_grid_flex),
        shot("schemas/group-split", "Group + split", schema_group_split),
        shot("schemas/fieldset", "Fieldset", schema_fieldset),
        shot("schemas/primes-all", "All primes", schema_primes_all),
        shot("panels/shell", "Panel shell", shell),
        shot("users/login", "Login", Login.render()),
    ]

    shot_list = "\n".join(f"  - {sid}" for sid, _ in SHOTS)
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8" />
<title>Orbit examples gallery</title>
<style>
{CSS}
/* Gallery chrome — not part of product CSS */
[x-cloak] {{ display: none !important; }}
.or-action-modal-host,
.or-modal-backdrop,
.or-modal {{ display: none !important; }} /* never capture confirm overlays */
html, body {{
  margin: 0;
  font-family: var(--or-font);
  background: #ffffff;
  color: var(--or-ink);
}}
body.dark {{
  background: #0f0e0d;
  color: #f3efe9;
}}
.gallery-header {{
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem 1.5rem 0.5rem;
}}
.gallery-header h1 {{ margin: 0 0 0.35rem; font-size: 1.5rem; }}
.gallery-header p {{ margin: 0; color: var(--or-muted); font-size: 0.95rem; }}
.gallery-header code {{ font-size: 0.85em; }}
.gallery-section {{
  max-width: 960px;
  margin: 0 auto;
  padding: 1.25rem 1.5rem 2rem;
}}
.gallery-label {{
  margin: 0 0 0.65rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--or-muted);
  letter-spacing: 0.02em;
}}
.gallery-label code {{
  font-weight: 500;
  opacity: 0.85;
}}
.or-shot {{
  background: #ffffff;
  border: 1px solid var(--or-line, #e5e2dc);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 10px 30px rgba(28, 20, 17, 0.06);
  overflow: hidden;
}}
body.dark .or-shot {{
  background: #1a1715;
  border-color: #2e2926;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}}
.or-shot-shell {{
  min-height: 420px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--or-line);
}}
.or-shot .or-app {{ min-height: 420px; }}
</style>
</head>
<body>
<header class="gallery-header">
  <h1>Orbit screenshot gallery</h1>
  <p>Shots use ids <code>section/name</code> → <code>examples/{{light|dark}}/section/name.png</code></p>
  <p><code>{shot_list}</code></p>
</header>
{"".join(parts)}
</body>
</html>
"""


def list_shot_ids() -> list[str]:
    return [sid for sid, _ in SHOTS]


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    html = build()
    # Sanity: never ship a gallery that still embeds confirm modal chrome visibly
    if "or-action-modal-host" in html and "display: none !important" not in html:
        raise SystemExit("Gallery must hide action modal host")
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT}")
    print("Shots:")
    for sid in list_shot_ids():
        print(f"  {sid}")
