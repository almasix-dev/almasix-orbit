"""Per-variant HTML builders for the Orbit screenshot gallery."""

from __future__ import annotations

from almasix.orbit.forms.components import (
    Block,
    Builder,
    Checkbox,
    CheckboxList,
    ColorPicker,
    DatePicker,
    DateTimePicker,
    FileUpload,
    Hidden,
    KeyValue,
    MarkdownEditor,
    MoneyInput,
    MorphToSelect,
    MultiSelect,
    OneTimeCodeInput,
    Placeholder,
    Radio,
    Repeater,
    RichEditor,
    Select,
    Slider,
    TagsInput,
    TextInput,
    Textarea,
    TimePicker,
    Toggle,
    ToggleButtons,
    ViewField,
)
from almasix.orbit.forms.form import Form
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


def _form(*components, state: dict | None = None) -> str:
    form = Form.make().schema(list(components))
    if state:
        form.fill(state)
    return form.render()


def build_form_variants() -> dict[str, tuple[str, str]]:
    """Return ``{shot_id: (label, html)}`` for nested form field shots."""
    status_opts = {"draft": "Draft", "published": "Published", "archived": "Archived"}
    feature_opts = {
        "api": "API access",
        "sso": "SSO",
        "audit": "Audit logs",
        "support": "Priority support",
    }
    plan_opts = {"starter": "Starter", "pro": "Pro", "enterprise": "Enterprise"}
    plan_desc = {
        "starter": "For side projects",
        "pro": "For growing teams",
        "enterprise": "Custom SLA",
    }

    return {
        # TextInput
        "forms/text-input/basic": (
            "Text input — basic",
            TextInput.make("title")
            .label("Title")
            .placeholder("Enter a title…")
            .helper_text("Shown on the public page.")
            .render("Launch Orbit"),
        ),
        "forms/text-input/email": (
            "Text input — email",
            TextInput.make("email")
            .email()
            .label("Email")
            .placeholder("you@acme.test")
            .render("ada@orbit.test"),
        ),
        "forms/text-input/password": (
            "Text input — password",
            TextInput.make("password")
            .password()
            .revealable()
            .label("Password")
            .placeholder("••••••••")
            .render("secret-pass"),
        ),
        "forms/text-input/url": (
            "Text input — url",
            TextInput.make("website").url().label("Website").placeholder("https://").render(
                "https://orbit.almasix.com"
            ),
        ),
        "forms/text-input/tel": (
            "Text input — tel",
            TextInput.make("phone").tel().label("Phone").placeholder("+1 555 0100").render(
                "+254 700 000000"
            ),
        ),
        "forms/text-input/numeric": (
            "Text input — numeric",
            TextInput.make("quantity").numeric().label("Quantity").min_value(0).max_value(99).render(
                "12"
            ),
        ),
        "forms/text-input/prefix": (
            "Text input — prefix",
            TextInput.make("price")
            .label("Price")
            .prefix("$")
            .numeric()
            .render("49.99"),
        ),
        "forms/text-input/suffix": (
            "Text input — suffix",
            TextInput.make("weight").label("Weight").suffix("kg").numeric().render("2.5"),
        ),
        "forms/text-input/prefix-icon": (
            "Text input — prefix icon",
            TextInput.make("search")
            .label("Search")
            .prefix_icon("heroicon-o-magnifying-glass")
            .placeholder("Filter records…")
            .render("orbit"),
        ),
        "forms/text-input/suffix-icon": (
            "Text input — suffix icon",
            TextInput.make("slug")
            .label("Slug")
            .suffix_icon("heroicon-o-link")
            .render("launch-orbit"),
        ),
        "forms/text-input/required": (
            "Text input — required",
            TextInput.make("name").label("Name").required().render("Ada Lovelace"),
        ),
        "forms/text-input/disabled": (
            "Text input — disabled",
            TextInput.make("locked").label("Locked field").disabled().render("Cannot edit"),
        ),
        "forms/text-input/readonly": (
            "Text input — readonly",
            TextInput.make("id").label("Record ID").readonly().render("post-42"),
        ),
        "forms/text-input/copyable": (
            "Text input — copyable",
            TextInput.make("token")
            .label("API token")
            .copyable()
            .readonly()
            .render("orb_live_sk_abc123"),
        ),
        "forms/text-input/mask": (
            "Text input — mask",
            TextInput.make("card")
            .label("Card number")
            .mask("9999 9999 9999 9999")
            .render("4242 4242 4242 4242"),
        ),
        "forms/text-input/datalist": (
            "Text input — datalist",
            TextInput.make("city")
            .label("City")
            .datalist(["Nairobi", "London", "Berlin", "Tokyo"])
            .render("Nairobi"),
        ),
        "forms/text-input/with-hint": (
            "Text input — with hint",
            TextInput.make("slug")
            .label("Slug")
            .hint("Used in the public URL.")
            .hint_icon("heroicon-o-information-circle")
            .render("launch-orbit"),
        ),
        # Select
        "forms/select/basic": (
            "Select — basic",
            Select.make("status").label("Status").options(status_opts).render("published"),
        ),
        "forms/select/searchable": (
            "Select — searchable",
            Select.make("status")
            .label("Status")
            .options(status_opts)
            .searchable()
            .render("draft"),
        ),
        "forms/select/multiple": (
            "Select — multiple",
            MultiSelect.make("tags")
            .label("Tags")
            .options({"orbit": "Orbit", "tables": "Tables", "forms": "Forms"})
            .render(["orbit", "forms"]),
        ),
        # Textarea
        "forms/textarea/basic": (
            "Textarea — basic",
            Textarea.make("bio")
            .label("Bio")
            .placeholder("Tell us about yourself…")
            .helper_text("Brief summary for your profile.")
            .render("Editor at Orbit."),
        ),
        "forms/textarea/rows": (
            "Textarea — rows",
            Textarea.make("notes").label("Notes").rows(6).render(
                "Line one.\nLine two.\nLine three."
            ),
        ),
        # Checkbox / Toggle
        "forms/checkbox/basic": (
            "Checkbox — basic",
            Checkbox.make("terms").label("Accept terms and conditions").render(True),
        ),
        "forms/toggle/basic": (
            "Toggle — basic",
            Toggle.make("active").label("Active account").render(True),
        ),
        # Date pickers
        "forms/date-picker/basic": (
            "Date picker — basic",
            DatePicker.make("starts").label("Starts on").render("2026-09-18"),
        ),
        "forms/date-picker/min-max": (
            "Date picker — min/max",
            DatePicker.make("window")
            .label("Window")
            .min_date("2026-01-01")
            .max_date("2026-12-31")
            .render("2026-06-15"),
        ),
        "forms/date-time-picker/basic": (
            "Date time picker — basic",
            DateTimePicker.make("published_at").label("Published at").render("2026-09-18T09:00"),
        ),
        "forms/date-time-picker/min-max": (
            "Date time picker — min/max",
            DateTimePicker.make("scheduled")
            .label("Scheduled")
            .min_date("2026-01-01")
            .max_date("2026-12-31")
            .render("2026-09-18T14:30"),
        ),
        "forms/time-picker/basic": (
            "Time picker — basic",
            TimePicker.make("remind_at").label("Remind at").render("09:00"),
        ),
        "forms/time-picker/min-max": (
            "Time picker — min/max",
            TimePicker.make("slot")
            .label("Time slot")
            .min_date("08:00")
            .max_date("18:00")
            .render("10:30"),
        ),
        # File upload
        "forms/file-upload/basic": (
            "File upload — basic",
            FileUpload.make("attachment").label("Attachment").render(),
        ),
        "forms/file-upload/image": (
            "File upload — image",
            FileUpload.make("cover").image().label("Cover image").render(),
        ),
        "forms/file-upload/avatar": (
            "File upload — avatar",
            FileUpload.make("avatar").avatar().label("Avatar").render(),
        ),
        # Radio / CheckboxList
        "forms/radio/basic": (
            "Radio — basic",
            Radio.make("plan").label("Plan").options(plan_opts).render("pro"),
        ),
        "forms/radio/with-descriptions": (
            "Radio — with descriptions",
            Radio.make("plan")
            .label("Plan")
            .options(plan_opts)
            .descriptions(plan_desc)
            .render("pro"),
        ),
        "forms/radio/columns": (
            "Radio — columns",
            Radio.make("plan")
            .label("Plan")
            .options(plan_opts)
            .options_columns(2)
            .render("starter"),
        ),
        "forms/checkbox-list/basic": (
            "Checkbox list — basic",
            CheckboxList.make("features")
            .label("Features")
            .options(feature_opts)
            .render(["api", "sso"]),
        ),
        "forms/checkbox-list/bulk-toggle": (
            "Checkbox list — bulk toggle",
            CheckboxList.make("features")
            .label("Features")
            .options(feature_opts)
            .descriptions({"sso": "SAML + OIDC", "audit": "90-day retention"})
            .bulk_toggleable()
            .options_columns(2)
            .render(["api"]),
        ),
        # Tags
        "forms/tags-input/basic": (
            "Tags input — basic",
            TagsInput.make("tags").label("Tags").render(["orbit", "forms"]),
        ),
        "forms/tags-input/suggestions": (
            "Tags input — suggestions",
            TagsInput.make("tags")
            .label("Tags")
            .suggestions(["orbit", "tables", "forms", "panels"])
            .reorderable()
            .render(["orbit", "tables"]),
        ),
        # Color / Money
        "forms/color-picker/basic": (
            "Color picker — basic",
            ColorPicker.make("brand").label("Brand color").render("#286291"),
        ),
        "forms/money-input/usd": (
            "Money input — USD",
            MoneyInput.make("price").label("Price").currency("USD").render(49.99),
        ),
        "forms/money-input/eur": (
            "Money input — EUR",
            MoneyInput.make("price").label("Price").currency("EUR").render(49.99),
        ),
        # Editors
        "forms/rich-editor/basic": (
            "Rich editor — basic",
            RichEditor.make("body")
            .label("Body")
            .toolbar_buttons(["bold", "italic", "link", "heading"])
            .render("<p>Hello from <strong>Orbit</strong>.</p>"),
        ),
        "forms/markdown-editor/basic": (
            "Markdown editor — basic",
            MarkdownEditor.make("readme")
            .label("README")
            .rows(5)
            .render("# Orbit\n\nShip admin UIs without the SPA tax."),
        ),
        # KeyValue
        "forms/key-value/basic": (
            "Key-value — basic",
            KeyValue.make("meta").label("Metadata").render({}),
        ),
        "forms/key-value/populated": (
            "Key-value — populated",
            KeyValue.make("meta")
            .label("Metadata")
            .render({"version": "1.0", "env": "production"}),
        ),
        # Repeater
        "forms/repeater/basic": (
            "Repeater — basic",
            Repeater.make("items")
            .label("Line items")
            .schema(
                [
                    TextInput.make("name").label("Name"),
                    TextInput.make("qty").label("Qty"),
                ]
            )
            .default_items(1)
            .render([{"name": "Widget", "qty": "2"}]),
        ),
        "forms/repeater/cloneable-reorderable": (
            "Repeater — cloneable + reorderable",
            Repeater.make("items")
            .label("Line items")
            .schema([TextInput.make("name").label("Name"), TextInput.make("qty").label("Qty")])
            .cloneable()
            .reorderable()
            .collapsible()
            .default_items(2)
            .render([{"name": "Widget", "qty": "2"}, {"name": "Gadget", "qty": "1"}]),
        ),
        "forms/repeater/table": (
            "Repeater — table layout",
            Repeater.make("items")
            .label("Line items")
            .schema([TextInput.make("name").label("Name"), TextInput.make("qty").label("Qty")])
            .table(["Name", "Qty"])
            .default_items(2)
            .render([{"name": "Widget", "qty": "2"}, {"name": "Gadget", "qty": "1"}]),
        ),
        # Builder / toggles / morph
        "forms/builder/basic": (
            "Builder — basic",
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
            .render([{"type": "hero", "heading": "Welcome to Orbit"}]),
        ),
        "forms/toggle-buttons/basic": (
            "Toggle buttons — basic",
            ToggleButtons.make("visibility")
            .label("Visibility")
            .options({"public": "Public", "private": "Private", "draft": "Draft"})
            .render("public"),
        ),
        "forms/morph-to-select/basic": (
            "Morph-to select — basic",
            MorphToSelect.make("assignee")
            .label("Assignee")
            .searchable()
            .types(
                [
                    {"type": "user", "label": "User", "options": {"1": "Ada", "2": "Grace"}},
                    {"type": "team", "label": "Team", "options": {"10": "Engineering"}},
                ]
            )
            .render({"type": "user", "id": "1"}),
        ),
        # Misc fields
        "forms/placeholder/basic": (
            "Placeholder — basic",
            Placeholder.make("note")
            .content("This slot is reserved for future fields.")
            .render(),
        ),
        "forms/hidden/basic": (
            "Hidden — note",
            '<p class="or-helper">Hidden fields render as '
            f'{Hidden.make("token").render("orb_secret")}'
            " — not shown in screenshots.</p>",
        ),
        "forms/one-time-code-input/basic": (
            "One-time code — basic",
            OneTimeCodeInput.make("code").label("Verification code").render("123456"),
        ),
        "forms/view-field/basic": (
            "View field — basic",
            ViewField.make("summary")
            .label("Summary")
            .content("<p>Published on <strong>18 Sep 2026</strong>.</p>")
            .render(),
        ),
        "forms/slider/basic": (
            "Slider — basic",
            Slider.make("volume").label("Volume").min_value(0).max_value(100).render(65),
        ),
    }


