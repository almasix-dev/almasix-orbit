#!/usr/bin/env python3
"""Build a static HTML gallery from Orbit render() output for screenshot capture.

Shot IDs use ``{section}/{name}`` and become files under
``docs/public/examples/{light|dark}/{section}/{name}.png``.
"""

from __future__ import annotations

import re
from pathlib import Path

from almasix.orbit.actions.action import CreateAction, DeleteBulkAction, EditAction
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
    Textarea,
    TextInput,
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
    Section,
    Tabs,
    Wizard,
)
from almasix.orbit.schemas.layouts import (
    Grid as SchemaGrid,
)
from almasix.orbit.schemas.layouts import (
    Group as SchemaGroup,
)
from almasix.orbit.schemas.layouts import (
    Split as SchemaSplit,
)
from almasix.orbit.schemas.primes import Icon, Image, Text, UnorderedList
from almasix.orbit.schemas.schema import Schema
from almasix.orbit.support.html import e
from almasix.orbit.tables.columns import (
    BadgeColumn,
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
from almasix.orbit.tables.filters import (
    Filter,
    FilterGroup,
    SelectFilter,
    TernaryFilter,
    TrashedFilter,
)
from almasix.orbit.tables.grouping import Group
from almasix.orbit.tables.layout import Grid, Split, Stack, View
from almasix.orbit.tables.layout import Panel as LayoutPanel
from almasix.orbit.tables.summaries import Average, Count, Sum
from almasix.orbit.tables.table import Table
from gallery_variants import (
    build_action_variants,
    build_form_variants,
    build_infolist_variants,
    build_navigation_variants,
    build_notification_variants,
    build_resource_variants,
    build_schema_variants,
    build_tenancy_variants,
    build_widget_variants,
)

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
    ("tables/overview-columns", "Overview — columns"),
    ("tables/overview-searchable", "Overview — searchable"),
    ("tables/overview-sortable", "Overview — sortable"),
    ("tables/overview-relationships", "Overview — relationship columns"),
    ("tables/overview-pagination", "Overview — pagination"),
    ("tables/overview-pagination-disabled", "Overview — pagination disabled"),
    ("tables/overview-heading", "Overview — heading"),
    ("tables/overview-reorder", "Overview — reorder"),
    ("tables/overview-striped", "Overview — striped rows"),
    ("tables/columns-overview", "Columns overview — shared APIs"),
    ("tables/columns-overview-manager", "Columns overview — column manager"),
    ("tables/money", "Money / currency"),
    ("tables/text-features", "Text column features"),
    ("tables/text-formatting", "Text — color, size, weight, font"),
    ("tables/text-icons", "Text — icons"),
    ("tables/icon-boolean", "Icon + boolean"),
    ("tables/icon-colors", "Icon — colors + sizes"),
    ("tables/image-color", "Image + color"),
    ("tables/image-stacked", "Image — stacked"),
    ("tables/editable", "Editable columns"),
    ("tables/select-column", "Select column"),
    ("tables/toggle-column", "Toggle column"),
    ("tables/text-input-column", "Text input column"),
    ("tables/checkbox-column", "Checkbox column"),
    ("tables/badge-column", "Badge column"),
    ("tables/boolean-column", "Boolean column"),
    ("tables/tags-column", "Tags column"),
    ("tables/tags-view", "Tags + view"),
    ("tables/view-column", "View column"),
    ("tables/column-group", "Column group"),
    ("tables/layout", "Cell layouts"),
    ("tables/filters", "Filters chrome"),
    ("tables/filters-deferred", "Filters deferred"),
    ("tables/filters-ternary", "Filters ternary + trashed"),
    ("tables/summaries", "Summaries"),
    ("tables/grouping", "Grouped rows"),
    ("tables/actions", "Row actions"),
    ("tables/empty", "Empty state"),
    ("schemas/overview", "Schemas overview"),
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
    # Infolists
    ("infolists/overview", "Infolists overview"),
    ("infolists/overview/labels", "Infolists — labels"),
    ("infolists/overview/helper-hint", "Infolists — helper + hint"),
    ("infolists/overview/hidden-label", "Infolists — hidden label"),
    ("infolists/overview/inline-label", "Infolists — inline label"),
    ("infolists/overview/placeholder", "Infolists — placeholder"),
    ("infolists/overview/default", "Infolists — default"),
    ("infolists/overview/copyable", "Infolists — copyable"),
    ("infolists/overview/format-state", "Infolists — format state"),
    ("infolists/overview/tooltip", "Infolists — tooltip"),
    ("infolists/overview/slots", "Infolists — content slots"),
    ("infolists/overview/affix", "Infolists — affix actions"),
    ("infolists/overview/extra-attributes", "Infolists — extra attributes"),
    ("infolists/overview/columns", "Infolists — columns"),
    ("infolists/overview/sections", "Infolists — sections"),
    ("infolists/text-entry/basic", "Text entry — basic"),
    ("infolists/text-entry/badge", "Text entry — badge"),
    ("infolists/text-entry/color", "Text entry — color"),
    ("infolists/text-entry/icon", "Text entry — icon"),
    ("infolists/text-entry/url", "Text entry — url"),
    ("infolists/text-entry/size-weight", "Text entry — size + weight"),
    ("infolists/text-entry/font-family", "Text entry — font family"),
    ("infolists/text-entry/line-clamp", "Text entry — line clamp"),
    ("infolists/text-entry/list", "Text entry — list with line breaks"),
    ("infolists/text-entry/bulleted", "Text entry — bulleted"),
    ("infolists/text-entry/separator", "Text entry — separator badges"),
    ("infolists/text-entry/date", "Text entry — date / time"),
    ("infolists/text-entry/since", "Text entry — since"),
    ("infolists/text-entry/money", "Text entry — money"),
    ("infolists/text-entry/numeric", "Text entry — numeric"),
    ("infolists/text-entry/markdown", "Text entry — markdown"),
    ("infolists/text-entry/html", "Text entry — html"),
    ("infolists/text-entry/prose", "Text entry — prose"),
    ("infolists/text-entry/limit", "Text entry — limit / words"),
    ("infolists/icon-entry/basic", "Icon entry — basic"),
    ("infolists/icon-entry/boolean", "Icon entry — boolean"),
    ("infolists/icon-entry/colors", "Icon entry — colors"),
    ("infolists/image-entry/basic", "Image entry — basic"),
    ("infolists/image-entry/circular", "Image entry — circular"),
    ("infolists/image-entry/stacked", "Image entry — stacked"),
    ("infolists/color-entry/basic", "Color entry — basic"),
    ("infolists/color-entry/copyable", "Color entry — copyable"),
    ("infolists/code-entry/basic", "Code entry — basic"),
    ("infolists/code-entry/grammar", "Code entry — grammar + copy"),
    ("infolists/key-value-entry/basic", "Key-value entry — basic"),
    ("infolists/key-value-entry/labels", "Key-value entry — labels"),
    ("infolists/repeatable-entry/basic", "Repeatable entry — basic"),
    ("infolists/repeatable-entry/columns", "Repeatable entry — columns"),
    ("infolists/view-entry/basic", "View entry — basic"),
    ("infolists/view-entry/callable", "View entry — callable"),
    # Actions
    ("actions/overview", "Actions overview"),
    ("actions/overview/triggers", "Actions — trigger styles"),
    ("actions/overview/sizes", "Actions — sizes"),
    ("actions/overview/outlined", "Actions — outlined"),
    ("actions/overview/icons", "Actions — icons"),
    ("actions/overview/tooltip", "Actions — tooltip"),
    ("actions/overview/badge", "Actions — badge indicator"),
    ("actions/overview/url", "Actions — URL + new tab"),
    ("actions/overview/authorize", "Actions — authorize"),
    ("actions/overview/schema", "Actions — schema / form"),
    ("actions/overview/notifications", "Actions — notifications"),
    ("actions/modals/confirm", "Modals — confirmation"),
    ("actions/modals/form", "Modals — form"),
    ("actions/modals/slide-over", "Modals — slide over"),
    ("actions/modals/labels", "Modals — custom labels"),
    ("actions/modals/icon", "Modals — icon + alignment"),
    ("actions/grouping/dropdown", "Grouping — dropdown"),
    ("actions/grouping/button-group", "Grouping — button group"),
    ("actions/grouping/sections", "Grouping — sections"),
    ("actions/create", "Create action"),
    ("actions/edit", "Edit action"),
    ("actions/view", "View action"),
    ("actions/delete", "Delete action"),
    ("actions/replicate", "Replicate action"),
    ("actions/force-delete", "Force-delete action"),
    ("actions/restore", "Restore action"),
    ("actions/import", "Import action"),
    ("actions/export", "Export action"),
    # Widgets + dashboard
    ("widgets/overview", "Widgets overview"),
    ("widgets/overview/heading", "Widgets — heading"),
    ("widgets/overview/sort", "Widgets — sort"),
    ("widgets/overview/column-span", "Widgets — column span"),
    ("widgets/overview/visibility", "Widgets — visibility"),
    ("widgets/overview/custom", "Widgets — custom"),
    ("widgets/stats-overview", "Stats overview"),
    ("widgets/stats-overview/value", "Stats — value"),
    ("widgets/stats-overview/description", "Stats — description"),
    ("widgets/stats-overview/colors", "Stats — colors"),
    ("widgets/stats-overview/chart", "Stats — sparklines"),
    ("widgets/stats-overview/url", "Stats — URL"),
    ("widgets/charts", "Charts — Chart.js"),
    ("widgets/charts/libraries", "Charts — libraries"),
    ("widgets/charts/types", "Charts — types"),
    ("widgets/charts/datasets", "Charts — datasets"),
    ("widgets/charts/chrome", "Charts — chrome"),
    ("widgets/charts/filters", "Charts — filters"),
    ("widgets/charts/empty", "Charts — empty"),
    ("widgets/tables", "Table widget"),
    ("widgets/tables/basic", "Table widget — basic"),
    ("widgets/tables/full-span", "Table widget — full span"),
    ("widgets/tables/empty", "Table widget — empty"),
    ("panels/dashboard", "Dashboard"),
    ("panels/dashboard/widgets", "Dashboard — widgets"),
    ("panels/dashboard/columns", "Dashboard — columns"),
    ("panels/dashboard/filters", "Dashboard — filters"),
    ("panels/dashboard/route-path", "Dashboard — route path"),
    # Navigation
    ("navigation/overview", "Navigation overview"),
    ("navigation/overview/layouts-apps", "Navigation — apps layout"),
    ("navigation/overview/layouts-sidebar", "Navigation — sidebar layout"),
    ("navigation/overview/layouts-top", "Navigation — top layout"),
    ("navigation/overview/groups", "Navigation — groups"),
    ("navigation/overview/subgroups", "Navigation — subgroups"),
    ("navigation/overview/badges", "Navigation — badges"),
    ("navigation/overview/parent-items", "Navigation — parent items"),
    ("navigation/overview/custom-items", "Navigation — custom items"),
    ("navigation/overview/sidebar-collapse", "Navigation — sidebar collapse"),
    ("navigation/custom-pages", "Custom pages"),
    ("navigation/user-menu", "User menu"),
    ("navigation/user-menu/groups", "User menu — groups"),
    ("navigation/user-menu/position", "User menu — sidebar position"),
    ("navigation/clusters", "Clusters"),
    ("navigation/clusters/sub-nav", "Clusters — sub-navigation"),
    ("panels/shell", "Panel shell"),
    ("users/login", "Login"),
    ("users/tenancy/switcher", "Tenancy — switcher"),
    ("users/tenancy/menu", "Tenancy — switcher menu"),
    ("users/tenancy/scoped-list", "Tenancy — scoped list"),
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


def static_selection_chrome(html: str, *, count_label: str = "1 record selected") -> str:
    """Gallery has no Alpine — reveal the selection bar for static screenshots."""
    html = html.replace(
        'role="status" aria-live="polite" x-show="selectionCount > 0" x-cloak>',
        'role="status" aria-live="polite">',
        1,
    )
    return re.sub(
        r'<span class="or-ta-selection-label"[^>]*></span>',
        f'<span class="or-ta-selection-label">{count_label}</span>',
        html,
        count=1,
    )


def static_filters_open(html: str) -> str:
    """Gallery has no Alpine — reveal the filters panel for screenshots."""
    return html.replace(
        'class="or-filters-panel" x-show="filtersOpen" x-cloak',
        'class="or-filters-panel"',
        1,
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
    schema_overview = (
        Schema.make("profile")
        .operation("edit")
        .schema(
            [
                Callout.make("tip")
                .info()
                .label("Tip")
                .description("Schemas nest layouts, fields, and primes."),
                SchemaGrid.make()
                .columns(2)
                .schema(
                    [
                        Section.make("details")
                        .heading("Details")
                        .icon("heroicon-o-user")
                        .schema(
                            [
                                TextInput.make("name").label("Name").required(),
                                TextInput.make("email").email().label("Email"),
                            ]
                        ),
                        Section.make("notes")
                        .heading("Notes")
                        .secondary()
                        .schema([Textarea.make("bio").label("Bio").rows(3)]),
                    ]
                ),
            ]
        )
        .fill(
            {
                "name": "Ada Lovelace",
                "email": "ada@orbit.test",
                "bio": "Mathematician and first programmer.",
            }
        )
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

    _overview_posts = [
        {"id": 1, "title": "Launch Orbit", "status": "published", "amount": 1200, "author": {"name": "Ada Lovelace"}, "featured": True, "sort": 1},
        {"id": 2, "title": "Conduit hosts", "status": "draft", "amount": 340, "author": {"name": "Grace Hopper"}, "featured": False, "sort": 2},
        {"id": 3, "title": "Mobile tables", "status": "review", "amount": 880, "author": {"name": "Katherine Johnson"}, "featured": True, "sort": 3},
        {"id": 4, "title": "Panel chrome", "status": "published", "amount": 560, "author": {"name": "Ada Lovelace"}, "featured": False, "sort": 4},
        {"id": 5, "title": "Form fields", "status": "published", "amount": 210, "author": {"name": "Margaret Hamilton"}, "featured": True, "sort": 5},
        {"id": 6, "title": "Action modals", "status": "draft", "amount": 95, "author": {"name": "Grace Hopper"}, "featured": False, "sort": 6},
        {"id": 7, "title": "Global search", "status": "review", "amount": 430, "author": {"name": "Dorothy Vaughan"}, "featured": False, "sort": 7},
        {"id": 8, "title": "Theme tokens", "status": "published", "amount": 175, "author": {"name": "Katherine Johnson"}, "featured": True, "sort": 8},
        {"id": 9, "title": "Empty states", "status": "draft", "amount": 60, "author": {"name": "Ada Lovelace"}, "featured": False, "sort": 9},
        {"id": 10, "title": "Bulk delete", "status": "published", "amount": 720, "author": {"name": "Margaret Hamilton"}, "featured": True, "sort": 10},
        {"id": 11, "title": "Query builder", "status": "review", "amount": 310, "author": {"name": "Dorothy Vaughan"}, "featured": False, "sort": 11},
        {"id": 12, "title": "Infolist entries", "status": "published", "amount": 450, "author": {"name": "Grace Hopper"}, "featured": True, "sort": 12},
    ]

    table = (
        Table.make()
        .heading("Posts")
        .description("Searchable, sortable, and actionable records.")
        .columns(
            [
                TextColumn.make("title").label("Title").searchable().sortable(),
                TextColumn.make("author.name").label("Author").sortable(),
                TextColumn.make("status").label("Status").badge().sortable(),
                TextColumn.make("amount").label("Amount").money("USD").align_end().sortable(),
            ]
        )
        .records(_overview_posts)
        .striped()
        .actions([EditAction.make().url(lambda record, **_: f"/edit/{record['id']}")])
        .header_actions([CreateAction.make().url("/create")])
        .paginate(page=1, per_page=10)
        .extreme_pagination_links()
    )

    table_overview_columns = (
        Table.make()
        .columns(
            [
                TextColumn.make("title"),
                TextColumn.make("slug"),
                IconColumn.make("featured").boolean().label("Featured"),
            ]
        )
        .records(
            [
                {"title": "Launch Orbit", "slug": "launch-orbit", "featured": True},
                {"title": "Conduit hosts", "slug": "conduit-hosts", "featured": False},
                {"title": "Mobile tables", "slug": "mobile-tables", "featured": True},
                {"title": "Panel chrome", "slug": "panel-chrome", "featured": False},
                {"title": "Form fields", "slug": "form-fields", "featured": True},
            ]
        )
        .striped()
        .paginated(False)
    )

    table_overview_searchable = (
        Table.make()
        .columns(
            [
                TextColumn.make("title").searchable().sortable(),
                TextColumn.make("status").badge(),
            ]
        )
        .records(_overview_posts)
        .search("Orbit")
        .header_actions([CreateAction.make().url("/create")])
        .paginate(page=1, per_page=10)
    )

    table_overview_sortable = (
        Table.make()
        .columns(
            [
                TextColumn.make("title").sortable(),
                TextColumn.make("amount").money("USD").align_end().sortable(),
            ]
        )
        .records(_overview_posts[:8])
        .sort("amount", "desc")
        .striped()
        .paginate(page=1, per_page=10)
    )

    table_overview_relationships = (
        Table.make()
        .columns(
            [
                TextColumn.make("title").searchable(),
                TextColumn.make("author.name").label("Author"),
                TextColumn.make("status").badge(),
            ]
        )
        .records(_overview_posts[:6])
        .striped()
        .paginated(False)
    )

    _cols_people = [
        {
            "id": 1,
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@example.com",
            "nickname": None,
            "website": "https://almasix.com",
        },
        {
            "id": 2,
            "first_name": "Grace",
            "last_name": "Hopper",
            "email": "grace@example.com",
            "nickname": "Amazing Grace",
            "website": "https://docs.almasix.com",
        },
        {
            "id": 3,
            "first_name": "Katherine",
            "last_name": "Johnson",
            "email": "katherine@example.com",
            "nickname": "",
            "website": None,
        },
        {
            "id": 4,
            "first_name": "Margaret",
            "last_name": "Hamilton",
            "email": "margaret@example.com",
            "nickname": None,
            "website": "https://orbit.almasix.com",
        },
    ]

    table_columns_overview = (
        Table.make()
        .heading("Columns overview")
        .description("Shared Column APIs — state, placeholder, multi-key sort/search.")
        .reorderable_columns()
        .columns(
            [
                TextColumn.make("full_name")
                .label("Full name")
                .state(
                    lambda record: f"{record.get('first_name', '')} {record.get('last_name', '')}".strip()
                )
                .sortable(["last_name", "first_name"])
                .searchable(["first_name", "last_name", "email"])
                .wrap_header()
                .grow()
                .header_tooltip("Sorted by last name, then first name"),
                TextColumn.make("nickname").placeholder("No nickname").toggleable().width(140),
                TextColumn.make("email").searchable().sortable().toggleable(),
                TextColumn.make("website")
                .label("Site")
                .placeholder("—")
                .url(lambda record, state, **_: state or "#")
                .open_url_in_new_tab()
                .toggleable(),
            ]
        )
        .records(_cols_people)
        .striped()
        .paginated(False)
        .default_sort("full_name")
    )

    table_columns_overview_manager = (
        Table.make()
        .reorderable_columns()
        .columns(
            [
                TextColumn.make("full_name")
                .label("Full name")
                .state(
                    lambda record: f"{record.get('first_name', '')} {record.get('last_name', '')}".strip()
                )
                .toggleable(),
                TextColumn.make("email").toggleable(),
                TextColumn.make("website")
                .label("Site")
                .toggleable(is_toggled_hidden_by_default=True),
            ]
        )
        .records(_cols_people)
        .striped()
        .paginated(False)
    )

    table_overview_pagination = (
        Table.make()
        .columns(
            [
                TextColumn.make("title"),
                TextColumn.make("status").badge(),
            ]
        )
        .records(_overview_posts)
        .paginated([5, 10, 25, "all"])
        .default_pagination_page_option(5)
        .extreme_pagination_links()
        .paginate(page=1, per_page=5)
        .striped()
    )

    table_overview_pagination_disabled = (
        Table.make()
        .columns(
            [
                TextColumn.make("title"),
                TextColumn.make("status").badge(),
            ]
        )
        .records(_overview_posts[:6])
        .paginated(False)
        .striped()
    )

    table_overview_heading = (
        Table.make()
        .heading("Clients")
        .description("Manage your clients here.")
        .columns(
            [
                TextColumn.make("title").label("Name"),
                TextColumn.make("status").badge(),
            ]
        )
        .records(_overview_posts[:5])
        .header_actions([CreateAction.make().url("/create")])
        .striped()
        .paginated(False)
    )

    table_overview_reorder = (
        Table.make()
        .columns(
            [
                TextColumn.make("title"),
                TextColumn.make("sort").label("Order"),
            ]
        )
        .records(_overview_posts[:5])
        .reorderable("sort")
        .striped()
        .paginated(False)
    )

    table_overview_striped = (
        Table.make()
        .columns(
            [
                TextColumn.make("title"),
                TextColumn.make("status").badge(),
                TextColumn.make("amount").money("USD").align_end(),
            ]
        )
        .records(_overview_posts[:6])
        .striped()
        .record_classes(
            lambda record: "or-row-draft" if record.get("status") == "draft" else None
        )
        .paginated(False)
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

    table_text_formatting = (
        Table.make()
        .columns(
            [
                TextColumn.make("status").label("Status").color("primary"),
                TextColumn.make("priority")
                .label("Priority")
                .color(lambda state=None, **_: "danger" if state == "urgent" else "gray"),
                TextColumn.make("heading").label("Heading").size("lg"),
                TextColumn.make("name").label("Name").weight("bold"),
                TextColumn.make("reference").label("Reference").font_family("mono"),
            ]
        )
        .records(
            [
                {
                    "status": "Published",
                    "priority": "urgent",
                    "heading": "Launch week",
                    "name": "Ada Lovelace",
                    "reference": "ORB-1042",
                },
                {
                    "status": "Draft",
                    "priority": "normal",
                    "heading": "Follow-up",
                    "name": "Grace Hopper",
                    "reference": "ORB-1043",
                },
            ]
        )
    )

    table_text_icons = (
        Table.make()
        .columns(
            [
                TextColumn.make("name").label("Name").icon("heroicon-o-users"),
                TextColumn.make("role")
                .label("Role (icon after)")
                .icon("heroicon-o-cog-6-tooth")
                .icon_position("after"),
                TextColumn.make("priority")
                .label("Priority (icon color)")
                .icon("heroicon-o-bell")
                .icon_color("primary"),
            ]
        )
        .records(
            [
                {"name": "Ada Lovelace", "role": "Admin", "priority": "High"},
                {"name": "Grace Hopper", "role": "Editor", "priority": "Normal"},
            ]
        )
    )

    table_badge_column = (
        Table.make()
        .columns(
            [
                TextColumn.make("subject").label("Subject").searchable(),
                BadgeColumn.make("status")
                .sortable()
                .color(
                    lambda state=None, **_: {"open": "warning", "closed": "success"}.get(
                        state, "gray"
                    )
                ),
                BadgeColumn.make("priority").color("primary"),
            ]
        )
        .records(
            [
                {"id": 1, "subject": "Payments down", "status": "open", "priority": "urgent"},
                {"id": 2, "subject": "Typo on homepage", "status": "closed", "priority": "low"},
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

    table_icon_colors = (
        Table.make()
        .columns(
            [
                TextColumn.make("title").label("Alert"),
                # IconColumn's non-boolean mode renders the resolved state itself as the
                # icon name, so the icon lives directly in the record data here.
                IconColumn.make("severity")
                .label("Severity")
                .color(
                    lambda state=None, **_: {
                        "heroicon-o-information-circle": "info",
                        "heroicon-o-bell": "warning",
                        "heroicon-o-x-mark": "danger",
                    }.get(state, "gray")
                ),
                IconColumn.make("severity_lg").label("Large").color("danger").size("lg"),
            ]
        )
        .records(
            [
                {
                    "title": "Disk usage high",
                    "severity": "heroicon-o-x-mark",
                    "severity_lg": "heroicon-o-bell",
                },
                {
                    "title": "Deploy finished",
                    "severity": "heroicon-o-information-circle",
                    "severity_lg": "heroicon-o-check",
                },
                {
                    "title": "Latency rising",
                    "severity": "heroicon-o-bell",
                    "severity_lg": "heroicon-o-bell",
                },
            ]
        )
    )

    table_boolean_column = (
        Table.make()
        .columns(
            [
                TextColumn.make("name").searchable(),
                BooleanColumn.make("enabled").label("Enabled").sortable().align_center(),
                IconColumn.make("verified")
                .label("Verified")
                .boolean()
                .true_color("info")
                .false_color("gray")
                .align_center(),
                TextColumn.make("beta").label("Beta?").boolean(),
            ]
        )
        .records(
            [
                {"id": 1, "name": "Dark mode", "enabled": True, "verified": True, "beta": False},
                {
                    "id": 2,
                    "name": "AI summaries",
                    "enabled": False,
                    "verified": False,
                    "beta": True,
                },
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

    table_image_stacked = (
        Table.make()
        .columns(
            [
                TextColumn.make("name").weight("bold"),
                ImageColumn.make("teammate_urls")
                .label("Teammates")
                .stacked()
                .limit(3)
                .circular()
                .size(28)
                .ring(2)
                .overlap("0.6rem"),
            ]
        )
        .records(
            [
                {
                    "id": 1,
                    "name": "Ada Lovelace",
                    "teammate_urls": [
                        "https://api.dicebear.com/9.x/shapes/svg?seed=a",
                        "https://api.dicebear.com/9.x/shapes/svg?seed=b",
                        "https://api.dicebear.com/9.x/shapes/svg?seed=c",
                        "https://api.dicebear.com/9.x/shapes/svg?seed=d",
                    ],
                },
                {
                    "id": 2,
                    "name": "Grace Hopper",
                    "teammate_urls": [
                        "https://api.dicebear.com/9.x/shapes/svg?seed=e",
                        "https://api.dicebear.com/9.x/shapes/svg?seed=f",
                    ],
                },
            ]
        )
    )

    table_select_column = (
        Table.make()
        .columns(
            [
                TextColumn.make("title").searchable().sortable(),
                SelectColumn.make("status")
                .label("Status")
                .options({"draft": "Draft", "review": "Review", "published": "Published"})
                .selectable_placeholder(False),
            ]
        )
        .records(
            [
                {"id": 1, "title": "Launch Orbit", "status": "draft"},
                {"id": 2, "title": "Conduit hosts", "status": "published"},
            ]
        )
    )

    table_toggle_column = (
        Table.make()
        .columns(
            [
                TextColumn.make("name").searchable(),
                ToggleColumn.make("enabled").label("On").align_center(),
                ToggleColumn.make("public")
                .align_center()
                .disabled(lambda record=None, **_: record.get("locked")),
            ]
        )
        .records(
            [
                {"id": 1, "name": "Dark mode", "enabled": True, "public": True, "locked": False},
                {"id": 2, "name": "Beta banner", "enabled": False, "public": False, "locked": True},
            ]
        )
    )

    table_text_input_column = (
        Table.make()
        .columns(
            [
                TextColumn.make("product").searchable(),
                TextInputColumn.make("sku").label("SKU"),
                TextInputColumn.make("price")
                .label("Price")
                .type("number")
                .input_mode("decimal")
                .step("0.01")
                .prefix("$"),
            ]
        )
        .records(
            [
                {"id": 1, "product": "Widget", "sku": "ORB-1", "price": "19.99"},
                {"id": 2, "product": "Gadget", "sku": "ORB-2", "price": "42.00"},
            ]
        )
    )

    table_checkbox_column = (
        Table.make()
        .columns(
            [
                TextColumn.make("title").searchable(),
                CheckboxColumn.make("approved").label("OK").align_center(),
                CheckboxColumn.make("featured")
                .align_center()
                .disabled(lambda record=None, **_: not record.get("approved")),
            ]
        )
        .records(
            [
                {"id": 1, "title": "Great write-up", "approved": True, "featured": False},
                {"id": 2, "title": "Needs edits", "approved": False, "featured": False},
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

    table_tags_column = (
        Table.make()
        .columns(
            [
                TextColumn.make("title").searchable().sortable().weight("bold"),
                TagsColumn.make("tags").color("primary").limit(3),
                TagsColumn.make("topics").separator(";"),
            ]
        )
        .records(
            [
                {
                    "id": 1,
                    "title": "Orbit tables",
                    "tags": ["docs", "ui", "tables", "polish"],
                    "topics": "python;html",
                },
                {"id": 2, "title": "Conduit hosts", "tags": ["live"], "topics": "conduit"},
            ]
        )
    )

    table_view_column = (
        Table.make()
        .columns(
            [
                TextColumn.make("company").searchable().sortable(),
                ViewColumn.make("contact").content(
                    lambda record=None, **_: (
                        f'<strong>{e(record.get("name", ""))}</strong><br />'
                        f'<a href="mailto:{e(record.get("email", ""))}">'
                        f'{e(record.get("email", ""))}</a>'
                    ),
                ),
                ViewColumn.make("progress")
                .label("Progress")
                .content(lambda state=None, **_: f"{int(state or 0)}%")
                .url(lambda record=None, **_: f"/projects/{record['id']}"),
            ]
        )
        .records(
            [
                {
                    "id": 1,
                    "company": "Acme",
                    "name": "Ada Lovelace",
                    "email": "ada@acme.test",
                    "progress": 80,
                },
                {
                    "id": 2,
                    "company": "Orbit Labs",
                    "name": "Grace Hopper",
                    "email": "grace@orbitlabs.test",
                    "progress": 45,
                },
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
                FilterGroup.make("visibility")
                .label("Visibility")
                .filters(
                    [
                        SelectFilter.make("status")
                        .label("Status")
                        .options({"draft": "Draft", "published": "Published"}),
                        Filter.make("featured")
                        .label("Featured")
                        .toggle()
                        .query(lambda q, value: [r for r in q if r.get("featured")]),
                    ]
                ),
            ]
        )
        .filter_state({"status": "published", "featured": True})
        .records(
            [
                {"title": "Published one", "status": "published", "featured": True},
                {"title": "Drafty", "status": "draft", "featured": False},
            ]
        )
        .header_actions([CreateAction.make().url("/create")])
    )

    table_filters_deferred = (
        Table.make()
        .columns([TextColumn.make("title").searchable(), TextColumn.make("status")])
        .filters(
            [
                SelectFilter.make("status").options(
                    {"draft": "Draft", "published": "Published"}
                )
            ]
        )
        .defer_filters()
        .filter_state({"status": "draft"})
        .records(
            [
                {"title": "Draft note", "status": "draft"},
                {"title": "Live post", "status": "published"},
            ]
        )
    )

    table_filters_ternary = (
        Table.make()
        .columns(
            [
                TextColumn.make("title"),
                TextColumn.make("featured").badge(),
            ]
        )
        .filters(
            [
                TernaryFilter.make("featured")
                .label("Featured")
                .true_label("Featured")
                .false_label("Not featured")
                .placeholder("Any"),
                TrashedFilter.make(),
            ]
        )
        .filter_state({"featured": "1"})
        .records(
            [
                {"title": "Pinned", "featured": True, "deleted_at": None},
                {"title": "Archived", "featured": False, "deleted_at": "2024-01-01"},
            ]
        )
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
        .bulk_actions([DeleteBulkAction.make()])
        .striped()
    )
    table_actions_html = static_selection_chrome(
        table_actions.render(selected=["1"]),
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
    infolist_variants = build_infolist_variants()
    action_variants = build_action_variants()
    widget_variants = build_widget_variants()
    navigation_variants = build_navigation_variants()
    notification_variants = build_notification_variants()
    tenancy_variants = build_tenancy_variants()
    resource_variants = build_resource_variants()

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
        *(
            shot(sid, label, html)
            for sid, (label, html) in infolist_variants.items()
        ),
        *(
            shot(sid, label, html)
            for sid, (label, html) in action_variants.items()
        ),
        *(
            shot(sid, label, html)
            for sid, (label, html) in widget_variants.items()
        ),
        *(
            shot(sid, label, html)
            for sid, (label, html) in navigation_variants.items()
        ),
        *(
            shot(sid, label, html)
            for sid, (label, html) in notification_variants.items()
        ),
        *(
            shot(sid, label, html)
            for sid, (label, html) in tenancy_variants.items()
        ),
        *(
            shot(sid, label, html)
            for sid, (label, html) in resource_variants.items()
        ),
        shot("tables/overview", "Tables overview", table.render()),
        shot("tables/overview-columns", "Overview — columns", table_overview_columns.render()),
        shot(
            "tables/overview-searchable",
            "Overview — searchable",
            table_overview_searchable.render(),
        ),
        shot(
            "tables/overview-sortable",
            "Overview — sortable",
            table_overview_sortable.render(),
        ),
        shot(
            "tables/overview-relationships",
            "Overview — relationship columns",
            table_overview_relationships.render(),
        ),
        shot(
            "tables/columns-overview",
            "Columns overview — shared APIs",
            table_columns_overview.render(),
        ),
        shot(
            "tables/columns-overview-manager",
            "Columns overview — column manager",
            table_columns_overview_manager.render(toggled_columns={"website": False}),
        ),
        shot(
            "tables/overview-pagination",
            "Overview — pagination",
            table_overview_pagination.render(),
        ),
        shot(
            "tables/overview-pagination-disabled",
            "Overview — pagination disabled",
            table_overview_pagination_disabled.render(),
        ),
        shot(
            "tables/overview-heading",
            "Overview — heading",
            table_overview_heading.render(),
        ),
        shot(
            "tables/overview-reorder",
            "Overview — reorder",
            table_overview_reorder.render(),
        ),
        shot(
            "tables/overview-striped",
            "Overview — striped rows",
            table_overview_striped.render(),
        ),
        shot("tables/money", "Money / currency", table_money.render()),
        shot("tables/text-features", "Text column features", table_text.render()),
        shot(
            "tables/text-formatting",
            "Text — color, size, weight, font",
            table_text_formatting.render(),
        ),
        shot("tables/text-icons", "Text — icons", table_text_icons.render()),
        shot("tables/icon-boolean", "Icon + boolean", table_icons.render()),
        shot("tables/icon-colors", "Icon — colors + sizes", table_icon_colors.render()),
        shot("tables/image-color", "Image + color", table_media.render()),
        shot("tables/image-stacked", "Image — stacked", table_image_stacked.render()),
        shot("tables/editable", "Editable columns", table_editable.render()),
        shot("tables/select-column", "Select column", table_select_column.render()),
        shot("tables/toggle-column", "Toggle column", table_toggle_column.render()),
        shot(
            "tables/text-input-column",
            "Text input column",
            table_text_input_column.render(),
        ),
        shot("tables/checkbox-column", "Checkbox column", table_checkbox_column.render()),
        shot("tables/badge-column", "Badge column", table_badge_column.render()),
        shot("tables/boolean-column", "Boolean column", table_boolean_column.render()),
        shot("tables/tags-column", "Tags column", table_tags_column.render()),
        shot("tables/tags-view", "Tags + view", table_tags.render()),
        shot("tables/view-column", "View column", table_view_column.render()),
        shot("tables/column-group", "Column group", table_group_cols.render()),
        shot("tables/layout", "Cell layouts", table_layout.render()),
        shot(
            "tables/filters",
            "Filters chrome",
            static_filters_open(table_filters.render()),
        ),
        shot(
            "tables/filters-deferred",
            "Filters deferred",
            static_filters_open(table_filters_deferred.render()),
        ),
        shot(
            "tables/filters-ternary",
            "Filters ternary + trashed",
            static_filters_open(table_filters_ternary.render()),
        ),
        shot("tables/summaries", "Summaries", table_summaries.render()),
        shot("tables/grouping", "Grouped rows", table_grouping.render()),
        shot("tables/actions", "Row / bulk actions", table_actions_html),
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
        shot("schemas/overview", "Schemas overview", schema_overview),
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
[data-shot^="actions/"] .or-gallery-modal .or-modal {{
  display: block !important;
  position: relative;
  left: auto;
  top: auto;
  transform: none;
  margin: 0 auto;
}}
[data-shot^="actions/"] .or-gallery-modal .or-modal-slide {{
  position: relative;
  right: auto;
  bottom: auto;
  width: min(22rem, 100%);
  min-height: 16rem;
}}
[data-shot^="actions/"] .or-dropdown-menu {{
  display: block !important;
  position: static;
  margin-top: 0.5rem;
}}
[data-shot^="navigation/user-menu"] .or-user-menu-panel {{
  display: block !important;
  position: absolute;
  right: 0;
  top: calc(100% + 0.35rem);
  z-index: 40;
  min-width: 14rem;
}}
[data-shot="users/tenancy/menu"] .or-tenant-menu {{
  display: block !important;
  position: absolute;
  right: 0;
  top: calc(100% + 0.35rem);
  z-index: 40;
  min-width: 14rem;
}}
[data-shot="navigation/overview/subgroups"] .or-topnav-dropdown .or-topnav-menu,
[data-shot="navigation/overview"] .or-topnav-dropdown.is-active .or-topnav-menu {{
  display: block !important;
}}
html, body {{
  margin: 0;
  font-family: var(--or-font);
  background: #ffffff;
  color: var(--or-ink);
}}
body.dark {{
  background: #140f0d;
  color: #faf7f5;
}}
.gallery-header {{
  max-width: 1480px;
  margin: 0 auto;
  padding: 2rem 1.5rem 0.5rem;
}}
.gallery-header h1 {{ margin: 0 0 0.35rem; font-size: 1.5rem; }}
.gallery-header p {{ margin: 0; color: var(--or-muted); font-size: 0.95rem; }}
.gallery-header code {{ font-size: 0.85em; }}
.gallery-section {{
  max-width: 1480px;
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
  overflow: visible;
}}
.or-shot:has(.or-combobox) {{
  padding-bottom: 14rem; /* room for open combobox dropdown in screenshots */
}}
body.dark .or-shot {{
  background: #1c1613;
  border-color: #3a302b;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
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
<script src="../vendor/orbit/chart.umd.min.js"></script>
<script src="../vendor/orbit/apexcharts.min.js"></script>
<script src="../vendor/orbit/orbit.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.8/dist/cdn.min.js"></script>
<script>
document.addEventListener("alpine:initialized", () => {{
  const openShot = (shot) => {{
    const root = shot.querySelector('[x-data="orbitCombobox"]');
    if (!root || typeof Alpine === "undefined") return;
    const data = Alpine.$data(root);
    if (!data || typeof data.openPanel !== "function") return;
    data.openPanel();
  }};
  document
    .querySelectorAll(
      '[data-shot^="forms/select/"], [data-shot^="forms/multi-select/"], [data-shot="forms/select"]',
    )
    .forEach(openShot);
}});
</script>
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
