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
from almasix.orbit.tables import BadgeColumn, Table, TextColumn
from almasix.orbit.widgets import (
    ChartLibrary,
    ChartWidget,
    Stat,
    StatsOverviewWidget,
    TableWidget,
    Widget,
)
from almasix.orbit.notifications import (
    Alignment,
    Notification,
    NotificationAction,
    Notifications,
    VerticalAlignment,
)
from almasix.orbit.panels.cluster import Cluster
from almasix.orbit.panels.navigation import (
    NavigationGroup,
    NavigationItem,
    NavigationSubgroup,
    normalize_nav_layout,
)
from almasix.orbit.panels.page import Page
from almasix.orbit.panels.pages.dashboard import Dashboard
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.relation_manager import RelationManager
from almasix.orbit.panels.resource import Resource
from almasix.orbit.panels.tenancy import Tenancy, Tenant
from almasix.orbit.panels.users import OrbitUser, PanelNotification, UserMenuItem


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
        "forms/file-upload/stored-files": (
            "File upload — stored files",
            FileUpload.make("gallery")
            .label("Gallery")
            .image()
            .multiple()
            .openable()
            .downloadable()
            .upload_url("/admin/orbit-upload")
            .render(
                [
                    {
                        "path": "post-covers/launch.png",
                        "url": (
                            "data:image/svg+xml;utf8,"
                            "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 120'>"
                            "<rect width='120' height='120' fill='%236366f1'/>"
                            "<circle cx='60' cy='48' r='22' fill='%23c7d2fe'/>"
                            "<path d='M12 108 L48 64 L78 100 L96 82 L120 108 Z' fill='%234338ca'/>"
                            "</svg>"
                        ),
                        "name": "launch.png",
                    },
                    {"path": "post-covers/press-kit.pdf", "name": "press-kit.pdf"},
                ]
            ),
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
        "forms/rich-editor/merge-tags": (
            "Rich editor — merge tags",
            RichEditor.make("message")
            .label("Message")
            .toolbar_buttons(["bold", "italic", "h2", "bulletList", "link"])
            .merge_tags(["customer_name", "invoice_total"])
            .placeholder("Write the message…")
            .min_height("12rem")
            .render(""),
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
        "forms/key-value/editing": (
            "Key-value — editing rows",
            KeyValue.make("meta")
            .label("Metadata")
            .key_label("Attribute")
            .value_label("Value")
            .key_placeholder("e.g. reading_time")
            .value_placeholder("e.g. 4 min")
            .add_action_label("Add attribute")
            .render({"reading_time": "4 min", "audience": "developers"}),
        ),
        "forms/key-value/locked-keys": (
            "Key-value — locked keys",
            KeyValue.make("limits")
            .label("Plan limits")
            .editable_keys(False)
            .addable(False)
            .deletable(False)
            .render({"seats": "25", "projects": "10"}),
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
        "forms/morph-to-select/live-search": (
            "Morph-to select — live search",
            MorphToSelect.make("assignee")
            .label("Assignee")
            .searchable()
            .types([{"type": "user", "label": "User"}, {"type": "team", "label": "Team"}])
            .options_using(
                lambda type="", search="": (
                    {"1": "Ada Lovelace", "2": "Grace Hopper"} if type == "user" else {}
                )
            )
            .render({"type": "user", "id": "2"}, morph_search={"assignee": "hopper"}),
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
        "forms/modal-table-select/picker": (
            "Modal table select — picker open",
            ModalTableSelect.make("author_id")
            .label("Author")
            .modal_heading("Pick an author")
            .browse_label("Browse authors")
            .title_attribute("name")
            .records(
                [
                    {"id": "1", "name": "Ada Lovelace"},
                    {"id": "2", "name": "Grace Hopper"},
                    {"id": "3", "name": "Katherine Johnson"},
                ]
            )
            .render(None, table_select={"field": "author_id", "search": ""}),
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
        "forms/overview/inline-label": (
            "Overview — inline label",
            _form(
                TextInput.make("timezone").label("Timezone").inline_label().placeholder("UTC"),
                Toggle.make("marketing_emails").label("Marketing emails").inline_label(),
                state={"timezone": "America/New_York", "marketing_emails": True},
            ),
        ),
        "forms/overview/placeholder": (
            "Overview — placeholder",
            _form(
                TextInput.make("email")
                .label("Email")
                .email()
                .placeholder("you@acme.test")
                .helper_text("We never share this address."),
                state={},
            ),
        ),
        "forms/overview/autofocus": (
            "Overview — autofocus",
            _form(
                TextInput.make("title").label("Title").autofocus().required(),
                Textarea.make("body").label("Body").rows(4),
                state={"title": "", "body": ""},
            ),
        ),
        "forms/overview/extra-attributes": (
            "Overview — extra attributes",
            _form(
                TextInput.make("title")
                .label("Title")
                .extra_input_attributes({"data-testid": "post-title", "spellcheck": "true"})
                .extra_field_wrapper_attributes({"data-tour": "title-field"}),
                state={"title": "Launch Orbit"},
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
        "body": "Orbit infolists turn one record into a stacked detail sheet — labels above values, badges, and copyable slugs.",
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
        "subtitle": "Admin panels for Python teams",
        "timezone": "UTC",
        "locale": "en-US",
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
        "infolists/overview/hidden-label": (
            "Infolists — hidden label",
            _infolist(
                TextEntry.make("title").hidden_label().weight("bold").size("lg"),
                TextEntry.make("subtitle").hidden_label().color("gray"),
                record=sample,
            ),
        ),
        "infolists/overview/inline-label": (
            "Infolists — inline label",
            _infolist(
                TextEntry.make("timezone").label("Timezone").inline_label(),
                TextEntry.make("locale").label("Locale").inline_label().default("en"),
                TextEntry.make("email").label("Email").inline_label(),
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
                TextEntry.make("full_name")
                .label("Full name")
                .state(
                    lambda record, **_: f"{record.get('author', {}).get('name', 'Unknown')}"
                ),
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
        "infolists/overview/extra-attributes": (
            "Infolists — extra attributes",
            _infolist(
                TextEntry.make("title")
                .label("Title")
                .weight("bold")
                .extra_attributes({"data-tour": "title"})
                .extra_entry_wrapper_attributes({"data-qa": "post-title"}),
                TextEntry.make("slug")
                .label("Slug")
                .copyable()
                .extra_entry_wrapper_attributes({"data-qa": "post-slug"}),
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
        "infolists/overview/sections": (
            "Infolists — sections",
            _infolist(
                Section.make("basics")
                .heading("Basics")
                .description("Core fields for this post.")
                .schema(
                    [
                        TextEntry.make("title").label("Title").weight("bold"),
                        TextEntry.make("status").label("Status").badge().color("success"),
                        TextEntry.make("slug").label("Slug").copyable(),
                    ]
                ),
                Section.make("author")
                .heading("Author")
                .schema(
                    [
                        TextEntry.make("author.name").label("Name"),
                        TextEntry.make("email").label("Email"),
                        ImageEntry.make("photo").label("Avatar").circular().size(40),
                    ]
                ),
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


def _dashboard(*widgets: Widget | type[Widget], columns: int = 2) -> str:
    return Dashboard.render(
        widgets=list(widgets),
        columns=columns,
        brand="Orbit",
    )


def build_widget_variants() -> dict[str, tuple[str, str]]:
    """Return ``{shot_id: (label, html)}`` for widget + dashboard shots."""
    stats = (
        StatsOverviewWidget.make("overview")
        .heading("Overview")
        .stats(
            [
                Stat.make("Users")
                .value(1280)
                .description("+4% this week")
                .description_icon("heroicon-m-arrow-trending-up")
                .color("success")
                .icon("heroicon-o-users")
                .chart([820, 932, 901, 1034, 1190, 1280]),
                Stat.make("Posts")
                .value(342)
                .color("primary")
                .icon("heroicon-o-document-text")
                .chart([210, 240, 280, 310, 330, 342]),
                Stat.make("Revenue")
                .value("$12.4k")
                .color("warning")
                .icon("heroicon-o-banknotes")
                .chart([8.1, 9.2, 9.8, 10.4, 11.2, 12.4]),
            ]
        )
    )
    chart_js = (
        ChartWidget.make("signups")
        .heading("Signups")
        .description("Last 7 days")
        .chart_library(ChartLibrary.CHARTJS)
        .chart_type("line")
        .labels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        .datasets([{"label": "Users", "data": [12, 19, 14, 22, 18, 25, 30]}])
        .color("primary")
        .max_height("240px")
    )
    chart_apex = (
        ChartWidget.make("revenue")
        .heading("Revenue")
        .chart_library(ChartLibrary.APEX)
        .chart_type("area")
        .labels(["Jan", "Feb", "Mar", "Apr", "May", "Jun"])
        .datasets([{"label": "MRR", "data": [12, 15, 14, 18, 22, 26]}])
        .color("success")
        .max_height("240px")
    )
    table_widget = (
        TableWidget.make("recent")
        .heading("Recent posts")
        .description("Latest drafts and publications")
        .column_span("full")
        .table(
            Table.make()
            .columns(
                [
                    TextColumn.make("title").label("Title"),
                    BadgeColumn.make("status").label("Status"),
                ]
            )
            .records(
                [
                    {"title": "Launch Orbit", "status": "published"},
                    {"title": "Conduit hosts", "status": "draft"},
                    {"title": "Widget polish", "status": "published"},
                ]
            )
            .paginated(False)
        )
    )
    custom_cls_body = '<p class="or-muted">Hello from Orbit Admin.</p>'

    class _Welcome(Widget):
        def render_body(self, state=None, **ctx):  # type: ignore[no-untyped-def]
            return custom_cls_body

    custom = _Welcome.make("welcome").heading("Welcome").description("Custom widget body")

    return {
        "widgets/overview": (
            "Widgets overview",
            _dashboard(stats, chart_js, chart_apex, table_widget, columns=2),
        ),
        "widgets/overview/heading": (
            "Widgets — heading",
            Widget.make("notes")
            .heading("Release notes")
            .description("Latest shipping updates for the team.")
            .render(),
        ),
        "widgets/overview/sort": (
            "Widgets — sort",
            _dashboard(
                ChartWidget.make("later")
                .heading("Sort 20")
                .sort(20)
                .labels(["A", "B"])
                .datasets([{"label": "N", "data": [1, 2]}])
                .max_height("160px"),
                ChartWidget.make("earlier")
                .heading("Sort 5")
                .sort(5)
                .labels(["A", "B"])
                .datasets([{"label": "N", "data": [2, 1]}])
                .max_height("160px"),
            ),
        ),
        "widgets/overview/column-span": (
            "Widgets — column span",
            _dashboard(
                ChartWidget.make("wide")
                .heading("Full width")
                .column_span_full()
                .labels(["Mon", "Tue", "Wed"])
                .datasets([{"label": "Hits", "data": [4, 6, 5]}])
                .max_height("180px"),
                columns=2,
            ),
        ),
        "widgets/overview/visibility": (
            "Widgets — visibility",
            _dashboard(
                Widget.make("shown").heading("Visible").can_view_when(True),
                Widget.make("hidden").heading("Hidden").can_view_when(False),
            ),
        ),
        "widgets/overview/custom": (
            "Widgets — custom",
            custom.render(),
        ),
        "widgets/stats-overview": (
            "Stats overview",
            stats.render(),
        ),
        "widgets/stats-overview/value": (
            "Stats — value",
            StatsOverviewWidget.make("v")
            .stats(
                [
                    Stat.make("Open tickets").value(12),
                    Stat.make("Queued jobs").placeholder("—"),
                ]
            )
            .render(),
        ),
        "widgets/stats-overview/description": (
            "Stats — description",
            Stat.make("Signups")
            .value(86)
            .description("vs last week")
            .description_icon("heroicon-m-arrow-trending-up")
            .icon("heroicon-o-user-plus")
            .color("success")
            .render(),
        ),
        "widgets/stats-overview/colors": (
            "Stats — colors",
            StatsOverviewWidget.make("c")
            .stats(
                [
                    Stat.make("Healthy").value("OK").color("success"),
                    Stat.make("Attention").value(3).color("warning"),
                    Stat.make("Failed").value(1).color("danger"),
                ]
            )
            .render(),
        ),
        "widgets/stats-overview/chart": (
            "Stats — sparklines",
            StatsOverviewWidget.make("trends")
            .stats(
                [
                    Stat.make("Users")
                    .value(1280)
                    .color("success")
                    .chart([820, 932, 901, 1034, 1190, 1280]),
                    Stat.make("Sessions")
                    .value("4.2k")
                    .color("primary")
                    .chart([2.1, 2.4, 2.8, 3.1, 3.6, 4.2]),
                ]
            )
            .render(),
        ),
        "widgets/stats-overview/url": (
            "Stats — URL",
            Stat.make("Users")
            .value(1280)
            .url("#users")
            .icon("heroicon-o-users")
            .color("primary")
            .render(),
        ),
        "widgets/charts": (
            "Charts — Chart.js",
            chart_js.render(),
        ),
        "widgets/charts/libraries": (
            "Charts — libraries",
            _dashboard(
                ChartWidget.make("js")
                .heading("Chart.js")
                .chart_library(ChartLibrary.CHARTJS)
                .chart_type("bar")
                .labels(["A", "B", "C"])
                .datasets([{"label": "Series", "data": [3, 7, 4]}])
                .max_height("200px"),
                ChartWidget.make("apex")
                .heading("ApexCharts")
                .chart_library(ChartLibrary.APEX)
                .chart_type("area")
                .labels(["A", "B", "C"])
                .datasets([{"label": "Series", "data": [3, 7, 4]}])
                .max_height("200px"),
            ),
        ),
        "widgets/charts/types": (
            "Charts — types",
            _dashboard(
                ChartWidget.make("bars")
                .heading("By channel")
                .chart_type("bar")
                .labels(["Organic", "Ads", "Referral"])
                .datasets([{"label": "Visits", "data": [40, 28, 17]}])
                .max_height("200px"),
                ChartWidget.make("share")
                .heading("Share")
                .chart_type("doughnut")
                .labels(["Pro", "Free", "Trial"])
                .datasets([{"data": [55, 30, 15]}])
                .max_height("200px"),
            ),
        ),
        "widgets/charts/datasets": (
            "Charts — datasets",
            ChartWidget.make("multi")
            .heading("Revenue vs costs")
            .chart_type("line")
            .labels(["Jan", "Feb", "Mar", "Apr"])
            .datasets(
                [
                    {"label": "Revenue", "data": [12, 19, 14, 22]},
                    {"label": "Costs", "data": [8, 11, 9, 13]},
                ]
            )
            .max_height("220px")
            .render(),
        ),
        "widgets/charts/chrome": (
            "Charts — chrome",
            ChartWidget.make("compact")
            .heading("Compact")
            .color("success")
            .max_height("200px")
            .labels(["Mon", "Tue", "Wed"])
            .datasets([{"label": "Hits", "data": [4, 6, 5]}])
            .render(),
        ),
        "widgets/charts/filters": (
            "Charts — filters",
            ChartWidget.make("range")
            .heading("Traffic")
            .filters({"7d": "7 days", "30d": "30 days", "90d": "90 days"})
            .filter("7d")
            .labels(["Mon", "Tue", "Wed"])
            .datasets([{"label": "Views", "data": [10, 14, 12]}])
            .max_height("200px")
            .render(),
        ),
        "widgets/charts/empty": (
            "Charts — empty",
            ChartWidget.make("empty")
            .heading("Conversions")
            .empty_state_heading("No data yet")
            .empty_state_description("Publish a campaign to see conversion trends.")
            .render(),
        ),
        "widgets/tables": (
            "Table widget",
            table_widget.render(),
        ),
        "widgets/tables/basic": (
            "Table widget — basic",
            TableWidget.make("queue")
            .heading("Job queue")
            .table(
                Table.make()
                .heading("Pending jobs")
                .columns(
                    [
                        TextColumn.make("name"),
                        TextColumn.make("attempts"),
                    ]
                )
                .records(
                    [
                        {"name": "SendNewsletter", "attempts": 0},
                        {"name": "RebuildSearch", "attempts": 1},
                    ]
                )
                .paginated(False)
            )
            .render(),
        ),
        "widgets/tables/full-span": (
            "Table widget — full span",
            _dashboard(
                TableWidget.make("activity")
                .heading("Activity")
                .column_span_full()
                .table(
                    Table.make()
                    .columns([TextColumn.make("event"), TextColumn.make("at")])
                    .records(
                        [
                            {"event": "User signed up", "at": "09:14"},
                            {"event": "Post published", "at": "10:02"},
                        ]
                    )
                    .paginated(False)
                ),
            ),
        ),
        "widgets/tables/empty": (
            "Table widget — empty",
            TableWidget.make("empty")
            .heading("Mentions")
            .table(
                Table.make()
                .columns([TextColumn.make("author"), TextColumn.make("body")])
                .records([])
                .paginated(False)
            )
            .render(),
        ),
        "panels/dashboard": (
            "Dashboard",
            _dashboard(stats, chart_js, chart_apex, table_widget, columns=2),
        ),
        "panels/dashboard/widgets": (
            "Dashboard — widgets",
            _dashboard(stats, chart_js, columns=2),
        ),
        "panels/dashboard/columns": (
            "Dashboard — columns",
            _dashboard(stats, chart_js, chart_apex, columns=3),
        ),
        "panels/dashboard/filters": (
            "Dashboard — filters",
            (
                '<div class="or-page or-page-dashboard">'
                '<div class="or-dashboard-heading">'
                '<h1 class="or-page-title">Dashboard</h1></div>'
                '<div class="or-dashboard-filters">'
                '<label class="or-field"><span class="or-label">Range</span>'
                '<select class="or-input"><option>7 days</option>'
                "<option>30 days</option></select></label></div>"
                f'{stats.render()}'
                "</div>"
            ),
        ),
        "panels/dashboard/route-path": (
            "Dashboard — route path",
            Dashboard.render(
                widgets=[
                    ChartWidget.make("analytics")
                    .heading("Analytics")
                    .labels(["W1", "W2", "W3", "W4"])
                    .datasets([{"label": "Sessions", "data": [120, 140, 160, 190]}])
                    .max_height("220px")
                ],
                columns=1,
                brand="Orbit",
            ).replace(
                '<h1 class="or-page-title">Dashboard</h1>',
                '<h1 class="or-page-title">Analytics</h1>',
                1,
            ),
        ),
    }


# --- Navigation gallery helpers -------------------------------------------------


class _GalleryPostResource(Resource):
    slug = "posts"
    navigation_label = "Posts"
    navigation_icon = "heroicon-o-document-text"
    navigation_group = "Content"
    navigation_sort = 10
    navigation_subgroup = "Writing"

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")])

    @classmethod
    def get_records(cls):
        return [{"id": 1, "title": "Hello"}]


class _GalleryPageResource(Resource):
    slug = "pages"
    navigation_label = "Pages"
    navigation_icon = "heroicon-o-document"
    navigation_group = "Content"
    navigation_sort = 20
    navigation_subgroup = "Writing"

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")])

    @classmethod
    def get_records(cls):
        return []


class _GalleryInboxResource(Resource):
    slug = "inbox"
    navigation_label = "Inbox"
    navigation_icon = "heroicon-o-inbox"
    active_navigation_icon = "heroicon-s-inbox"
    navigation_group = "Content"
    navigation_sort = 5
    navigation_badge = "3"
    navigation_badge_color = "danger"
    navigation_badge_tooltip = "Unread"

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")])

    @classmethod
    def get_records(cls):
        return []


class _GalleryAuthorResource(Resource):
    slug = "authors"
    navigation_label = "Authors"
    navigation_icon = "heroicon-o-users"
    navigation_group = "People"
    navigation_sort = 10

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("name")])

    @classmethod
    def get_records(cls):
        return []


class _GallerySettingsPage(Page):
    slug = "settings"
    navigation_label = "Settings"
    navigation_icon = "heroicon-o-cog-6-tooth"
    navigation_group = "System"
    navigation_sort = 10


class _GalleryPreferencesPage(Page):
    slug = "preferences"
    navigation_label = "Preferences"
    navigation_group = "System"
    navigation_parent_item = "Settings"
    navigation_sort = 11


class _GalleryReportsPage(Page):
    slug = "reports"
    title = "Reports"
    navigation_label = "Reports"
    navigation_icon = "heroicon-o-chart-bar"
    navigation_group = "Content"
    navigation_subgroup = "Insights"
    navigation_sort = 40
    navigation_badge = "Live"
    navigation_badge_color = "success"


class _GallerySettingsCluster(Cluster):
    navigation_icon = "heroicon-o-cog-6-tooth"
    navigation_label = "Settings Hub"
    navigation_group = "Platform"
    navigation_sort = 5
    slug = "settings"
    sub_navigation_position = "start"
    cluster_breadcrumb = "Settings"


class _GalleryColorResource(Resource):
    slug = "colors"
    navigation_label = "Colors"
    navigation_icon = "heroicon-o-swatch"
    cluster = _GallerySettingsCluster
    navigation_sort = 1

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("name")])

    @classmethod
    def get_records(cls):
        return [{"id": 1, "name": "Primary"}]


class _GalleryFontResource(Resource):
    slug = "fonts"
    navigation_label = "Fonts"
    navigation_icon = "heroicon-o-language"
    cluster = _GallerySettingsCluster
    navigation_sort = 2

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("name")])

    @classmethod
    def get_records(cls):
        return []


def _nav_placeholder(title: str = "Posts") -> str:
    return (
        f'<div class="or-page"><h1 class="or-page-title">{title}</h1>'
        '<p class="or-muted">Navigation gallery content.</p></div>'
    )


def _nav_shell(
    panel: Panel,
    content: str | None = None,
    *,
    active_path: str | None = None,
    user: OrbitUser | None = None,
) -> str:
    """Panel chrome fragment for navigation screenshots (no full HTML document)."""
    layout = normalize_nav_layout(panel._navigation_layout)
    ctx = panel.menu_layout_context(active_path=active_path, user=user)
    show_sidebar = panel._navigation_enabled and layout != "top"
    show_topbar = panel._topbar_enabled
    sidebar = (
        panel._render_sidebar(ctx, panel._sidebar_collapsible, user=user) if show_sidebar else ""
    )
    topbar = (
        panel._render_topbar(ctx, user=user, collapsible=panel._sidebar_collapsible)
        if show_topbar
        else ""
    )
    if (
        user is not None
        and panel._user_menu_enabled
        and show_sidebar
        and (panel._user_menu_position == "sidebar" or not show_topbar)
    ):
        sidebar = sidebar.replace(
            "</aside>",
            f'{panel._render_user_menu(user=user, placement="sidebar")}</aside>',
            1,
        )
    cluster, cluster_items = panel.collect_cluster_sub_navigation(active_path, user=user)
    cluster_nav = panel._render_cluster_sub_nav(cluster, cluster_items)
    breadcrumbs = panel._render_breadcrumbs(active_path)
    body = content if content is not None else _nav_placeholder()
    if cluster_nav:
        position = getattr(cluster, "sub_navigation_position", "start")
        if position == "top":
            body = (
                '<div class="or-cluster-layout or-cluster-layout-top">'
                f"{cluster_nav}<div class=\"or-cluster-body\">{body}</div></div>"
            )
        elif position == "end":
            body = (
                '<div class="or-cluster-layout or-cluster-layout-end">'
                f'<div class="or-cluster-body">{body}</div>{cluster_nav}</div>'
            )
        else:
            body = (
                '<div class="or-cluster-layout or-cluster-layout-start">'
                f"{cluster_nav}<div class=\"or-cluster-body\">{body}</div></div>"
            )
    app_class = "or-app or-shot-shell"
    if layout == "sidebar_topbar":
        app_class += " or-app-split or-app-apps"
    elif layout == "top":
        app_class += " or-app-top"
    elif layout == "sidebar":
        app_class += " or-app-sidebar"
    if not show_sidebar:
        app_class += " or-app-no-sidebar"
    return (
        f'<div class="{app_class}" x-data="{{ sidebarOpen: true, collapsed: false }}">'
        f"{sidebar}"
        f'<div class="or-main">{topbar}{breadcrumbs}'
        f'<main class="or-content">{body}</main></div></div>'
    )


def _nav_demo_panel(*, layout: str = "apps") -> Panel:
    return (
        Panel.make("admin")
        .path("admin")
        .brand_name("Orbit")
        .navigation_layout(layout)  # type: ignore[arg-type]
        .sidebar_collapsible()
        .dashboard(False)
        .navigation_groups(
            [
                NavigationGroup.make("Content")
                .icon("heroicon-o-document-text")
                .sort(10),
                NavigationGroup.make("People").icon("heroicon-o-users").sort(20),
                NavigationGroup.make("System")
                .icon("heroicon-o-cog-6-tooth")
                .sort(30),
                NavigationGroup.make("Platform")
                .icon("heroicon-o-squares-2x2")
                .sort(40),
            ]
        )
        .navigation_subgroups(
            [
                NavigationSubgroup.make("Writing")
                .parent("Content")
                .icon("heroicon-o-pencil-square")
                .sort(5),
                NavigationSubgroup.make("Insights")
                .parent("Content")
                .icon("heroicon-o-chart-bar")
                .sort(10),
            ]
        )
        .navigation_items(
            [
                NavigationItem.make("docs")
                .label("Docs")
                .url("https://orbit.almasix.com")
                .icon("heroicon-o-book-open")
                .group("Content")
                .sort(100)
                .open_url_in_new_tab(),
            ]
        )
        .resources(
            [
                _GalleryInboxResource,
                _GalleryPostResource,
                _GalleryPageResource,
                _GalleryAuthorResource,
            ]
        )
        .pages([_GallerySettingsPage, _GalleryPreferencesPage, _GalleryReportsPage])
        .default_user()
    )


def build_navigation_variants() -> dict[str, tuple[str, str]]:
    """Return ``{shot_id: (label, html)}`` for navigation / user-menu / cluster shots."""
    user = OrbitUser.default()
    apps = _nav_demo_panel(layout="apps")
    sidebar = _nav_demo_panel(layout="sidebar")
    top = _nav_demo_panel(layout="top")

    badges_panel = (
        Panel.make("admin")
        .path("admin")
        .brand_name("Orbit")
        .apps_navigation()
        .dashboard(False)
        .navigation_group(
            NavigationGroup.make("Content").icon("heroicon-o-document-text").sort(10)
        )
        .resources([_GalleryInboxResource, _GalleryPostResource])
        .pages([_GalleryReportsPage])
        .default_user()
    )

    parent_panel = (
        Panel.make("admin")
        .path("admin")
        .brand_name("Orbit")
        .sidebar_navigation()
        .dashboard(False)
        .navigation_group(
            NavigationGroup.make("System").icon("heroicon-o-cog-6-tooth").sort(10)
        )
        .pages([_GallerySettingsPage, _GalleryPreferencesPage])
        .default_user()
    )

    custom_panel = (
        Panel.make("admin")
        .path("admin")
        .brand_name("Orbit")
        .apps_navigation()
        .dashboard(False)
        .navigation_group(
            NavigationGroup.make("Content").icon("heroicon-o-document-text").sort(10)
        )
        .navigation_items(
            [
                NavigationItem.make("docs")
                .label("External docs")
                .url("https://orbit.almasix.com")
                .icon("heroicon-o-book-open")
                .group("Content")
                .sort(50)
                .open_url_in_new_tab()
                .badge("Ext", color="info"),
            ]
        )
        .resources([_GalleryPostResource])
        .default_user()
    )

    pages_panel = (
        Panel.make("admin")
        .path("admin")
        .brand_name("Orbit")
        .apps_navigation()
        .dashboard(False)
        .navigation_group(
            NavigationGroup.make("Content").icon("heroicon-o-document-text").sort(10)
        )
        .pages([_GalleryReportsPage, _GallerySettingsPage])
        .default_user()
    )

    user_menu_panel = (
        Panel.make("admin")
        .path("admin")
        .brand_name("Orbit")
        .apps_navigation()
        .dashboard(False)
        .resources([_GalleryPostResource])
        .user_menu_items(
            [
                UserMenuItem.make("settings")
                .label("Settings")
                .url("/admin/settings")
                .icon("heroicon-o-cog-6-tooth")
                .group("Account")
                .sort(10),
                UserMenuItem.make("docs")
                .label("Documentation")
                .url("https://orbit.almasix.com")
                .icon("heroicon-o-book-open")
                .group("Help")
                .sort(20),
            ]
        )
        .user_menu_items(
            {
                "profile": lambda item: item.label("Edit profile")
                .url("/admin/profile")
                .icon("heroicon-o-user-circle"),
                "logout": lambda item: item.label("Sign out").post_to_url(),
            }
        )
        .default_user()
    )

    user_menu_sidebar = (
        Panel.make("admin")
        .path("admin")
        .brand_name("Orbit")
        .sidebar_navigation()
        .dashboard(False)
        .resources([_GalleryPostResource])
        .user_menu(position="sidebar")
        .user_menu_items(
            [
                UserMenuItem.make("settings")
                .label("Settings")
                .url("/admin/settings")
                .icon("heroicon-o-cog-6-tooth"),
            ]
        )
        .default_user()
    )

    cluster_panel = (
        Panel.make("admin")
        .path("admin")
        .brand_name("Orbit")
        .apps_navigation()
        .dashboard(False)
        .navigation_group(
            NavigationGroup.make("Platform").icon("heroicon-o-squares-2x2").sort(10)
        )
        .clusters([_GallerySettingsCluster])
        .resources([_GalleryColorResource, _GalleryFontResource, _GalleryPostResource])
        .default_user()
    )

    cluster_top = (
        Panel.make("admin")
        .path("admin")
        .brand_name("Orbit")
        .sidebar_navigation()
        .dashboard(False)
        .clusters([_GallerySettingsCluster])
        .resources([_GalleryColorResource, _GalleryFontResource])
        .default_user()
    )
    # Force top sub-nav for the dedicated shot.
    _GallerySettingsCluster.sub_navigation_position = "top"

    collapse_panel = (
        Panel.make("admin")
        .path("admin")
        .brand_name("Orbit")
        .apps_navigation()
        .sidebar_collapsible()
        .sidebar_width("16rem")
        .collapsed_sidebar_width("4.5rem")
        .dashboard(False)
        .navigation_group(
            NavigationGroup.make("Content").icon("heroicon-o-document-text").sort(10)
        )
        .resources([_GalleryPostResource, _GalleryInboxResource])
        .default_user()
    )

    overview_html = _nav_shell(apps, active_path="/admin/posts", user=user)
    # Restore cluster position after top shot build prep.
    cluster_top_html = _nav_shell(
        cluster_top,
        _nav_placeholder("Colors"),
        active_path="/admin/settings/colors",
        user=user,
    )
    _GallerySettingsCluster.sub_navigation_position = "start"
    cluster_html = _nav_shell(
        cluster_panel,
        _nav_placeholder("Colors"),
        active_path="/admin/settings/colors",
        user=user,
    )

    return {
        "navigation/overview": (
            "Navigation overview",
            overview_html,
        ),
        "navigation/overview/layouts-apps": (
            "Navigation — apps layout",
            _nav_shell(apps, active_path="/admin/posts", user=user),
        ),
        "navigation/overview/layouts-sidebar": (
            "Navigation — sidebar layout",
            _nav_shell(sidebar, active_path="/admin/posts", user=user),
        ),
        "navigation/overview/layouts-top": (
            "Navigation — top layout",
            _nav_shell(top, active_path="/admin/posts", user=user),
        ),
        "navigation/overview/groups": (
            "Navigation — groups",
            _nav_shell(apps, active_path="/admin/authors", user=user),
        ),
        "navigation/overview/subgroups": (
            "Navigation — subgroups",
            _nav_shell(apps, active_path="/admin/reports", user=user),
        ),
        "navigation/overview/badges": (
            "Navigation — badges",
            _nav_shell(badges_panel, active_path="/admin/inbox", user=user),
        ),
        "navigation/overview/parent-items": (
            "Navigation — parent items",
            _nav_shell(parent_panel, active_path="/admin/preferences", user=user),
        ),
        "navigation/overview/custom-items": (
            "Navigation — custom items",
            _nav_shell(custom_panel, active_path="/admin/posts", user=user),
        ),
        "navigation/overview/sidebar-collapse": (
            "Navigation — sidebar collapse",
            _nav_shell(collapse_panel, active_path="/admin/posts", user=user).replace(
                "collapsed: false",
                "collapsed: true",
                1,
            ),
        ),
        "navigation/custom-pages": (
            "Custom pages",
            _nav_shell(pages_panel, _nav_placeholder("Reports"), active_path="/admin/reports", user=user),
        ),
        "navigation/user-menu": (
            "User menu",
            _nav_shell(user_menu_panel, active_path="/admin/posts", user=user),
        ),
        "navigation/user-menu/groups": (
            "User menu — groups",
            _nav_shell(user_menu_panel, active_path="/admin/posts", user=user),
        ),
        "navigation/user-menu/position": (
            "User menu — sidebar position",
            _nav_shell(user_menu_sidebar, active_path="/admin/posts", user=user),
        ),
        "navigation/clusters": (
            "Clusters",
            cluster_html,
        ),
        "navigation/clusters/sub-nav": (
            "Clusters — sub-navigation",
            cluster_top_html,
        ),
    }


_STATIC_TOAST_HOST = (
    "position:relative;inset:auto;transform:none;width:min(24rem,100%);"
    "pointer-events:auto;padding:0;left:auto;right:auto;top:auto;bottom:auto;"
)


def _toast_frame(*notes: Notification, alignment: str = "end", valign: str = "start") -> str:
    """Static toast stack for screenshots (relative, not fixed viewport)."""
    parts: list[str] = []
    for n in notes:
        if not n._persistent:
            object.__setattr__(n, "_persistent", True)
            object.__setattr__(n, "persistent", True)
        parts.append(n.render())
    body = "".join(parts)
    return (
        f'<div class="or-notifications or-notifications-align-{alignment} '
        f'or-notifications-valign-{valign}" style="{_STATIC_TOAST_HOST}">{body}</div>'
    )


def _db_panel(*, position: str = "topbar", open_panel: bool = True) -> str:
    seeds = [
        PanelNotification.make("Welcome")
        .body("Database notifications are on.")
        .status("success")
        .id("n-welcome"),
        PanelNotification.make("Deploy finished")
        .body("v1.4.2 is live on production.")
        .status("info")
        .id("n-deploy"),
        PanelNotification.make("Backup complete")
        .body("Nightly backup finished.")
        .status("success")
        .read()
        .id("n-backup"),
    ]
    panel = (
        Panel.make("admin")
        .path("admin")
        .brand_name("Orbit")
        .apps_navigation()
        .dashboard(False)
        .database_notifications(seeds, position=position)  # type: ignore[arg-type]
        .database_notifications_polling("30s")
        .resources([_GalleryPostResource])
        .default_user()
    )
    user = OrbitUser.default()
    html = _nav_shell(panel, active_path="/admin/posts", user=user)
    if open_panel:
        # Force the Alpine panel open for static screenshots.
        html = html.replace(
            'class="or-notify-panel" x-show="open" x-cloak',
            'class="or-notify-panel" style="display:block"',
            1,
        )
    return html


def build_notification_variants() -> dict[str, tuple[str, str]]:
    """Return ``{shot_id: (label, html)}`` for notification docs shots."""
    overview = _toast_frame(
        Notification.make()
        .title("Saved successfully")
        .success()
        .body("Changes to the post have been saved."),
        Notification.make()
        .title("Storage almost full")
        .warning()
        .body("Free up space or upgrade your plan."),
        Notification.make()
        .title("Export failed")
        .danger()
        .body("Could not write the CSV file."),
    )

    actions_note = (
        Notification.make()
        .title("Saved successfully")
        .success()
        .body("Changes to the post have been saved.")
        .actions(
            [
                NotificationAction.make("view").button().url("/admin/posts/1"),
                NotificationAction.make("undo").color("gray").close(),
            ]
        )
    )

    # Alignment shot: temporarily set process-wide alignment for host classes.
    Notifications.reset()
    Notifications.alignment(Alignment.START)
    Notifications.vertical_alignment(VerticalAlignment.END)
    alignment_html = _toast_frame(
        Notification.make().title("Aligned start / end").info().body("Toast host corner."),
        alignment="start",
        valign="end",
    )
    Notifications.reset()

    broadcast = _toast_frame(
        Notification.make()
        .title("Deploy finished")
        .success()
        .body("v1.4.2 is live on production."),
    )
    live_html = (
        '<div class="or-live-notifier" data-channels="App.Models.User.1,orders" '
        'style="display:block">'
        f"{broadcast}"
        '<p class="or-muted" style="margin-top:0.75rem;font-size:0.8125rem;'
        'color:var(--or-muted)">Listening: App.Models.User.1, orders</p></div>'
    )

    return {
        "notifications/overview": (
            "Notifications overview",
            overview,
        ),
        "notifications/overview/title": (
            "Notifications — title",
            _toast_frame(Notification.make().title("Saved successfully").info()),
        ),
        "notifications/overview/icon": (
            "Notifications — icon",
            _toast_frame(
                Notification.make()
                .title("Saved successfully")
                .icon("heroicon-o-document-text")
                .icon_color("success")
                .color("success")
            ),
        ),
        "notifications/overview/status": (
            "Notifications — status",
            _toast_frame(
                Notification.make().title("Success").success(),
                Notification.make().title("Warning").warning(),
                Notification.make().title("Danger").danger(),
                Notification.make().title("Info").info(),
            ),
        ),
        "notifications/overview/color": (
            "Notifications — color",
            _toast_frame(
                Notification.make().title("Saved successfully").color("success").info()
            ),
        ),
        "notifications/overview/duration": (
            "Notifications — duration",
            _toast_frame(
                Notification.make()
                .title("Saved successfully")
                .success()
                .seconds(5)
                .body("Closes after 5 seconds.")
            ),
        ),
        "notifications/overview/persistent": (
            "Notifications — persistent",
            _toast_frame(
                Notification.make()
                .title("Review required")
                .warning()
                .persistent()
                .body("Dismiss manually when finished.")
            ),
        ),
        "notifications/overview/body": (
            "Notifications — body",
            _toast_frame(
                Notification.make()
                .title("Saved successfully")
                .success()
                .body("Changes to the post have been saved.")
            ),
        ),
        "notifications/overview/actions": (
            "Notifications — actions",
            _toast_frame(actions_note),
        ),
        "notifications/overview/alignment": (
            "Notifications — alignment",
            alignment_html,
        ),
        "notifications/database-notifications": (
            "Database notifications",
            _db_panel(),
        ),
        "notifications/database-notifications/enable": (
            "Database — enable",
            _db_panel(),
        ),
        "notifications/database-notifications/send": (
            "Database — send",
            _toast_frame(
                Notification.make()
                .title("New comment")
                .info()
                .body("Alex replied on Launch Orbit.")
            )
            + '<p style="margin-top:0.75rem;font-size:0.8125rem;color:var(--or-muted)">'
            "Also stored for the panel bell via "
            "<code>.send_to_database()</code>.</p>",
        ),
        "notifications/database-notifications/position": (
            "Database — sidebar position",
            _db_panel(position="sidebar"),
        ),
        "notifications/database-notifications/mark-read": (
            "Database — mark read",
            _db_panel(),
        ),
        "notifications/broadcast-notifications": (
            "Broadcast notifications",
            broadcast,
        ),
        "notifications/broadcast-notifications/send": (
            "Broadcast — send",
            _toast_frame(
                Notification.make()
                .title("Processing complete")
                .success()
                .body("Queued job finished.")
            ),
        ),
        "notifications/broadcast-notifications/live-host": (
            "Broadcast — live host",
            live_html,
        ),
    }


def _open_tenant_menu(html: str) -> str:
    """Force the tenant switcher menu open for static screenshots."""
    return html.replace(
        'class="or-tenant-menu" x-show="open" x-cloak',
        'class="or-tenant-menu" style="display:block"',
        1,
    )


def _tenancy_demo_panel() -> Panel:
    acme = Tenant(1, "Acme Corp", slug="acme")
    beta = Tenant(2, "Beta Labs", slug="beta")
    tenancy = (
        Tenancy()
        .tenants([acme, beta])
        .current(acme)
        .registration(True)
        .profile(True)
        .menu_items([{"label": "Invite members", "url": "/admin/invite"}])
        .scope_using(
            lambda rows, tenant: [
                r
                for r in rows
                if not isinstance(r, dict)
                or "tenant_id" not in r
                or r.get("tenant_id") == tenant.id
            ]
        )
    )
    return (
        Panel.make("admin")
        .path("admin")
        .brand_name("Orbit")
        .apps_navigation()
        .dashboard(False)
        .tenant(tenancy)
        .tenant_registration(True)
        .tenant_profile(True)
        .navigation_group(
            NavigationGroup.make("Tenancy").icon("heroicon-o-building-office-2").sort(10)
        )
        .resources([_GalleryTenantProjectResource])
        .default_user()
    )


class _GalleryTenantProjectResource(Resource):
    model = type("Project", (), {})
    slug = "tenant-projects"
    navigation_label = "Projects"
    navigation_group = "Tenancy"
    navigation_icon = "heroicon-o-folder"
    records: list[dict] = [
        {"id": 1, "title": "Launch site", "tenant_id": 1, "status": "Active"},
        {"id": 2, "title": "Billing revamp", "tenant_id": 1, "status": "Draft"},
        {"id": 3, "title": "Beta onboarding", "tenant_id": 2, "status": "Active"},
    ]

    @classmethod
    def get_records(cls) -> list[dict]:
        return list(cls.records)

    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.heading("Projects")
            .description("Scoped to the current tenant.")
            .columns(
                [
                    TextColumn.make("title").searchable(),
                    TextColumn.make("status").label("Status"),
                ]
            )
        )


def build_tenancy_variants() -> dict[str, tuple[str, str]]:
    """Return ``{shot_id: (label, html)}`` for multi-tenancy docs shots."""
    panel = _tenancy_demo_panel()
    user = OrbitUser.default()
    tenancy = panel.get_tenancy()
    assert tenancy is not None

    closed = _nav_shell(
        panel,
        _nav_placeholder("Projects"),
        active_path="/admin/tenant-projects",
        user=user,
    )
    opened = _open_tenant_menu(closed)

    scoped_rows = tenancy.scope_query(_GalleryTenantProjectResource.get_records())
    scoped_table = (
        Table.make()
        .heading("Projects")
        .description("Showing Acme Corp only — switch tenants to see Beta Labs.")
        .columns(
            [
                TextColumn.make("title").searchable(),
                TextColumn.make("status").label("Status"),
            ]
        )
        .records(scoped_rows)
        .render()
    )
    scoped_shell = _nav_shell(
        panel,
        scoped_table,
        active_path="/admin/tenant-projects",
        user=user,
    )

    return {
        "users/tenancy/switcher": (
            "Tenancy — switcher",
            closed,
        ),
        "users/tenancy/menu": (
            "Tenancy — switcher menu",
            opened,
        ),
        "users/tenancy/scoped-list": (
            "Tenancy — scoped list",
            scoped_shell,
        ),
    }


# --- resources ---------------------------------------------------------------


class _GalleryCommentsRelation(RelationManager):
    relationship = "comments"
    title = "Comments"
    description = "Reader replies attached to this post."
    record_title_attribute = "author"

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns(
            [
                TextColumn.make("author").label("Author").searchable(),
                TextColumn.make("body").label("Comment").limit(60),
                TextColumn.make("status").label("Status").badge(),
            ]
        )


class _GalleryPostResource(Resource):
    model = type("Post", (), {})
    slug = "posts"
    navigation_label = "Posts"
    record_title_attribute = "title"
    model_label = "Post"
    global_search_attributes = ("title", "body")
    global_search_result_details = ("status",)
    records: list[dict] = [
        {
            "id": 1,
            "title": "Launch Orbit",
            "status": "published",
            "body": "Ship the admin panel.",
            "comments": [
                {"id": 1, "author": "Ada Lovelace", "body": "Shipping this week?", "status": "visible"},
                {"id": 2, "author": "Grace Hopper", "body": "The tables feel fast now.", "status": "visible"},
                {"id": 3, "author": "Anon", "body": "Removed by a moderator.", "status": "hidden"},
            ],
        }
    ]

    @classmethod
    def get_records(cls) -> list[dict]:
        return list(cls.records)

    @classmethod
    def infolist(cls, infolist: Infolist) -> Infolist:
        return infolist.schema(
            [
                TextEntry.make("title").label("Title").weight("bold"),
                TextEntry.make("status").label("Status").badge().color("success"),
                TextEntry.make("body").label("Body"),
            ]
        )

    @classmethod
    def get_relations(cls) -> list[type]:
        return [_GalleryCommentsRelation]


class _GalleryArchiveResource(Resource):
    model = type("Archive", (), {})
    slug = "archives"
    navigation_label = "Archive"
    records_mutable = True
    soft_deletes = True
    records: list[dict] = [
        {"id": 1, "title": "Quarterly report", "deleted_at": None},
        {"id": 2, "title": "Legacy pricing page", "deleted_at": "2026-02-01"},
    ]

    @classmethod
    def get_records(cls) -> list[dict]:
        return list(cls.records)

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.heading("Archive").columns(
            [
                TextColumn.make("title").label("Title"),
                TextColumn.make("deleted_at").label("Deleted").placeholder("—"),
            ]
        )


def build_resource_variants() -> dict[str, tuple[str, str]]:
    """Return ``{shot_id: (label, html)}`` for the Resources docs shots."""
    from almasix.orbit.panels.global_search import render_global_search_groups
    from almasix.orbit.panels.pages.resource_pages import ViewRecord

    _GalleryPostResource._panel_path = "/admin"
    _GalleryArchiveResource._panel_path = "/admin"
    record = _GalleryPostResource.records[0]

    class _BoundView(ViewRecord):
        resource = _GalleryPostResource

    view_page = _BoundView.render(record=record)
    relation = _GalleryCommentsRelation.render(record)

    results = render_global_search_groups(
        [
            {
                "label": "Posts",
                "results": _GalleryPostResource.get_global_search_results("launch", [record]),
            },
            {
                "label": "Authors",
                "results": [
                    {
                        "title": "Ada Lovelace",
                        "url": "/admin/authors/1",
                        "details": {"Email": "ada@orbit.test"},
                    }
                ],
            },
        ]
    )
    search = (
        '<div class="or-global-search" style="width: 26rem">'
        '<input class="or-input or-global-search-input" type="search" value="launch" />'
        '<div class="or-global-search-panel" '
        'style="position: static; width: 100%; margin-top: 0.375rem">'
        f"{results}</div></div>"
    )

    trashed = (
        _GalleryArchiveResource.get_table()
        .records(_GalleryArchiveResource.get_records())
        .filter_state({"trashed": "with"})
        .render()
    )

    return {
        "resources/view-record": ("Resources — view page", view_page),
        "resources/relation-manager": ("Resources — relation manager", relation),
        "resources/global-search": ("Resources — global search", search),
        "resources/soft-deletes": ("Resources — soft deletes", trashed),
    }