def build_schema_variants() -> dict[str, tuple[str, str]]:
    """Return ``{shot_id: (label, html)}`` for nested schema layout shots."""
    return {
        "schemas/section/basic": (
            "Section — basic",
            _form(
                Section.make("profile")
                .heading("Profile")
                .schema([TextInput.make("name").label("Name")]),
                state={"name": "Ada Lovelace"},
            ),
        ),
        "schemas/section/collapsible": (
            "Section — collapsible",
            _form(
                Section.make("advanced")
                .heading("Advanced")
                .collapsible()
                .collapsed()
                .schema([Toggle.make("debug").label("Debug mode")]),
                state={"debug": False},
            ),
        ),
        "schemas/section/compact": (
            "Section — compact",
            _form(
                Section.make("profile")
                .heading("Profile")
                .compact()
                .icon("heroicon-o-user")
                .schema([TextInput.make("name").label("Name")]),
                state={"name": "Ada"},
            ),
        ),
        "schemas/tabs/basic": (
            "Tabs — basic",
            _form(
                Tabs.make("main")
                .tabs(
                    {
                        "label": "General",
                        "schema": [TextInput.make("title").label("Title")],
                    },
                    {
                        "label": "SEO",
                        "schema": [TextInput.make("slug").label("Slug")],
                    },
                )
                .active_tab(0),
                state={"title": "Launch Orbit", "slug": "launch-orbit"},
            ),
        ),
        "schemas/tabs/with-badges": (
            "Tabs — with badges",
            _form(
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
                )
                .active_tab(0),
                state={"title": "Launch Orbit", "slug": "launch-orbit"},
            ),
        ),
        "schemas/wizard/basic": (
            "Wizard — basic",
            _form(
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
                )
                .start_step(0),
                state={"email": "ada@orbit.test", "name": "Ada"},
            ),
        ),
        "schemas/grid/basic": (
            "Grid — basic",
            _form(
                SchemaGrid.make()
                .columns(2)
                .schema(
                    [
                        TextInput.make("col_a").label("Column A"),
                        TextInput.make("col_b").label("Column B"),
                    ]
                ),
                state={"col_a": "Alpha", "col_b": "Beta"},
            ),
        ),
        "schemas/flex/basic": (
            "Flex — basic",
            _form(
                Flex.make()
                .from_breakpoint("md")
                .schema(
                    [
                        TextInput.make("left").label("Left"),
                        TextInput.make("right").label("Right"),
                    ]
                ),
                state={"left": "Sidebar", "right": "Main"},
            ),
        ),
        "schemas/group/basic": (
            "Group — basic",
            _form(
                SchemaGroup.make()
                .columns(2)
                .schema(
                    [
                        TextInput.make("sku").label("SKU"),
                        TextInput.make("qty").label("Quantity"),
                    ]
                ),
                state={"sku": "ORB-1", "qty": "12"},
            ),
        ),
        "schemas/split/basic": (
            "Split — basic",
            _form(
                SchemaSplit.make()
                .from_breakpoint("md")
                .schema(
                    [
                        Textarea.make("notes").label("Notes").rows(2),
                        FileUpload.make("attachment").label("Attachment"),
                    ]
                ),
                state={"notes": "Handle with care."},
            ),
        ),
        "schemas/fieldset/basic": (
            "Fieldset — basic",
            _form(
                Fieldset.make("billing")
                .label("Billing address")
                .schema(
                    [
                        TextInput.make("line1").label("Line 1"),
                        TextInput.make("city").label("City"),
                    ]
                ),
                state={"line1": "42 Orbit Way", "city": "Nairobi"},
            ),
        ),
        "schemas/callout/info": (
            "Callout — info",
            Callout.make().info().label("Tip").description("Fill these fields before saving.").render(),
        ),
        "schemas/callout/danger": (
            "Callout — danger",
            Callout.make()
            .danger()
            .label("Danger")
            .description("This action cannot be undone.")
            .render(),
        ),
        "schemas/callout/success": (
            "Callout — success",
            Callout.make()
            .success()
            .label("Saved")
            .description("Your changes were published.")
            .render(),
        ),
        "schemas/empty-state/basic": (
            "Empty state — basic",
            EmptyState.make()
            .heading("No drafts")
            .description("Create one when you are ready.")
            .render(),
        ),
        "schemas/primes/text": (
            "Prime — text",
            Text.make().content("Published").badge().color("success").render(),
        ),
        "schemas/primes/icon": (
            "Prime — icon",
            Icon.make().icon("heroicon-o-check").color("success").size("lg").render(),
        ),
        "schemas/primes/image": (
            "Prime — image",
            Image.make()
            .src("https://api.dicebear.com/9.x/shapes/svg?seed=orbit")
            .image_size(48)
            .render(),
        ),
        "schemas/primes/list": (
            "Prime — list",
            UnorderedList.make().items(["Tables", "Forms", "Panels"]).bullet_size("sm").render(),
        ),
    }
