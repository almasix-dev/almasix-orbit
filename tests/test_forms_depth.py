"""Forms depth: upload storage, rich editor, key-value, morph + modal pickers."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any, ClassVar

import pytest
from almasix.orbit.forms import (
    FilesystemUploadStorage,
    FileUpload,
    Form,
    KeyValue,
    MemoryUploadStorage,
    ModalTableSelect,
    MorphToSelect,
    RichEditor,
    TextInput,
    get_upload_storage,
    set_upload_storage,
)
from almasix.orbit.forms.uploads import (
    StoredUpload,
    UploadRejected,
    UploadRules,
    UploadStorage,
    _disk_url,
    _maybe_await,
    build_upload_path,
    delete_upload,
    guess_mime,
    is_image,
    matches_accepted_types,
    sanitize_filename,
    store_upload,
    validate_upload,
)
from almasix.orbit.panels.conduit.hosts import CreateRecordHost, EditRecordHost
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.panels.uploads import (
    find_upload_field,
    handle_upload,
    handle_upload_delete,
    panel_upload_url,
    resource_upload_url,
    upload_rules_for,
)
from almasix.orbit.tables import Table, TextColumn


def run(coro: Any) -> Any:
    return asyncio.run(coro)


@pytest.fixture(autouse=True)
def memory_storage() -> Any:
    storage = MemoryUploadStorage()
    set_upload_storage(storage)
    yield storage
    set_upload_storage(MemoryUploadStorage())


# --------------------------------------------------------------------------- storage


def test_memory_storage_stores_and_deletes(memory_storage: MemoryUploadStorage) -> None:
    rules = UploadRules(directory="avatars", preserve_filenames=True)
    stored = run(store_upload(b"data", "photo.png", rules))
    assert stored.path == "avatars/photo.png"
    assert stored.mime == "image/png"
    assert stored.url.endswith("/avatars/photo.png")
    assert memory_storage.files["avatars/photo.png"] == b"data"
    assert stored.to_dict()["name"] == "photo.png"
    assert run(delete_upload(stored.path, rules)) is True
    assert run(delete_upload(stored.path, rules)) is False


def test_stored_upload_falls_back_to_path_for_url() -> None:
    assert StoredUpload(path="a/b.png", name="b.png").to_dict()["url"] == "a/b.png"


def test_get_upload_storage_returns_registered_instance(
    memory_storage: MemoryUploadStorage,
) -> None:
    assert get_upload_storage() is memory_storage
    assert isinstance(memory_storage, UploadStorage)
    # The protocol itself is a contract: its method bodies do nothing.
    assert run(UploadStorage.store(memory_storage, b"", "a.png", UploadRules())) is None
    assert run(UploadStorage.delete(memory_storage, "a.png", UploadRules())) is None


def test_random_filenames_keep_the_extension() -> None:
    path = build_upload_path("report card.PDF", UploadRules())
    assert path.endswith(".PDF")
    assert "report" not in path


def test_sanitize_filename_strips_directories_and_junk() -> None:
    assert sanitize_filename("../../etc/pa$$wd") == "pa-wd"
    assert sanitize_filename("C:\\temp\\logo.png") == "logo.png"
    assert sanitize_filename("...") == "file"
    assert sanitize_filename("") == "file"


def test_validate_upload_enforces_field_rules() -> None:
    big = b"x" * 3072
    with pytest.raises(UploadRejected, match="larger than"):
        validate_upload(big, "big.png", UploadRules(max_size=1))
    with pytest.raises(UploadRejected, match="smaller than"):
        validate_upload(b"x", "tiny.png", UploadRules(min_size=5))
    with pytest.raises(UploadRejected, match="accepted types"):
        validate_upload(b"x", "notes.txt", UploadRules(accepted_types=["image/*"]))
    validate_upload(b"x", "notes.txt", UploadRules(accepted_types=[".txt"]))


def test_accepted_type_matching_covers_every_entry_shape() -> None:
    assert matches_accepted_types("logo.png", ["", "image/*"]) is True
    assert matches_accepted_types("logo.png", [".png"]) is True
    assert matches_accepted_types("logo.png", ["image/png"]) is True
    assert matches_accepted_types("logo.png", ["application/pdf", ".pdf"]) is False


def test_mime_guessing_and_image_detection() -> None:
    assert guess_mime("a.jpeg") == "image/jpeg"
    assert guess_mime("a.unknown") == "application/octet-stream"
    assert is_image("a.webp") is True
    assert is_image("a.zip") is False


def test_filesystem_storage_writes_through_a_disk(monkeypatch: Any) -> None:
    import sys

    written: dict[str, Any] = {}
    deleted: list[str] = []

    class FakeDisk:
        async def put(self, path: str, data: bytes, visibility: str | None = None) -> None:
            written["path"] = path
            written["data"] = data
            written["visibility"] = visibility

        def delete(self, path: str) -> bool:
            deleted.append(path)
            return True

        def url(self, path: str) -> str:
            return f"https://cdn.test/{path}"

    class FakeStorage:
        @staticmethod
        def disk(name: str | None = None) -> FakeDisk:
            written["disk"] = name
            return FakeDisk()

    monkeypatch.setitem(
        sys.modules, "almasix.filesystem", SimpleNamespace(Storage=FakeStorage)
    )
    storage = FilesystemUploadStorage()
    rules = UploadRules(disk="s3", directory="docs", visibility="public", preserve_filenames=True)
    stored = run(storage.store(b"pdf", "guide.pdf", rules))
    assert written["disk"] == "s3"
    assert written["path"] == "docs/guide.pdf"
    assert written["visibility"] == "public"
    assert stored.url == "https://cdn.test/docs/guide.pdf"
    assert run(storage.delete("docs/guide.pdf", rules)) is True
    assert deleted == ["docs/guide.pdf"]


def test_disk_url_falls_back_when_the_disk_cannot_build_one() -> None:
    class Raising:
        def url(self, path: str) -> str:
            raise RuntimeError("no public url")

    assert _disk_url(Raising(), "a.png", "/storage") == "/storage/a.png"
    assert _disk_url(object(), "a.png", "/storage") == "/storage/a.png"
    from almasix.orbit.forms.uploads import public_upload_url

    assert public_upload_url("ee98.png") == "/storage/ee98.png"
    assert public_upload_url("/storage/ee98.png") == "/storage/ee98.png"
    assert public_upload_url("https://cdn.test/a.png") == "https://cdn.test/a.png"
    assert public_upload_url("") == ""


def test_memory_upload_urls_use_orbit_uploads_prefix(
    memory_storage: MemoryUploadStorage,
) -> None:
    from almasix.orbit.forms.uploads import public_upload_url

    stored = run(store_upload(b"img", "a.png", UploadRules(directory="avatars")))
    assert stored.url.startswith("/orbit-uploads/")
    assert public_upload_url(stored.path) == stored.url
    assert memory_storage.get_bytes(stored.path) == b"img"
    assert memory_storage.get_bytes(f"orbit-uploads/{stored.path}") == b"img"


def test_public_upload_url_tolerates_get_storage_errors(monkeypatch) -> None:
    from almasix.orbit.forms import uploads as uploads_mod

    monkeypatch.setattr(
        uploads_mod,
        "get_upload_storage",
        lambda: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    assert uploads_mod.public_upload_url("x.png") == "/storage/x.png"


def test_handle_serve_upload_requires_memory_storage() -> None:
    from almasix.orbit.panels.uploads import handle_serve_upload

    set_upload_storage(FilesystemUploadStorage())
    out = run(handle_serve_upload("a.png"))
    assert getattr(out, "status_code", None) == 404
    set_upload_storage(MemoryUploadStorage())


def test_maybe_await_passes_plain_values_through() -> None:
    async def coro() -> str:
        return "awaited"

    assert run(_maybe_await("plain")) == "plain"
    assert run(_maybe_await(coro())) == "awaited"


# --------------------------------------------------------------------------- FileUpload field


def test_file_upload_renders_rules_as_data_attributes() -> None:
    field = (
        FileUpload.make("avatar")
        .disk("s3")
        .directory("avatars")
        .visibility("private")
        .avatar()
        .image_preview()
        .reorderable()
        .downloadable()
        .openable()
        .move_files()
        .store_files(False)
        .fetch_file_information(False)
        .preserve_filenames()
        .image_editor()
        .image_editor_aspect_ratios(["1:1", "16:9"])
        .max_size(2048)
        .min_size(1)
        .max_files(3)
        .min_files(1)
        .panel_layout()
        .image_preview_height(120)
        .prevent_file_path_tampering()
        .image_size(min_width=10, max_width=20, min_height=30, max_height=40)
        .accepted_file_types(["image/*"])
        .upload_url("/admin/orbit-upload")
    )
    html = field.render(None)
    for attr in (
        'data-disk="s3"',
        'data-directory="avatars"',
        'data-visibility="private"',
        'data-avatar="true"',
        'data-image-preview="true"',
        'data-reorderable="true"',
        'data-downloadable="true"',
        'data-openable="true"',
        'data-move-files="true"',
        'data-store-files="false"',
        'data-fetch-file-information="false"',
        'data-preserve-filenames="true"',
        'data-image-editor="true"',
        'data-aspect-ratios="1:1,16:9"',
        'data-max-size="2048"',
        'data-min-size="1"',
        'data-max-files="3"',
        'data-min-files="1"',
        'data-panel-layout="true"',
        'data-preview-height="120"',
        'data-prevent-tampering="true"',
        'data-image-min-width="10"',
        'data-image-max-height="40"',
        'data-upload-url="/admin/orbit-upload"',
        'data-upload-field="avatar"',
        'data-upload-path="data.avatar"',
        "or-field-FileUpload or-file-avatar",
        "or-file-panel",
        "wire:ignore",
        "conduit:ignore",
    ):
        assert attr in html, attr
    assert 'accept="image/*"' in html
    assert " multiple" in html
    assert "or-file-progress" not in html
    assert "data-existing=" not in html
    assert "conduit:model=" not in html
    assert "wire:model=" not in html


def test_file_upload_previews_existing_files() -> None:
    field = FileUpload.make("docs").downloadable().openable()
    html = field.render(
        [
            {"path": "docs/a.png", "url": "/storage/docs/a.png", "name": "a.png"},
            "docs/b.pdf",
            "",
        ]
    )
    assert 'data-existing="' in html
    assert "docs/a.png" in html
    assert "docs/b.pdf" in html
    assert "or-file-preview-fallback" in html
    assert '<img class="or-file-thumb" src="/storage/docs/a.png"' in html
    assert '<span class="or-file-name">b.pdf</span>' in html
    assert 'href="/storage/docs/a.png" target="_blank"' in html
    assert "download" in html
    assert html.count("or-file-card") == 2 + html.count("or-file-card-actions")


def test_file_upload_single_value_and_no_preview() -> None:
    html = FileUpload.make("logo").render("logo.png")
    assert "or-file-card" in html
    assert "data-existing=" in html
    assert "/storage/logo.png" in html
    assert "or-file-preview" not in FileUpload.make("logo").previewable(False).render("logo.png")
    assert "data-existing=" in FileUpload.make("logo").previewable(False).render("logo.png")


def test_file_upload_js_syncs_data_path_via_sync_data_path() -> None:
    """Regression: FilePond must sync ``data.{field}`` without remorphing Alpine islands."""
    from pathlib import Path

    js = Path("packages/panels/src/almasix/orbit/resources/js/orbit.js").read_text(
        encoding="utf-8"
    )
    assert "data-upload-path" in js
    assert "sync_data_path" in js
    assert "wire:ignore" in Path(
        "packages/forms/src/almasix/orbit/forms/components.py"
    ).read_text(encoding="utf-8")

    field = FileUpload.make("attachment").disabled()
    html = field.render(None, upload_url="/panel/orbit-upload", resource=_UploadResource)
    assert " disabled" in html
    assert 'data-upload-url="/panel/orbit-upload"' in html
    assert 'data-upload-resource="uploads"' in html


def test_hidden_file_upload_renders_nothing() -> None:
    assert FileUpload.make("avatar").hidden().render(None) == ""


def test_upload_rules_come_off_the_field() -> None:
    rules = (
        FileUpload.make("avatar")
        .disk("s3")
        .directory("avatars")
        .max_size(100)
        .accepted_file_types(["image/*"])
        .get_upload_rules()
    )
    assert rules.disk == "s3"
    assert rules.directory == "avatars"
    assert rules.max_size == 100
    assert rules.accepted_types == ["image/*"]


# --------------------------------------------------------------------------- upload endpoint


class _UploadResource(Resource):
    model = type("Upload", (), {})
    slug = "uploads"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("title"),
                FileUpload.make("avatar").directory("avatars").max_size(1),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")])


class _BrokenFormResource(Resource):
    model = type("Broken", (), {})
    slug = "broken"

    @classmethod
    def get_form(cls) -> Any:
        raise RuntimeError("form blew up")

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")])


def _upload_panel() -> Panel:
    return Panel.make("uploads-panel").path("/admin").resources([_BrokenFormResource, _UploadResource])


def test_find_upload_field_skips_other_resources_and_broken_forms() -> None:
    panel = _upload_panel()
    assert find_upload_field(panel, "", "") is None
    assert find_upload_field(panel, "", "avatar") is not None  # skips the broken resource
    assert find_upload_field(panel, "uploads", "title") is None
    assert find_upload_field(panel, "uploads", "avatar") is not None
    assert find_upload_field(panel, "missing", "avatar") is None
    assert upload_rules_for(panel, "uploads", "missing") is None


def test_handle_upload_stores_and_reports_rejections(
    memory_storage: MemoryUploadStorage,
) -> None:
    panel = _upload_panel()
    ok = run(
        handle_upload(panel, resource="uploads", field="avatar", filename="me.png", data=b"tiny")
    )
    assert ok["ok"] is True
    assert ok["file"]["path"].startswith("avatars/")

    too_big = run(
        handle_upload(
            panel, resource="uploads", field="avatar", filename="big.png", data=b"x" * 4096
        )
    )
    assert too_big["ok"] is False
    assert "larger than" in too_big["error"]

    unknown = run(
        handle_upload(panel, resource="uploads", field="nope", filename="a.png", data=b"a")
    )
    assert unknown == {"ok": False, "error": "Unknown upload field 'nope'."}


def test_handle_upload_delete_removes_the_file(memory_storage: MemoryUploadStorage) -> None:
    panel = _upload_panel()
    stored = run(
        handle_upload(panel, resource="uploads", field="avatar", filename="me.png", data=b"tiny")
    )
    path = stored["file"]["path"]
    assert run(
        handle_upload_delete(panel, resource="uploads", field="avatar", path=path)
    ) == {"ok": True, "path": path}
    assert path not in memory_storage.files
    assert run(handle_upload_delete(panel, resource="uploads", field="avatar", path="")) == {
        "ok": False,
        "error": "No file path given.",
    }
    assert run(handle_upload_delete(panel, resource="uploads", field="x", path="a"))["ok"] is False


class _FakeUpload:
    def __init__(self, filename: str, data: Any) -> None:
        self.filename = filename
        self._data = data

    async def read(self) -> Any:
        return self._data


class _UploadRequest:
    """Minimal stand-in for the framework request the upload route receives."""

    def __init__(
        self,
        *,
        fields: dict[str, str] | None = None,
        query: dict[str, str] | None = None,
        upload: Any = None,
        file_raises: bool = False,
    ) -> None:
        self._fields = fields or {}
        self._upload = upload
        self._file_raises = file_raises
        qs = "&".join(f"{k}={v}" for k, v in (query or {}).items())
        self.url = SimpleNamespace(path="/admin/orbit-upload", query=qs)
        self.path = "/admin/orbit-upload"

    def input(self, name: str) -> Any:
        return self._fields.get(name)

    def file(self, name: str) -> Any:
        if self._file_raises:
            raise RuntimeError("no multipart parser")
        return self._upload


def _upload_route(panel: Panel) -> Any:
    from almasix.orbit.panels.routing import mount_panel
    from almasix.routing.router import Router

    router = Router()
    mount_panel(router, panel)
    return next(r for r in router.routes if str(r.uri or "").endswith("orbit-upload"))


def test_upload_route_stores_deletes_and_rejects(memory_storage: MemoryUploadStorage) -> None:
    panel = Panel.make("upload-route").path("admin").middleware([], replace=True).resources(
        [_UploadResource]
    )
    route = _upload_route(panel)

    stored = run(
        route.action(
            _UploadRequest(
                fields={"resource": "uploads", "field": "avatar"},
                upload=_FakeUpload("me.png", b"tiny"),
            )
        )
    )
    assert b'"ok":true' in _body(stored)

    path = next(iter(memory_storage.files))
    deleted = run(
        route.action(
            _UploadRequest(
                fields={"resource": "uploads", "field": "avatar", "path": path, "intent": "delete"}
            )
        )
    )
    assert b'"ok":true' in _body(deleted)
    assert memory_storage.files == {}

    empty = run(
        route.action(
            _UploadRequest(query={"resource": "uploads", "field": "avatar"}, file_raises=True)
        )
    )
    assert b'"ok":false' in _body(empty)


def test_upload_route_reads_lists_and_string_bodies(memory_storage: MemoryUploadStorage) -> None:
    panel = Panel.make("upload-list").path("admin").middleware([], replace=True).resources(
        [_UploadResource]
    )
    route = _upload_route(panel)
    response = run(
        route.action(
            _UploadRequest(
                fields={"resource": "uploads", "field": "avatar"},
                upload=[_FakeUpload("", "text body")],
            )
        )
    )
    assert b'"ok":true' in _body(response)
    assert list(memory_storage.files.values()) == [b"text body"]

    none_list = run(
        route.action(
            _UploadRequest(fields={"resource": "uploads", "field": "avatar"}, upload=[])
        )
    )
    assert b'"ok":false' in _body(none_list)


def test_request_helpers_tolerate_unusual_request_objects() -> None:
    from almasix.orbit.panels.routing import _form_param, _request_file, _upload_payload

    class Hostile:
        def input(self, name: str) -> str:
            raise RuntimeError("no form parser")

    assert _request_file(None) is None
    assert _request_file(SimpleNamespace()) is None
    assert _form_param(None, "field") == ""
    assert _form_param(SimpleNamespace(), "field") == ""
    assert _form_param(Hostile(), "field") == ""
    assert run(_upload_payload(None)) == {"resource": "", "field": "", "filename": "", "data": b""}


def test_panel_can_turn_uploads_off() -> None:
    panel = Panel.make("no-uploads").path("admin").middleware([], replace=True).uploads(False)
    assert panel.uploads_enabled() is False
    from almasix.orbit.panels.routing import mount_panel
    from almasix.routing.router import Router

    router = Router()
    mount_panel(router, panel)
    assert not any(str(r.uri or "").endswith("orbit-upload") for r in router.routes)
    assert Panel.make("with-uploads").path("admin").upload_url() == "/admin/orbit-upload"


def _body(response: Any) -> bytes:
    content = getattr(response, "body", getattr(response, "content", response))
    if isinstance(content, str):
        return content.encode()
    return bytes(content)


def test_upload_urls_follow_the_panel_path() -> None:
    assert panel_upload_url(_upload_panel()) == "/admin/orbit-upload"
    assert panel_upload_url(Panel.make("root").path("/")) == "/orbit-upload"
    assert resource_upload_url(SimpleNamespace(_panel_path="/admin")) == "/admin/orbit-upload"
    assert resource_upload_url(SimpleNamespace()) == "/orbit-upload"


# --------------------------------------------------------------------------- RichEditor


def test_rich_editor_renders_the_requested_toolbar() -> None:
    html = (
        RichEditor.make("body")
        .toolbar_buttons(["bold", "h2", "bulletList", "link"])
        .placeholder("Write something…")
        .merge_tags(["customer_name"])
        .min_height(320)
        .render("<p>Hi</p>")
    )
    assert 'data-tool="bold"' in html
    assert 'data-tool="h2"' in html
    assert 'data-tool="mergeTag:customer_name"' in html
    assert "{{ customer_name }}" in html
    assert 'data-placeholder="Write something…"' in html
    assert 'style="min-height: 320px"' in html


def test_rich_editor_toolbar_button_appends_a_tool() -> None:
    editor = (
        RichEditor.make("body")
        .toolbar_buttons(["bold"])
        .toolbar_button("italic")
        .toolbar_button("bold")
        .toolbar_button("callout", "Callout box")
    )
    assert editor.get_toolbar_buttons() == ["bold", "italic", "callout"]
    html = editor.render(None)
    assert 'data-tool="bold"' in html
    assert 'data-tool="italic"' in html
    assert ">Callout box<" in html


def test_rich_editor_labels_and_heights() -> None:
    editor = RichEditor.make("body").merge_tags(["name"]).min_height("18rem")
    assert editor.get_merge_tags() == ["name"]
    assert 'style="min-height: 18rem"' in editor.render(None)
    assert editor.tool_label("bold") == "Bold"
    assert editor.tool_label("superscript") == "Superscript"


def test_disabled_rich_editor_locks_the_surface() -> None:
    html = RichEditor.make("body").disabled().render("<p>Hi</p>")
    assert 'data-editor-disabled="true"' in html
    assert " disabled" in html


# --------------------------------------------------------------------------- KeyValue


def test_key_value_renders_a_row_per_entry() -> None:
    html = (
        KeyValue.make("meta")
        .key_label("Attribute")
        .value_label("Detail")
        .key_placeholder("e.g. colour")
        .value_placeholder("e.g. blue")
        .add_action_label("Add attribute")
        .reorderable()
        .render({"colour": "blue", "size": "M"})
    )
    assert "<span>Attribute</span><span>Detail</span>" in html
    assert html.count('class="or-key-value-row"') == 2
    assert "setKeyValueKey('meta', 'colour', $event.target.value)" in html
    assert 'wire:model="meta.colour"' in html
    assert "removeKeyValueRow('meta', 'size')" in html
    assert "addKeyValueRow('meta')" in html
    assert "Add attribute" in html
    assert 'data-reorderable="true"' in html


def test_key_value_shows_a_blank_row_when_empty() -> None:
    html = KeyValue.make("meta").render({})
    assert "or-key-value-empty" in html
    assert 'placeholder="Key"' in html


def test_key_value_can_lock_keys_and_hide_actions() -> None:
    html = (
        KeyValue.make("meta")
        .editable_keys(False)
        .addable(False)
        .deletable(False)
        .render({"colour": "blue"})
    )
    assert "readonly" in html
    assert "setKeyValueKey" not in html
    assert "removeKeyValueRow" not in html
    assert "addKeyValueRow" not in html


def test_disabled_key_value_disables_every_input() -> None:
    html = KeyValue.make("meta").disabled().render({"colour": "blue"})
    assert html.count(" disabled") >= 2
    assert "addKeyValueRow" not in html
    assert KeyValue.make("meta").hidden().render({}) == ""


# --------------------------------------------------------------------------- MorphToSelect


def test_morph_to_select_loads_options_for_the_chosen_type() -> None:
    calls: list[tuple[str, str]] = []

    def options(type: str = "", search: str = "") -> dict[str, str]:
        calls.append((type, search))
        return {"1": "Orbit launch", "2": "Second post"} if type == "post" else {}

    field = (
        MorphToSelect.make("commentable")
        .types([{"type": "post", "label": "Post"}, {"type": "video", "label": "Video"}])
        .searchable()
        .options_using(options)
    )
    html = field.render({"type": "post", "id": "1"}, morph_search={"commentable": "launch"})
    assert '<option value="post" selected>Post</option>' in html
    assert "Orbit launch" in html
    assert "Second post" not in html
    assert "$data.onTypeChange" in html
    assert "or-morph-record-combobox" in html
    assert 'data-sync-path="data.commentable.id"' in html
    assert 'conduit:model="data.commentable.type"' not in html
    assert 'conduit:model="data.commentable.id"' not in html
    assert "or-morph-to-select__type" in html
    assert calls == [("post", "launch")]


def test_morph_to_select_without_a_loader_uses_declared_options() -> None:
    field = MorphToSelect.make("commentable").types(
        [{"type": "post", "label": "Post", "options": {"1": "Orbit launch"}}]
    )
    html = field.render("post:1")
    assert "Orbit launch" in html
    assert "or-morph-search" not in html
    assert field.get_options_for_type("post") == {}


def test_morph_to_select_falls_back_to_flat_options() -> None:
    field = MorphToSelect.make("commentable").options({"post": "Post"})
    html = field.render(None)
    assert '<option value="post"' in html and "Post" in html
    assert MorphToSelect.make("commentable").hidden().render(None) == ""


def test_morph_to_select_starts_with_type_then_record_combobox() -> None:
    field = MorphToSelect.make("owner").searchable().types(
        [
            {"type": "user", "label": "User", "options": {"1": "Ada"}},
            {"type": "team", "label": "Team", "options": {"10": "Platform"}},
        ]
    )
    empty = field.render(None)
    assert "Select type…" in empty
    assert 'value="user" selected' not in empty
    assert "or-morph-to-select__type" in empty
    assert "or-morph-record-combobox" in empty
    assert "orbitCombobox" in empty
    assert "orbitMorphToSelect" in empty
    assert 'x-show="Boolean(type)"' in empty
    assert "data-options-by-type=" in empty
    assert "or-morph-sublabel" in empty

    filled = field.render({"type": "user", "id": "1"})
    assert '<option value="user" selected>User</option>' in filled
    assert "Ada" in filled
    assert "or-select-morph-id" in filled
    assert 'data-options-limit="' in filled


# --------------------------------------------------------------------------- ModalTableSelect


def _authors() -> list[dict[str, Any]]:
    return [{"id": "1", "name": "Ada Lovelace"}, {"id": "2", "name": "Grace Hopper"}]


def test_modal_table_select_shows_the_current_record() -> None:
    field = ModalTableSelect.make("author_id").records(_authors).browse_label("Choose author")
    html = field.render("2")
    assert 'value="Grace Hopper"' in html
    assert "Choose author" in html
    assert "mountTableSelect('author_id')" in html
    assert "or-modal-backdrop" not in html


def test_modal_table_select_opens_a_searchable_picker() -> None:
    field = (
        ModalTableSelect.make("author_id")
        .records(_authors())
        .modal_heading("Pick an author")
        .title_attribute("name")
    )
    html = field.render(None, table_select={"field": "author_id", "search": "grace"})
    assert "Pick an author" in html
    assert "selectTableRecord('author_id', '2')" in html
    assert "Ada Lovelace" not in html
    assert "closeTableSelect()" in html
    assert "setTableSelectSearch('author_id', $event.target.value)" in html


def test_modal_table_select_renders_a_table_when_given_one() -> None:
    table = Table.make("authors").columns([TextColumn.make("name")])
    field = ModalTableSelect.make("author_id").table(table).records(_authors())
    html = field.render(None, table_select={"field": "author_id"})
    assert field.get_table() is table
    assert "Ada Lovelace" in html
    assert "or-table" in html


def test_modal_table_select_handles_empty_results_and_objects() -> None:
    field = ModalTableSelect.make("author_id").records([])
    html = field.render(None, table_select={"field": "author_id"})
    assert "No records." in html

    records = [SimpleNamespace(id="7", name="Katherine Johnson")]
    obj_field = ModalTableSelect.make("author_id").records(records)
    assert obj_field.get_display_value("7") == "Katherine Johnson"
    assert "Katherine Johnson" in obj_field.render(None, table_select={"field": "author_id"})


def test_modal_table_select_display_value_resolution() -> None:
    field = ModalTableSelect.make("author_id").options({"1": "From options"}).records(_authors())
    assert field.get_display_value(None) == ""
    assert field.get_display_value("1") == "From options"
    assert field.get_display_value("99") == "99"
    assert ModalTableSelect.make("author_id").disabled().render(None).count("disabled") >= 1
    assert ModalTableSelect.make("author_id").hidden().render(None) == ""


# --------------------------------------------------------------------------- host wiring


class _HostResource(Resource):
    model = type("Note", (), {})
    slug = "notes"
    records_mutable = True
    records: ClassVar[list[dict[str, Any]]] = []

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title")])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")])


def _create_host() -> CreateRecordHost:
    host = CreateRecordHost()
    host.resource = _HostResource
    host.data = {}
    return host


def test_key_value_host_methods_edit_the_dictionary() -> None:
    host = _create_host()
    host.data = {"meta": {"colour": "blue", "size": "M"}}

    host.addKeyValueRow("meta")
    assert "key1" in host.data["meta"]

    host.setKeyValueKey("meta", "colour", "shade")
    assert list(host.data["meta"]) == ["shade", "size", "key1"]
    assert host.data["meta"]["shade"] == "blue"

    host.setKeyValueValue("meta", "shade", "red")
    assert host.data["meta"]["shade"] == "red"

    host.removeKeyValueRow("meta", "size")
    assert "size" not in host.data["meta"]


def test_key_value_host_methods_ignore_impossible_edits() -> None:
    host = _create_host()
    host.data = {"meta": "not-a-dict"}
    host.removeKeyValueRow("meta", "colour")
    host.setKeyValueKey("meta", "colour", "shade")
    assert host.data["meta"] == "not-a-dict"

    host.data = {"meta": {"colour": "blue"}}
    host.setKeyValueKey("meta", "colour", "")
    host.setKeyValueKey("meta", "colour", "colour")
    host.setKeyValueKey("meta", "missing", "other")
    assert host.data["meta"] == {"colour": "blue"}

    host.data = {"meta": {"a": "1", "b": "2"}}
    host.setKeyValueKey("meta", "a", "b")
    assert host.data["meta"] == {"b": "1"}

    host.data = {}
    host.setKeyValueValue("meta", "colour", "blue")
    assert host.data["meta"] == {"colour": "blue"}


def test_morph_host_methods_swap_type_and_search() -> None:
    host = _create_host()
    host.data = {"commentable": {"type": "post", "id": "1"}}
    host.searchMorphOptions("commentable", "ada")
    assert host.morph_search == {"commentable": "ada"}

    host.setMorphType("commentable", "video")
    assert host.data["commentable"] == {"type": "video", "id": None}
    assert host.morph_search == {}

    host.data = {}
    host.setMorphType("commentable", "post")
    assert host.data["commentable"] == {"type": "post", "id": None}


def test_table_select_host_methods_drive_the_picker() -> None:
    host = _create_host()
    host.mountTableSelect("author_id")
    assert host.table_select == {"field": "author_id", "search": ""}

    host.setTableSelectSearch("author_id", "grace")
    assert host.table_select["search"] == "grace"

    host.selectTableRecord("author_id", "2")
    assert host.data["author_id"] == "2"
    assert host.table_select == {}

    host.mountTableSelect("author_id")
    host.closeTableSelect()
    assert host.table_select == {}


def test_edit_host_passes_picker_state_into_the_form() -> None:
    _HostResource.records = [{"id": "1", "title": "First note"}]
    panel = Panel.make("forms-depth").path("/admin").resources([_HostResource])
    host_cls = EditRecordHost.bind(panel=panel, resource=_HostResource)
    host = host_cls()
    host.mount(record={"id": "1", "title": "First note"})
    host.morph_search = {"commentable": "ada"}
    host.table_select = {"field": "author_id", "search": "grace"}
    html = host.render()
    assert "or-form" in html
    assert "First note" in html
