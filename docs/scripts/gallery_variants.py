"""Per-variant HTML builders for the Orbit screenshot gallery."""

from __future__ import annotations

from enum import Enum

from almasix.orbit.actions import (
    Action,
    ActionGroup,
    CreateAction,
    DeleteAction,
    EditAction,
    ExportAction,
    ForceDeleteAction,
    ImportAction,
    ReplicateAction,
    RestoreAction,
    ViewAction,
)
from almasix.orbit.forms.components import (
    Block,
    Builder,
    Checkbox,
    CheckboxList,
    CodeEditor,
    ColorPicker,
    DatePicker,
    DateTimePicker,
    FileUpload,
    Hidden,
    KeyValue,
    MarkdownEditor,
    ModalTableSelect,
    MoneyInput,
    MorphToSelect,
    MultiSelect,
    OneTimeCodeInput,
    Placeholder,
    Radio,
    RelationshipRepeater,
    Repeater,
    RichEditor,
    Select,
    Slider,
    TagsInput,
    Textarea,
    TextInput,
    TimePicker,
    Toggle,
    ToggleButtons,
    ViewField,
)
from almasix.orbit.forms.form import Form
from almasix.orbit.infolists import (
    CodeEntry,
    ColorEntry,
    IconEntry,
    ImageEntry,
    Infolist,
    KeyValueEntry,
    RepeatableEntry,
    TextEntry,
    ViewEntry,
)
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


class _Status(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class _Visibility(Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    DRAFT = "draft"


def _form(*components, state: dict | None = None, operation: str | None = None) -> str:
    form = Form.make().schema(list(components))
    if operation:
        form.operation(operation)
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
    tag_opts = {"orbit": "Orbit", "tables": "Tables", "forms": "Forms", "panels": "Panels"}
    author_opts = {"1": "Ada Lovelace", "2": "Grace Hopper", "3": "Alan Turing"}
    builder_blocks = [
        Block.make("hero")
        .label("Hero")
        .icon("heroicon-o-star")
        .schema([TextInput.make("heading").label("Heading")]),
        Block.make("text")
        .label("Text")
        .icon("heroicon-o-document-text")
        .schema([Textarea.make("body").label("Body").rows(2)]),
    ]

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
        "forms/text-input/autocapitalize": (
            "Text input — autocapitalize",
            TextInput.make("name")
            .label("Display name")
            .autocapitalize("words")
            .render("ada lovelace"),
        ),
        "forms/text-input/content-slots": (
            "Text input — content slots",
            TextInput.make("title")
            .label("Title")
            .above_label("<span class='or-helper'>Above label</span>")
            .below_label("<span class='or-helper'>Below label</span>")
            .above_content("<span class='or-helper'>Above content</span>")
            .below_content("<span class='or-helper'>Below content</span>")
            .render("Launch Orbit"),
        ),
        "forms/text-input/length": (
            "Text input — length",
            TextInput.make("pin").label("PIN").length(4).render("4242"),
        ),
        "forms/text-input/mark-as-required": (
            "Text input — mark as required",
            TextInput.make("nickname")
            .label("Nickname")
            .mark_as_required()
            .helper_text("Shows the required asterisk without a required rule.")
            .render("Ada"),
        ),
        "forms/text-input/prefix-icon-color": (
            "Text input — prefix icon color",
            TextInput.make("search")
            .label("Search")
            .prefix_icon("heroicon-o-magnifying-glass")
            .prefix_icon_color("primary")
            .render("orbit"),
        ),
        "forms/text-input/strip-characters": (
            "Text input — strip characters",
            TextInput.make("code")
            .label("Promo code")
            .strip_characters("- ")
            .helper_text("Dashes and spaces are stripped on dehydrate.")
            .render("ORB-2026"),
        ),
        "forms/text-input/tel-regex": (
            "Text input — tel regex",
            TextInput.make("phone")
            .tel()
            .label("Phone")
            .tel_regex(r"^\+\d{8,15}$")
            .render("+254700000000"),
        ),
        "forms/text-input/trim": (
            "Text input — trim",
            TextInput.make("title")
            .label("Title")
            .trim()
            .helper_text("Leading and trailing whitespace is trimmed.")
            .render("  Launch Orbit  "),
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
        "forms/select/allow-html": (
            "Select — allow HTML",
            Select.make("status")
            .label("Status")
            .options(
                {
                    "draft": "<em>Draft</em>",
                    "published": "<strong>Published</strong>",
                    "archived": "Archived",
                }
            )
            .allow_html()
            .native(False)
            .render("published"),
        ),
        "forms/select/boolean": (
            "Select — boolean",
            Select.make("featured").label("Featured").boolean().render(True),
        ),
        "forms/select/create-option": (
            "Select — create option",
            Select.make("status")
            .label("Status")
            .options(status_opts)
            .native(False)
            .create_option_form([TextInput.make("label").label("Label").required()])
            .create_option_using(lambda label, **_: label)
            .render("draft"),
        ),
        "forms/select/custom-search": (
            "Select — custom search",
            Select.make("author")
            .label("Author")
            .options(author_opts)
            .searchable()
            .native(False)
            .get_search_results_using(
                lambda search, **_: {
                    k: v for k, v in author_opts.items() if search.lower() in v.lower()
                }
            )
            .render("1"),
        ),
        "forms/select/disable-option": (
            "Select — disable option",
            Select.make("status")
            .label("Status")
            .options(status_opts)
            .disable_option_when(lambda value, **_: value == "archived")
            .render("draft"),
        ),
        "forms/select/edit-option": (
            "Select — edit option",
            Select.make("status")
            .label("Status")
            .options(status_opts)
            .native(False)
            .edit_option_action("editStatus")
            .render("published"),
        ),
        "forms/select/enum": (
            "Select — enum",
            Select.make("status").label("Status").enum(_Status).render("published"),
        ),
        "forms/select/grouped": (
            "Select — grouped",
            Select.make("topic")
            .label("Topic")
            .options(
                {
                    "Product": {"tables": "Tables", "forms": "Forms"},
                    "Ops": {"panels": "Panels", "auth": "Auth"},
                }
            )
            .render("forms"),
        ),
        "forms/select/messages": (
            "Select — messages",
            Select.make("author")
            .label("Author")
            .options(author_opts)
            .searchable()
            .native(False)
            .search_prompt("Find an author…")
            .no_search_results_message("No authors match.")
            .loading_message("Loading authors…")
            .searching_message("Searching…")
            .render("1"),
        ),
        "forms/select/min-max-items": (
            "Select — min/max items",
            Select.make("tags")
            .label("Tags")
            .options(tag_opts)
            .multiple()
            .min_items(1)
            .max_items(3)
            .render(["orbit", "forms"]),
        ),
        "forms/select/native": (
            "Select — non-native",
            Select.make("status")
            .label("Status")
            .options(status_opts)
            .native(False)
            .searchable()
            .render("draft"),
        ),
        "forms/select/options-limit": (
            "Select — options limit",
            Select.make("author")
            .label("Author")
            .options(author_opts)
            .options_limit(2)
            .searchable()
            .native(False)
            .render("1"),
        ),
        "forms/select/preload": (
            "Select — preload",
            Select.make("author")
            .label("Author")
            .options(author_opts)
            .relationship("author", "name")
            .searchable()
            .preload()
            .render("1"),
        ),
        "forms/select/relationship": (
            "Select — relationship",
            Select.make("author_id")
            .label("Author")
            .relationship("author", "name")
            .options(author_opts)
            .searchable()
            .render("1"),
        ),
        "forms/select/reorderable": (
            "Select — reorderable",
            Select.make("tags")
            .label("Tags")
            .options(tag_opts)
            .multiple()
            .reorderable()
            .render(["forms", "orbit"]),
        ),
        "forms/select/selectable-placeholder": (
            "Select — selectable placeholder",
            Select.make("status")
            .label("Status")
            .options(status_opts)
            .selectable_placeholder()
            .placeholder("Choose a status")
            .render(None),
        ),
        "forms/select/wrap": (
            "Select — wrap labels",
            Select.make("plan")
            .label("Plan")
            .options(
                {
                    "starter": "Starter — for side projects and experiments",
                    "pro": "Pro — for growing product teams",
                    "enterprise": "Enterprise — custom SLA and support",
                }
            )
            .wrap()
            .native(False)
            .render("pro"),
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
        "forms/textarea/autosize": (
            "Textarea — autosize",
            Textarea.make("notes")
            .label("Notes")
            .autosize()
            .render("Grows with content.\nSecond line."),
        ),
        "forms/textarea/validation": (
            "Textarea — validation",
            Textarea.make("bio")
            .label("Bio")
            .required()
            .min_length(10)
            .max_length(280)
            .render("Editor at Orbit."),
        ),
        # Checkbox / Toggle
        "forms/checkbox/basic": (
            "Checkbox — basic",
            Checkbox.make("terms").label("Accept terms and conditions").render(True),
        ),
        "forms/checkbox/default": (
            "Checkbox — default",
            Checkbox.make("newsletter").label("Subscribe to newsletter").default(True).render(True),
        ),
        "forms/checkbox/disabled": (
            "Checkbox — disabled",
            Checkbox.make("locked").label("Locked preference").disabled().render(True),
        ),
        "forms/checkbox/inline": (
            "Checkbox — inline",
            Checkbox.make("remember").label("Remember me").inline().render(True),
        ),
        "forms/checkbox/required": (
            "Checkbox — required",
            Checkbox.make("terms").label("Accept terms").required().render(False),
        ),
        "forms/toggle/basic": (
            "Toggle — basic",
            Toggle.make("active").label("Active account").render(True),
        ),
        "forms/toggle/colors": (
            "Toggle — colors",
            Toggle.make("featured")
            .label("Featured")
            .on_color("success")
            .off_color("danger")
            .render(True),
        ),
        "forms/toggle/default": (
            "Toggle — default",
            Toggle.make("notifications").label("Email notifications").default(True).render(True),
        ),
        "forms/toggle/icons": (
            "Toggle — icons",
            Toggle.make("dark")
            .label("Dark mode")
            .on_icon("heroicon-o-moon")
            .off_icon("heroicon-o-sun")
            .render(True),
        ),
        "forms/toggle/inline": (
            "Toggle — inline",
            Toggle.make("active").label("Active").inline().render(True),
        ),
        "forms/toggle/required-disabled": (
            "Toggle — required + disabled",
            Toggle.make("verified")
            .label("Verified")
            .required()
            .disabled()
            .render(True),
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
        "forms/date-picker/display-format": (
            "Date picker — display format",
            DatePicker.make("starts")
            .label("Starts on")
            .display_format("d/m/Y")
            .render("2026-09-18"),
        ),
        "forms/date-picker/non-native": (
            "Date picker — non-native",
            DatePicker.make("starts")
            .label("Starts on")
            .native(False)
            .render("2026-09-18"),
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
        "forms/date-time-picker/display-format": (
            "Date time picker — display format",
            DateTimePicker.make("published_at")
            .label("Published at")
            .display_format("Y-m-d H:i")
            .render("2026-09-18T09:00"),
        ),
        "forms/date-time-picker/non-native": (
            "Date time picker — non-native",
            DateTimePicker.make("published_at")
            .label("Published at")
            .native(False)
            .render("2026-09-18T09:00"),
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
        "forms/time-picker/display-format": (
            "Time picker — display format",
            TimePicker.make("remind_at")
            .label("Remind at")
            .display_format("H:i")
            .render("09:00"),
        ),
        "forms/time-picker/step": (
            "Time picker — step",
            TimePicker.make("slot").label("Time slot").step(900).render("10:30"),
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
        "forms/file-upload/accepted-types": (
            "File upload — accepted types",
            FileUpload.make("docs")
            .label("Documents")
            .accepted_file_types(["application/pdf", "image/png"])
            .helper_text("PDF or PNG only.")
            .render(),
        ),
        "forms/file-upload/disk": (
            "File upload — disk",
            FileUpload.make("attachment")
            .label("Attachment")
            .disk("s3")
            .directory("uploads/orbit")
            .visibility("private")
            .render(),
        ),
        "forms/file-upload/image-editor": (
            "File upload — image editor",
            FileUpload.make("cover")
            .image()
            .label("Cover")
            .image_editor()
            .image_editor_aspect_ratios(["16:9", "1:1"])
            .render(),
        ),
        "forms/file-upload/image-size": (
            "File upload — image size",
            FileUpload.make("cover")
            .image()
            .label("Cover")
            .image_size(min_width=800, max_width=2400, min_height=400, max_height=1600)
            .render(),
        ),
        "forms/file-upload/multiple": (
            "File upload — multiple",
            FileUpload.make("gallery")
            .label("Gallery")
            .multiple()
            .min_files(1)
            .max_files(5)
            .reorderable()
            .render(),
        ),
        "forms/file-upload/panel-layout": (
            "File upload — panel layout",
            FileUpload.make("files").label("Files").panel_layout().multiple().render(),
        ),
        "forms/file-upload/preview-actions": (
            "File upload — preview actions",
            FileUpload.make("docs")
            .label("Documents")
            .previewable()
            .openable()
            .downloadable()
            .image_preview_height(120)
            .render(),
        ),
        "forms/file-upload/size-limits": (
            "File upload — size limits",
            FileUpload.make("attachment")
            .label("Attachment")
            .min_size(10)
            .max_size(5120)
            .helper_text("10 KB – 5 MB.")
            .render(),
        ),
        "forms/file-upload/storage-flags": (
            "File upload — storage flags",
            FileUpload.make("attachment")
            .label("Attachment")
            .move_files()
            .store_files(False)
            .preserve_filenames()
            .fetch_file_information(False)
            .prevent_file_path_tampering()
            .render(),
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
        "forms/radio/boolean": (
            "Radio — boolean",
            Radio.make("featured").label("Featured").boolean().render(True),
        ),
        "forms/radio/disable-option": (
            "Radio — disable option",
            Radio.make("plan")
            .label("Plan")
            .options(plan_opts)
            .disable_option_when(lambda value, **_: value == "enterprise")
            .helper_text("Enterprise is disabled for this account.")
            .render("pro"),
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
        "forms/checkbox-list/columns": (
            "Checkbox list — columns",
            CheckboxList.make("features")
            .label("Features")
            .options(feature_opts)
            .options_columns(2)
            .render(["api", "audit"]),
        ),
        "forms/checkbox-list/descriptions": (
            "Checkbox list — descriptions",
            CheckboxList.make("features")
            .label("Features")
            .options(feature_opts)
            .descriptions(
                {
                    "api": "REST + webhooks",
                    "sso": "SAML + OIDC",
                    "audit": "90-day retention",
                    "support": "Business hours",
                }
            )
            .render(["api", "sso"]),
        ),
        "forms/checkbox-list/disable-option": (
            "Checkbox list — disable option",
            CheckboxList.make("features")
            .label("Features")
            .options(feature_opts)
            .disable_option_when(lambda value, **_: value == "support")
            .helper_text("Priority support requires Pro.")
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
        "forms/tags-input/reorderable": (
            "Tags input — reorderable",
            TagsInput.make("tags")
            .label("Tags")
            .reorderable()
            .render(["forms", "orbit", "tables"]),
        ),
        "forms/tags-input/separator": (
            "Tags input — separator",
            TagsInput.make("tags")
            .label("Tags")
            .separator("|")
            .helper_text("Pipe-separated tags.")
            .render(["orbit", "forms"]),
        ),
        # Color / Money
        "forms/color-picker/basic": (
            "Color picker — basic",
            ColorPicker.make("brand").label("Brand color").render("#286291"),
        ),
        "forms/color-picker/required": (
            "Color picker — required",
            ColorPicker.make("brand").label("Brand color").required().render("#286291"),
        ),
        "forms/color-picker/with-hint": (
            "Color picker — with hint",
            ColorPicker.make("brand")
            .label("Brand color")
            .hint("Used on buttons and links.")
            .hint_icon("heroicon-o-information-circle")
            .render("#286291"),
        ),
        "forms/money-input/usd": (
            "Money input — USD",
            MoneyInput.make("price").label("Price").currency("USD").render(49.99),
        ),
        "forms/money-input/eur": (
            "Money input — EUR",
            MoneyInput.make("price").label("Price").currency("EUR").render(49.99),
        ),
        "forms/money-input/bounds": (
            "Money input — bounds",
            MoneyInput.make("price")
            .label("Price")
            .currency("USD")
            .min_value(0)
            .max_value(10000)
            .render(49.99),
        ),
        "forms/money-input/locale": (
            "Money input — locale",
            MoneyInput.make("price")
            .label("Price")
            .currency("EUR")
            .locale("de_DE")
            .render(49.99),
        ),
        # Editors
        "forms/rich-editor/basic": (
            "Rich editor — basic",
            RichEditor.make("body")
            .label("Body")
            .toolbar_buttons(["bold", "italic", "link", "heading"])
            .render("<p>Hello from <strong>Orbit</strong>.</p>"),
        ),
        "forms/rich-editor/disabled": (
            "Rich editor — disabled",
            RichEditor.make("body")
            .label("Body")
            .disabled()
            .render("<p>Read-only body.</p>"),
        ),
        "forms/rich-editor/live": (
            "Rich editor — live",
            RichEditor.make("body")
            .label("Body")
            .live()
            .toolbar_buttons(["bold", "italic"])
            .render("<p>Live updates on change.</p>"),
        ),
        "forms/rich-editor/toolbar": (
            "Rich editor — toolbar",
            RichEditor.make("body")
            .label("Body")
            .toolbar_buttons(["bold", "italic", "strike", "link", "bulletList", "orderedList", "blockquote"])
            .render("<p>Expanded toolbar.</p>"),
        ),
        "forms/markdown-editor/basic": (
            "Markdown editor — basic",
            MarkdownEditor.make("readme")
            .label("README")
            .rows(5)
            .render("# Orbit\n\nShip admin UIs without the SPA tax."),
        ),
        "forms/markdown-editor/autosize": (
            "Markdown editor — autosize",
            MarkdownEditor.make("readme")
            .label("README")
            .autosize()
            .render("# Orbit\n\nAutosized markdown."),
        ),
        "forms/markdown-editor/required": (
            "Markdown editor — required",
            MarkdownEditor.make("readme")
            .label("README")
            .required()
            .rows(4)
            .render("# Required"),
        ),
        "forms/code-editor/basic": (
            "Code editor — basic",
            CodeEditor.make("snippet")
            .label("Snippet")
            .rows(6)
            .render("print('hello orbit')\n"),
        ),
        "forms/code-editor/autosize": (
            "Code editor — autosize",
            CodeEditor.make("snippet")
            .label("Snippet")
            .autosize()
            .language("python")
            .render("def greet():\n    return 'orbit'\n"),
        ),
        "forms/code-editor/language": (
            "Code editor — language",
            CodeEditor.make("snippet")
            .label("Snippet")
            .language("javascript")
            .rows(5)
            .render("const greet = () => 'orbit';\n"),
        ),
        "forms/code-editor/required": (
            "Code editor — required",
            CodeEditor.make("snippet")
            .label("Snippet")
            .language("python")
            .required()
            .rows(4)
            .render("pass\n"),
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
        "forms/key-value/required": (
            "Key-value — required",
            KeyValue.make("meta")
            .label("Metadata")
            .required()
            .render({"owner": "orbit"}),
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
        "forms/repeater/actions": (
            "Repeater — actions",
            Repeater.make("items")
            .label("Line items")
            .schema([TextInput.make("name").label("Name")])
            .add_action_label("Add line item")
            .addable()
            .deletable()
            .cloneable()
            .default_items(1)
            .render([{"name": "Widget"}]),
        ),
        "forms/repeater/grid": (
            "Repeater — grid",
            Repeater.make("items")
            .label("Cards")
            .schema([TextInput.make("name").label("Name")])
            .grid(2)
            .default_items(2)
            .render([{"name": "Alpha"}, {"name": "Beta"}]),
        ),
        "forms/repeater/item-label": (
            "Repeater — item label",
            Repeater.make("items")
            .label("Line items")
            .schema([TextInput.make("name").label("Name")])
            .item_label(lambda index, item, **_: f"{item.get('name') or 'Item'} #{index + 1}")
            .default_items(2)
            .render([{"name": "Widget"}, {"name": "Gadget"}]),
        ),
        "forms/repeater/item-limits": (
            "Repeater — item limits",
            Repeater.make("items")
            .label("Line items")
            .schema([TextInput.make("name").label("Name")])
            .min_items(1)
            .max_items(3)
            .default_items(2)
            .render([{"name": "Widget"}, {"name": "Gadget"}]),
        ),
        "forms/repeater/relationship": (
            "Repeater — relationship",
            Repeater.make("items")
            .label("Order items")
            .relationship("items")
            .schema(
                [
                    TextInput.make("name").label("Name"),
                    TextInput.make("qty").label("Qty"),
                ]
            )
            .default_items(1)
            .render([{"name": "Widget", "qty": "2"}]),
        ),
        "forms/repeater/simple": (
            "Repeater — simple",
            Repeater.make("emails")
            .label("Emails")
            .simple(TextInput.make("email").email().label("Email"))
            .default_items(2)
            .render([{"email": "ada@orbit.test"}, {"email": "grace@orbit.test"}]),
        ),
        # Builder / toggles / morph
        "forms/builder/basic": (
            "Builder — basic",
            Builder.make("content")
            .label("Page blocks")
            .blocks(builder_blocks)
            .block_picker_columns(2)
            .render([{"type": "hero", "heading": "Welcome to Orbit"}]),
        ),
        "forms/builder/block-limits": (
            "Builder — block limits",
            Builder.make("content")
            .label("Page blocks")
            .blocks(
                [
                    Block.make("hero")
                    .label("Hero")
                    .icon("heroicon-o-star")
                    .max_items(1)
                    .schema([TextInput.make("heading").label("Heading")]),
                    Block.make("text")
                    .label("Text")
                    .icon("heroicon-o-document-text")
                    .max_items(3)
                    .schema([Textarea.make("body").label("Body").rows(2)]),
                ]
            )
            .render([{"type": "hero", "heading": "Only one hero"}]),
        ),
        "forms/builder/picker-columns": (
            "Builder — picker columns",
            Builder.make("content")
            .label("Page blocks")
            .blocks(builder_blocks)
            .block_picker_columns(3)
            .render([{"type": "text", "body": "Three-column picker."}]),
        ),
        "forms/builder/reorderable": (
            "Builder — reorderable",
            Builder.make("content")
            .label("Page blocks")
            .blocks(builder_blocks)
            .reorderable()
            .cloneable()
            .render(
                [
                    {"type": "hero", "heading": "First"},
                    {"type": "text", "body": "Second"},
                ]
            ),
        ),
        "forms/toggle-buttons/basic": (
            "Toggle buttons — basic",
            ToggleButtons.make("visibility")
            .label("Visibility")
            .options({"public": "Public", "private": "Private", "draft": "Draft"})
            .render("public"),
        ),
        "forms/toggle-buttons/boolean": (
            "Toggle buttons — boolean",
            ToggleButtons.make("featured").label("Featured").boolean().render(True),
        ),
        "forms/toggle-buttons/enum": (
            "Toggle buttons — enum",
            ToggleButtons.make("visibility").label("Visibility").enum(_Visibility).render("public"),
        ),
        "forms/toggle-buttons/required": (
            "Toggle buttons — required",
            ToggleButtons.make("visibility")
            .label("Visibility")
            .options({"public": "Public", "private": "Private"})
            .required()
            .render("private"),
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
        "forms/morph-to-select/attributes": (
            "Morph-to select — attributes",
            MorphToSelect.make("owner")
            .label("Owner")
            .type_attribute("owner_type")
            .id_attribute("owner_id")
            .types(
                [
                    {"type": "user", "label": "User", "options": {"1": "Ada", "2": "Grace"}},
                    {"type": "team", "label": "Team", "options": {"10": "Engineering"}},
                ]
            )
            .render({"owner_type": "team", "owner_id": "10"}),
        ),
        "forms/morph-to-select/class-strings": (
            "Morph-to select — class strings",
            MorphToSelect.make("assignee")
            .label("Assignee")
            .types(["App\\Models\\User", "App\\Models\\Team"])
            .options({"1": "Ada", "2": "Grace", "10": "Engineering"})
            .render({"type": "App\\Models\\User", "id": "1"}),
        ),
        "forms/morph-to-select/searchable": (
            "Morph-to select — searchable",
            MorphToSelect.make("assignee")
            .label("Assignee")
            .searchable()
            .types(
                [
                    {
                        "type": "user",
                        "label": "User",
                        "options": {"1": "Ada Lovelace", "2": "Grace Hopper"},
                    },
                    {"type": "team", "label": "Team", "options": {"10": "Engineering"}},
                ]
            )
            .render({"type": "user", "id": "2"}),
        ),
        # Multi-select dedicated page
        "forms/multi-select/min-max-items": (
            "Multi-select — min/max items",
            MultiSelect.make("tags")
            .label("Tags")
            .options(tag_opts)
            .min_items(1)
            .max_items(3)
            .render(["orbit", "forms"]),
        ),
        "forms/multi-select/relationship": (
            "Multi-select — relationship",
            MultiSelect.make("categories")
            .label("Categories")
            .relationship("categories", "name")
            .options(tag_opts)
            .searchable()
            .render(["orbit", "tables"]),
        ),
        "forms/multi-select/reorderable": (
            "Multi-select — reorderable",
            MultiSelect.make("tags")
            .label("Tags")
            .options(tag_opts)
            .reorderable()
            .render(["forms", "orbit"]),
        ),
        "forms/multi-select/searchable": (
            "Multi-select — searchable",
            MultiSelect.make("tags")
            .label("Tags")
            .options(tag_opts)
            .searchable()
            .native(False)
            .render(["orbit", "panels"]),
        ),
        # Modal / table select
        "forms/modal-table-select/basic": (
            "Modal table select — basic",
            ModalTableSelect.make("product_id").label("Product").render(),
        ),
        "forms/modal-table-select/disabled-on-view": (
            "Modal table select — disabled on view",
            ModalTableSelect.make("product_id")
            .label("Product")
            .disabled_on("view")
            .render("SKU-42", operation="view"),
        ),
        "forms/modal-table-select/populated": (
            "Modal table select — populated",
            ModalTableSelect.make("product_id").label("Product").render("SKU-42"),
        ),
        "forms/modal-table-select/required": (
            "Modal table select — required",
            ModalTableSelect.make("product_id").label("Product").required().render("SKU-1"),
        ),
        # Relationship repeater
        "forms/relationship-repeater/basic": (
            "Relationship repeater — basic",
            RelationshipRepeater.make("comments")
            .label("Comments")
            .relationship("comments")
            .schema(
                [
                    TextInput.make("author").label("Author"),
                    Textarea.make("body").label("Body").rows(2),
                ]
            )
            .default_items(1)
            .render([{"author": "Ada", "body": "Looks great."}]),
        ),
        "forms/relationship-repeater/mutate": (
            "Relationship repeater — mutate",
            RelationshipRepeater.make("comments")
            .label("Comments")
            .relationship("comments")
            .schema([TextInput.make("body").label("Body")])
            .mutate_relationship_data_before_create(lambda data, **_: {**data, "source": "admin"})
            .mutate_relationship_data_before_save(lambda data, **_: {**data, "edited": True})
            .default_items(1)
            .render([{"body": "Mutated on create/save."}]),
        ),
        "forms/relationship-repeater/mutate-fill": (
            "Relationship repeater — mutate fill",
            RelationshipRepeater.make("comments")
            .label("Comments")
            .relationship("comments")
            .schema([TextInput.make("body").label("Body")])
            .mutate_relationship_data_before_fill(
                lambda data, **_: {**data, "body": f"[filled] {data.get('body', '')}"}
            )
            .default_items(1)
            .render([{"body": "Original"}]),
        ),
        # Misc fields
        "forms/placeholder/basic": (
            "Placeholder — basic",
            Placeholder.make("note")
            .content("This slot is reserved for future fields.")
            .render(),
        ),
        "forms/placeholder/dehydrated": (
            "Placeholder — dehydrated",
            Placeholder.make("note")
            .content("Dehydrated placeholder content.")
            .dehydrated()
            .render(),
        ),
        "forms/placeholder/from-state": (
            "Placeholder — from state",
            Placeholder.make("summary").render("Computed from form state."),
        ),
        "forms/placeholder/visible-on": (
            "Placeholder — visible on",
            Placeholder.make("edit_note")
            .content("Only visible while editing.")
            .visible_on("edit")
            .render(None, operation="edit"),
        ),
        "forms/hidden/basic": (
            "Hidden — note",
            '<p class="or-helper">Hidden fields render as '
            f'{Hidden.make("token").render("orb_secret")}'
            " — not shown in screenshots.</p>",
        ),
        "forms/hidden/from-record": (
            "Hidden — from record",
            '<p class="or-helper">Hidden from record id: '
            f'{Hidden.make("id").default(42).render(42)}'
            "</p>",
        ),
        "forms/hidden/state-path": (
            "Hidden — state path",
            '<p class="or-helper">Nested state path: '
            f'{Hidden.make("token").state_path("meta.token").render("nested-secret")}'
            "</p>",
        ),
        "forms/hidden/validation": (
            "Hidden — validation",
            '<p class="or-helper">Hidden with required rule: '
            f'{Hidden.make("csrf").required().rules("uuid").render("not-a-uuid")}'
            "</p>",
        ),
        "forms/one-time-code-input/basic": (
            "One-time code — basic",
            OneTimeCodeInput.make("code").label("Verification code").render("123456"),
        ),
        "forms/one-time-code-input/mask": (
            "One-time code — mask",
            OneTimeCodeInput.make("code")
            .label("Verification code")
            .mask("999999")
            .render("424242"),
        ),
        "forms/one-time-code-input/required": (
            "One-time code — required",
            OneTimeCodeInput.make("code").label("Verification code").required().render("123456"),
        ),
        "forms/one-time-code-input/trim": (
            "One-time code — trim",
            OneTimeCodeInput.make("code")
            .label("Verification code")
            .trim()
            .render(" 123456 "),
        ),
        "forms/view-field/basic": (
            "View field — basic",
            ViewField.make("summary")
            .label("Summary")
            .content("<p>Published on <strong>18 Sep 2026</strong>.</p>")
            .render(),
        ),
        "forms/view-field/callable": (
            "View field — callable",
            ViewField.make("summary")
            .label("Summary")
            .content(lambda state, **_: f"<p>State is <strong>{state}</strong>.</p>")
            .render("ready"),
        ),
        "forms/view-field/conditional": (
            "View field — conditional",
            ViewField.make("notice")
            .label("Notice")
            .content("<p>Visible on create only.</p>")
            .visible_on("create")
            .render(None, operation="create"),
        ),
        "forms/view-field/dehydrated": (
            "View field — dehydrated",
            ViewField.make("summary")
            .label("Summary")
            .content("<p>Included in dehydrated state.</p>")
            .dehydrated()
            .render(),
        ),
        "forms/slider/basic": (
            "Slider — basic",
            Slider.make("volume").label("Volume").min_value(0).max_value(100).render(65),
        ),
        "forms/slider/live": (
            "Slider — live",
            Slider.make("volume").label("Volume").min_value(0).max_value(100).live().render(40),
        ),
        "forms/slider/pips": (
            "Slider — pips",
            Slider.make("volume")
            .label("Volume")
            .min_value(0)
            .max_value(100)
            .step(25)
            .pips()
            .render(50),
        ),
        "forms/slider/range": (
            "Slider — range",
            Slider.make("budget")
            .label("Budget")
            .min_value(0)
            .max_value(1000)
            .step(50)
            .helper_text("Range bounds via min/max (single thumb).")
            .render(250),
        ),
        # Overview shared Field APIs (Form.make demos)
        "forms/overview/affixes": (
            "Overview — affixes",
            _form(
                TextInput.make("price").label("Price").prefix("$").suffix("USD").numeric(),
                TextInput.make("domain").label("Domain").prefix("https://").suffix(".test"),
                state={"price": "49.99", "domain": "orbit"},
            ),
        ),
        "forms/overview/content-slots": (
            "Overview — content slots",
            _form(
                TextInput.make("title")
                .label("Title")
                .above_label("<span class='or-helper'>Above label</span>")
                .below_content("<span class='or-helper'>Below content</span>")
                .before_content("<span class='or-helper'>Before</span>")
                .after_content("<span class='or-helper'>After</span>"),
                state={"title": "Launch Orbit"},
            ),
        ),
        "forms/overview/defaults": (
            "Overview — defaults",
            _form(
                TextInput.make("locale").label("Locale").default("en"),
                Toggle.make("active").label("Active").default(True),
                state={"locale": "en", "active": True},
            ),
        ),
        "forms/overview/disabled": (
            "Overview — disabled",
            _form(
                TextInput.make("locked").label("Locked").disabled(),
                Select.make("status").label("Status").options(status_opts).disabled(),
                state={"locked": "Cannot edit", "status": "published"},
            ),
        ),
        "forms/overview/hidden-label": (
            "Overview — hidden label",
            _form(
                TextInput.make("search")
                .label("Search")
                .hidden_label()
                .placeholder("Search records…")
                .prefix_icon("heroicon-o-magnifying-glass"),
                state={"search": "orbit"},
            ),
        ),
        "forms/overview/labels": (
            "Overview — labels",
            _form(
                TextInput.make("title").label("Post title"),
                TextInput.make("slug").label("URL slug").helper_text("Derived from the title."),
                state={"title": "Launch Orbit", "slug": "launch-orbit"},
            ),
        ),
        "forms/overview/live": (
            "Overview — live",
            _form(
                TextInput.make("title").label("Title").live(),
                TextInput.make("slug").label("Slug").live(on_blur=True),
                state={"title": "Launch Orbit", "slug": "launch-orbit"},
            ),
        ),
        "forms/overview/operation": (
            "Overview — operation",
            _form(
                TextInput.make("name").label("Name"),
                TextInput.make("created_at")
                .label("Created at")
                .disabled_on("create")
                .visible_on("edit", "view"),
                operation="edit",
                state={"name": "Ada", "created_at": "2026-09-18"},
            ),
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


def _infolist(*components, record: dict | None = None, columns: int | None = None) -> str:
    infolist = Infolist.make().schema(list(components))
    if columns:
        infolist.columns(columns)
    return infolist.render(record or {})


_AVATAR = "https://api.dicebear.com/9.x/shapes/svg?seed=orbit"
_AVATAR_B = "https://api.dicebear.com/9.x/shapes/svg?seed=ada"
_AVATAR_C = "https://api.dicebear.com/9.x/shapes/svg?seed=grace"


def build_infolist_variants() -> dict[str, tuple[str, str]]:
    """Return ``{shot_id: (label, html)}`` for infolist entry shots."""
    sample = {
        "title": "Launch Orbit",
        "slug": "launch-orbit",
        "status": "published",
        "email": "ada@orbit.test",
        "website": "https://orbit.almasix.com",
        "body": "Orbit infolists mirror Filament’s read-only entries for resource view pages.",
        "md": "Ship **badges**, *icons*, and copyable slugs on the show page.",
        "html": "<em>Trusted</em> HTML when you opt in.",
        "bio": "Ada Lovelace wrote the first algorithm intended for a machine. "
        "Her notes on Babbage’s Analytical Engine still inspire engineers.",
        "tags": ["tables", "forms", "infolists"],
        "skills": "Python,SQL,CSS",
        "published_at": "2024-06-15T12:30:00",
        "starts_at": "2000-01-01T00:00:00",
        "price": 1999,
        "qty": 3.5,
        "active": True,
        "featured": False,
        "icon": "heroicon-o-rocket-launch",
        "photo": _AVATAR,
        "photos": [_AVATAR, _AVATAR_B, _AVATAR_C],
        "accent": "#f1511b",
        "payload": {"version": 1, "enabled": True},
        "source": "def greet(name):\n    return f'Hello, {name}!'",
        "meta": {"locale": "en", "timezone": "UTC"},
        "items": [
            {"name": "Tables", "status": "ready"},
            {"name": "Forms", "status": "ready"},
            {"name": "Infolists", "status": "shipping"},
        ],
        "author": {"name": "Ada Lovelace"},
        "notes": None,
    }

    return {
        "infolists/overview": (
            "Infolists overview",
            _infolist(
                TextEntry.make("title").label("Title").weight("bold"),
                TextEntry.make("status").label("Status").badge().color("success"),
                TextEntry.make("slug").label("Slug").copyable(),
                TextEntry.make("author.name").label("Author"),
                ImageEntry.make("photo").label("Cover").circular().size(48),
                columns=2,
                record=sample,
            ),
        ),
        "infolists/overview/labels": (
            "Infolists — labels",
            _infolist(
                TextEntry.make("title")
                .label("Post title")
                .helper_text("Shown on the public page.")
                .hint("Required for SEO")
                .hint_icon("heroicon-m-information-circle"),
                record=sample,
            ),
        ),
        "infolists/overview/helper-hint": (
            "Infolists — helper + hint",
            _infolist(
                TextEntry.make("email")
                .label("Email")
                .helper_text("Used for invoices and notifications.")
                .hint("Primary")
                .hint_icon("heroicon-m-envelope"),
                record=sample,
            ),
        ),
        "infolists/overview/placeholder": (
            "Infolists — placeholder",
            _infolist(
                TextEntry.make("notes").label("Notes").placeholder("No notes yet"),
                record=sample,
            ),
        ),
        "infolists/overview/default": (
            "Infolists — default",
            _infolist(
                TextEntry.make("locale").label("Locale").default("en"),
                record={},
            ),
        ),
        "infolists/overview/copyable": (
            "Infolists — copyable",
            _infolist(
                TextEntry.make("slug")
                .label("Slug")
                .copyable()
                .copy_message("Copied!")
                .copy_message_duration(1500),
                record=sample,
            ),
        ),
        "infolists/overview/format-state": (
            "Infolists — format state",
            _infolist(
                TextEntry.make("email")
                .label("Email")
                .format_state_using(lambda state, **_: str(state or "").upper()),
                record=sample,
            ),
        ),
        "infolists/overview/tooltip": (
            "Infolists — tooltip",
            _infolist(
                TextEntry.make("status")
                .label("Status")
                .badge()
                .color("success")
                .tooltip("Visible on the public site"),
                record=sample,
            ),
        ),
        "infolists/overview/slots": (
            "Infolists — content slots",
            _infolist(
                TextEntry.make("title")
                .label("Title")
                .above_label('<span class="or-muted">Above label</span>')
                .below_content('<span class="or-muted">Below content</span>'),
                record=sample,
            ),
        ),
        "infolists/overview/affix": (
            "Infolists — affix actions",
            _infolist(
                TextEntry.make("slug")
                .label("Slug")
                .prefix_action("edit")
                .suffix_action("copy"),
                record=sample,
            ),
        ),
        "infolists/overview/columns": (
            "Infolists — columns",
            _infolist(
                TextEntry.make("title").label("Title"),
                TextEntry.make("status").label("Status").badge().color("success"),
                TextEntry.make("email").label("Email"),
                TextEntry.make("slug").label("Slug").copyable(),
                columns=2,
                record=sample,
            ),
        ),
        "infolists/text-entry/basic": (
            "Text entry — basic",
            _infolist(TextEntry.make("title").label("Title"), record=sample),
        ),
        "infolists/text-entry/badge": (
            "Text entry — badge",
            _infolist(
                TextEntry.make("status").label("Status").badge().color("success"),
                record=sample,
            ),
        ),
        "infolists/text-entry/color": (
            "Text entry — color",
            _infolist(
                TextEntry.make("status").label("Status").color("info").weight("medium"),
                record=sample,
            ),
        ),
        "infolists/text-entry/icon": (
            "Text entry — icon",
            _infolist(
                TextEntry.make("email")
                .label("Email")
                .icon("heroicon-o-envelope")
                .icon_color("primary"),
                record=sample,
            ),
        ),
        "infolists/text-entry/url": (
            "Text entry — url",
            _infolist(
                TextEntry.make("website")
                .label("Website")
                .url(lambda state, **_: str(state))
                .open_url_in_new_tab()
                .color("primary"),
                record=sample,
            ),
        ),
        "infolists/text-entry/size-weight": (
            "Text entry — size + weight",
            _infolist(
                TextEntry.make("title").label("Title").size("lg").weight("bold"),
                record=sample,
            ),
        ),
        "infolists/text-entry/font-family": (
            "Text entry — font family",
            _infolist(
                TextEntry.make("slug").label("Slug").font_family("monospace"),
                record=sample,
            ),
        ),
        "infolists/text-entry/line-clamp": (
            "Text entry — line clamp",
            _infolist(
                TextEntry.make("bio").label("Bio").line_clamp(2).wrap(),
                record=sample,
            ),
        ),
        "infolists/text-entry/list": (
            "Text entry — list with line breaks",
            _infolist(
                TextEntry.make("tags").label("Tags").list_with_line_breaks(),
                record=sample,
            ),
        ),
        "infolists/text-entry/bulleted": (
            "Text entry — bulleted",
            _infolist(
                TextEntry.make("tags").label("Tags").bulleted(),
                record=sample,
            ),
        ),
        "infolists/text-entry/separator": (
            "Text entry — separator badges",
            _infolist(
                TextEntry.make("skills").label("Skills").separator(",").badge().color("gray"),
                record=sample,
            ),
        ),
        "infolists/text-entry/date": (
            "Text entry — date / time",
            _infolist(
                TextEntry.make("published_at").label("Published").date_time("%b %d, %Y %H:%M"),
                record=sample,
            ),
        ),
        "infolists/text-entry/since": (
            "Text entry — since",
            _infolist(
                TextEntry.make("starts_at").label("Started").since(),
                record=sample,
            ),
        ),
        "infolists/text-entry/money": (
            "Text entry — money",
            _infolist(
                TextEntry.make("price").label("Price").money("USD", divide_by=100),
                record=sample,
            ),
        ),
        "infolists/text-entry/numeric": (
            "Text entry — numeric",
            _infolist(
                TextEntry.make("qty").label("Quantity").numeric(2),
                record=sample,
            ),
        ),
        "infolists/text-entry/markdown": (
            "Text entry — markdown",
            _infolist(
                TextEntry.make("md").label("Summary").markdown(),
                record=sample,
            ),
        ),
        "infolists/text-entry/html": (
            "Text entry — html",
            _infolist(
                TextEntry.make("html").label("HTML").html(),
                record=sample,
            ),
        ),
        "infolists/text-entry/prose": (
            "Text entry — prose",
            _infolist(
                TextEntry.make("body").label("Body").prose().markdown(),
                record=sample,
            ),
        ),
        "infolists/text-entry/limit": (
            "Text entry — limit / words",
            _infolist(
                TextEntry.make("bio").label("Bio").limit(48),
                TextEntry.make("body").label("Body").words(8),
                record=sample,
            ),
        ),
        "infolists/icon-entry/basic": (
            "Icon entry — basic",
            _infolist(
                IconEntry.make("icon").label("Icon").color("primary").size("lg"),
                record=sample,
            ),
        ),
        "infolists/icon-entry/boolean": (
            "Icon entry — boolean",
            _infolist(
                IconEntry.make("active").label("Active").boolean(),
                IconEntry.make("featured")
                .label("Featured")
                .boolean()
                .false_color("gray")
                .false_icon("heroicon-o-minus"),
                record=sample,
            ),
        ),
        "infolists/icon-entry/colors": (
            "Icon entry — colors",
            _infolist(
                IconEntry.make("icon").label("Launch").color("warning").size("md"),
                record=sample,
            ),
        ),
        "infolists/image-entry/basic": (
            "Image entry — basic",
            _infolist(
                ImageEntry.make("photo").label("Cover").width(96).height(96).alt("Cover"),
                record=sample,
            ),
        ),
        "infolists/image-entry/circular": (
            "Image entry — circular",
            _infolist(
                ImageEntry.make("photo").label("Avatar").circular().size(56).alt("Avatar"),
                record=sample,
            ),
        ),
        "infolists/image-entry/stacked": (
            "Image entry — stacked",
            _infolist(
                ImageEntry.make("photos")
                .label("Team")
                .stacked()
                .circular()
                .limit(2)
                .overlap(10)
                .ring(2)
                .size(40),
                record=sample,
            ),
        ),
        "infolists/color-entry/basic": (
            "Color entry — basic",
            _infolist(
                ColorEntry.make("accent").label("Accent"),
                record=sample,
            ),
        ),
        "infolists/color-entry/copyable": (
            "Color entry — copyable",
            _infolist(
                ColorEntry.make("accent").label("Accent").copyable().copy_message("Hex copied"),
                record=sample,
            ),
        ),
        "infolists/code-entry/basic": (
            "Code entry — basic",
            _infolist(
                CodeEntry.make("payload").label("Payload"),
                record=sample,
            ),
        ),
        "infolists/code-entry/grammar": (
            "Code entry — grammar + copy",
            _infolist(
                CodeEntry.make("source").label("Source").grammar("python").copyable(),
                record=sample,
            ),
        ),
        "infolists/key-value-entry/basic": (
            "Key-value entry — basic",
            _infolist(
                KeyValueEntry.make("meta").label("Meta"),
                record=sample,
            ),
        ),
        "infolists/key-value-entry/labels": (
            "Key-value entry — labels",
            _infolist(
                KeyValueEntry.make("meta")
                .label("Meta")
                .key_label("Property")
                .value_label("Content"),
                record=sample,
            ),
        ),
        "infolists/repeatable-entry/basic": (
            "Repeatable entry — basic",
            _infolist(
                RepeatableEntry.make("items")
                .label("Modules")
                .schema(
                    [
                        TextEntry.make("name").label("Name"),
                        TextEntry.make("status").label("Status").badge().color("info"),
                    ]
                ),
                record=sample,
            ),
        ),
        "infolists/repeatable-entry/columns": (
            "Repeatable entry — columns",
            _infolist(
                RepeatableEntry.make("items")
                .label("Modules")
                .columns(2)
                .contained(False)
                .schema(
                    [
                        TextEntry.make("name").label("Name"),
                        TextEntry.make("status").label("Status").badge(),
                    ]
                ),
                record=sample,
            ),
        ),
        "infolists/view-entry/basic": (
            "View entry — basic",
            _infolist(
                ViewEntry.make("summary")
                .label("Summary")
                .content('<strong>3</strong> modules ready'),
                record=sample,
            ),
        ),
        "infolists/view-entry/callable": (
            "View entry — callable",
            _infolist(
                ViewEntry.make("title")
                .label("Headline")
                .content(
                    lambda state=None, **_: f'<span class="or-badge or-color-success">{state}</span>'
                ),
                record=sample,
            ),
        ),
    }


def _action_row(*actions: Action, record: dict | None = None) -> str:
    ctx: dict = {"record": record} if record is not None else {}
    inner = "".join(a.render(**ctx) for a in actions)
    return f'<div class="or-btn-group" style="display:flex;flex-wrap:wrap;gap:0.5rem;align-items:center">{inner}</div>'


def _static_modal(
    *,
    heading: str,
    description: str = "",
    form_html: str = "",
    submit: str = "Confirm",
    cancel: str = "Cancel",
    slide_over: bool = False,
    modal_icon: str = "",
    modal_icon_color: str = "primary",
    alignment: str = "start",
    width: str = "md",
) -> str:
    """Static modal preview for gallery shots (no Alpine host)."""
    from almasix.orbit.support.icons import icon as render_icon

    classes = ["or-modal", f"or-modal-{width}"]
    if slide_over:
        classes.append("or-modal-slide")
    if alignment == "center":
        classes.append("or-modal-align-center")
    icon_html = ""
    if modal_icon:
        icon_html = (
            f'<div class="or-modal-icon" data-color="{modal_icon_color}">'
            f"{render_icon(modal_icon)}</div>"
        )
    desc = f'<p class="or-modal-body">{description}</p>' if description else ""
    form = (
        f'<form class="or-modal-form"><div class="or-modal-form-fields">{form_html}</div></form>'
        if form_html
        else ""
    )
    return (
        '<div class="or-gallery-modal">'
        f'<div class="{" ".join(classes)}" role="dialog" aria-modal="true" style="position:relative;left:auto;top:auto;transform:none;display:block !important;">'
        '<button type="button" class="or-modal-close" aria-label="Close">&times;</button>'
        f'<div class="or-modal-header">{icon_html}<h2 class="or-modal-title">{heading}</h2></div>'
        f"{desc}{form}"
        '<div class="or-modal-actions">'
        f'<button type="button" class="or-btn or-btn-gray">{cancel}</button>'
        f'<button type="button" class="or-btn or-btn-primary">{submit}</button>'
        "</div></div></div>"
    )


def _open_dropdown(html: str) -> str:
    """Force ActionGroup dropdown open for static screenshots."""
    return (
        html.replace(' x-show="menuOpen" x-cloak', "")
        .replace('x-show="menuOpen"', "")
        .replace('x-cloak', "")
    )


def build_action_variants() -> dict[str, tuple[str, str]]:
    """Return ``{shot_id: (label, html)}`` for action chrome / preset shots."""
    record = {"id": 1, "title": "Launch Orbit", "status": "draft", "note": "Ship actions"}

    return {
        "actions/overview": (
            "Actions overview",
            _action_row(
                CreateAction.make(),
                EditAction.make().url("/edit/1"),
                ViewAction.make().url("/view/1"),
                DeleteAction.make(),
                record=record,
            ),
        ),
        "actions/overview/triggers": (
            "Actions — trigger styles",
            _action_row(
                Action.make("save").label("Save").color("primary").button(),
                Action.make("docs").label("Docs").link().url("https://orbit.almasix.com"),
                Action.make("settings")
                .label("Settings")
                .icon("heroicon-o-cog-6-tooth")
                .icon_button()
                .color("gray"),
                Action.make("inbox").label("Inbox").badge().color("primary"),
            ),
        ),
        "actions/overview/sizes": (
            "Actions — sizes",
            _action_row(
                Action.make("sm").label("Small").size("sm").color("primary"),
                Action.make("md").label("Medium").size("md").color("primary"),
                Action.make("lg").label("Large").size("lg").color("primary"),
            ),
        ),
        "actions/overview/outlined": (
            "Actions — outlined",
            _action_row(
                Action.make("a").label("Primary").color("primary").outlined(),
                Action.make("b").label("Danger").color("danger").outlined().without_confirmation(),
                Action.make("c").label("Gray").color("gray").outlined(),
            ),
        ),
        "actions/overview/icons": (
            "Actions — icons",
            _action_row(
                Action.make("before")
                .label("Before")
                .icon("heroicon-o-check")
                .icon_position("before")
                .color("success"),
                Action.make("after")
                .label("After")
                .icon("heroicon-o-chevron-right")
                .icon_position("after")
                .color("primary"),
            ),
        ),
        "actions/overview/tooltip": (
            "Actions — tooltip",
            _action_row(
                Action.make("tip")
                .label("Publish")
                .icon("heroicon-o-check")
                .tooltip("Publish this draft to production")
                .color("primary"),
            ),
        ),
        "actions/overview/badge": (
            "Actions — badge indicator",
            _action_row(
                Action.make("inbox")
                .label("Inbox")
                .icon("heroicon-o-bell")
                .badge(3)
                .badge_color("danger")
                .color("gray"),
            ),
        ),
        "actions/overview/url": (
            "Actions — URL + new tab",
            _action_row(
                Action.make("site")
                .label("Open site")
                .icon("heroicon-o-document-text")
                .url("https://orbit.almasix.com", open_in_new_tab=True)
                .color("gray"),
            ),
        ),
        "actions/overview/authorize": (
            "Actions — authorize (disabled)",
            _action_row(
                Action.make("admin")
                .label("Admin only")
                .icon("heroicon-o-x-mark")
                .authorize(False)
                .authorization_tooltip("You need admin access")
                .color("danger")
                .without_confirmation(),
            ),
        ),
        "actions/overview/schema": (
            "Actions — schema / form trigger",
            _action_row(
                Action.make("note")
                .label("Add note")
                .icon("heroicon-o-pencil-square")
                .modal()
                .modal_heading("Changelog note")
                .form([TextInput.make("note").label("Note")])
                .color("primary"),
            ),
        ),
        "actions/overview/notifications": (
            "Actions — notifications",
            _action_row(
                Action.make("save")
                .label("Save")
                .icon("heroicon-o-check")
                .success_notification("Saved")
                .success_notification_title("Success")
                .color("primary"),
            ),
        ),
        "actions/modals/confirm": (
            "Modals — confirmation",
            _static_modal(
                heading="Delete?",
                description="This permanently removes the record.",
                submit="Delete",
                cancel="Cancel",
                modal_icon="heroicon-o-trash",
                modal_icon_color="danger",
            ),
        ),
        "actions/modals/form": (
            "Modals — form",
            _static_modal(
                heading="Edit post",
                description="Update the title and status.",
                form_html=TextInput.make("title").label("Title").render("Launch Orbit")
                + Select.make("status")
                .label("Status")
                .options({"draft": "Draft", "published": "Published"})
                .render("draft"),
                submit="Save",
                cancel="Cancel",
            ),
        ),
        "actions/modals/slide-over": (
            "Modals — slide over",
            _static_modal(
                heading="Quick edit",
                description="Slide-over panel from the right.",
                form_html=TextInput.make("title").label("Title").render("Launch Orbit"),
                submit="Save",
                slide_over=True,
                width="md",
            ),
        ),
        "actions/modals/labels": (
            "Modals — custom labels",
            _static_modal(
                heading="Archive post?",
                description="Move this post to the archive.",
                submit="Archive",
                cancel="Keep editing",
            ),
        ),
        "actions/modals/icon": (
            "Modals — icon + alignment",
            _static_modal(
                heading="Publish?",
                description="Make this draft live on the public site.",
                submit="Publish",
                modal_icon="heroicon-o-check",
                modal_icon_color="success",
                alignment="center",
            ),
        ),
        "actions/grouping/dropdown": (
            "Grouping — dropdown",
            _open_dropdown(
                ActionGroup.make(
                    [
                        EditAction.make().url("/edit/1"),
                        ViewAction.make().url("/view/1"),
                        DeleteAction.make(),
                    ]
                )
                .label("Actions")
                .icon("heroicon-o-ellipsis-vertical")
                .render(record=record)
            ),
        ),
        "actions/grouping/button-group": (
            "Grouping — button group",
            ActionGroup.make(
                [
                    EditAction.make().url("/edit/1"),
                    ViewAction.make().url("/view/1"),
                    DeleteAction.make(),
                ]
            )
            .button_group()
            .render(record=record),
        ),
        "actions/grouping/sections": (
            "Grouping — sections",
            ActionGroup.make(
                [
                    ActionGroup.make(
                        [
                            EditAction.make().url("/edit/1"),
                            ViewAction.make().url("/view/1"),
                        ]
                    )
                    .label("Record")
                    .dropdown(False),
                    ActionGroup.make([DeleteAction.make(), ForceDeleteAction.make()])
                    .label("Danger zone")
                    .dropdown(False),
                ]
            )
            .button_group()
            .render(record=record),
        ),
        "actions/create": (
            "Create action",
            _action_row(CreateAction.make().create_another()),
        ),
        "actions/edit": (
            "Edit action",
            _action_row(EditAction.make().url("/edit/1"), record=record),
        ),
        "actions/view": (
            "View action",
            _action_row(ViewAction.make().url("/view/1"), record=record),
        ),
        "actions/delete": (
            "Delete action",
            _action_row(DeleteAction.make(), record=record),
        ),
        "actions/replicate": (
            "Replicate action",
            _action_row(ReplicateAction.make(), record=record),
        ),
        "actions/force-delete": (
            "Force-delete action",
            _action_row(ForceDeleteAction.make(), record=record),
        ),
        "actions/restore": (
            "Restore action",
            _action_row(RestoreAction.make(), record=record),
        ),
        "actions/import": (
            "Import action",
            _action_row(
                ImportAction.make()
                .accepted_file_types([".csv", ".json"])
                .options_form([TextInput.make("delimiter").label("Delimiter").default(",")])
            ),
        ),
        "actions/export": (
            "Export action",
            _action_row(
                ExportAction.make()
                .formats(["csv", "json"])
                .filename("posts-export")
                .columns(["title", "status"])
            ),
        ),
    }
