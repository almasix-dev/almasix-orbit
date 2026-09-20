"""Import / export in-process job runner."""

from __future__ import annotations

from typing import Any, ClassVar

import pytest
from almasix.orbit.actions import (
    ExportAction,
    ExportReport,
    ImmediateJobRunner,
    ImportAction,
    ImportReport,
    get_job_runner,
    run_export,
    run_import,
    set_job_runner,
)
from almasix.orbit.actions.jobs import (
    JobRunner,
    apply_column_map,
    iter_chunks,
    parse_tabular,
    serialize_tabular,
)
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.panels.conduit.hosts import ListRecordsHost
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.tables import Table, TextColumn


@pytest.fixture(autouse=True)
def restore_runner() -> Any:
    original = get_job_runner()
    yield
    set_job_runner(original)


def test_parse_tabular_handles_csv_json_and_empty() -> None:
    csv_rows = parse_tabular("Title,Status\nHello,draft\n", filename="posts.csv")
    assert csv_rows == [{"Title": "Hello", "Status": "draft"}]
    json_rows = parse_tabular('[{"title": "A"}]', filename="posts.json")
    assert json_rows == [{"title": "A"}]
    wrapped = parse_tabular('{"rows": [{"title": "B"}]}', filename="posts.json")
    assert wrapped == [{"title": "B"}]
    scalar = parse_tabular('{"data": [1, 2]}', filename="n.json")
    assert scalar == [{"value": 1}, {"value": 2}]
    assert parse_tabular("", filename="empty.csv") == []
    assert parse_tabular(b"\xef\xbb\xbfname\nAda\n", filename="people.csv") == [{"name": "Ada"}]


def test_parse_tabular_rejects_non_list_json() -> None:
    with pytest.raises(ValueError, match="list of objects"):
        parse_tabular('"just a string"', filename="bad.json")


def test_column_map_and_chunks() -> None:
    mapped = apply_column_map(
        [{"Title": "Hi", "Status": "draft"}], {"Title": "title", "Status": "status"}
    )
    assert mapped == [{"title": "Hi", "status": "draft"}]
    assert apply_column_map([{"a": 1}], None) == [{"a": 1}]
    chunks = list(iter_chunks(list(range(5)), 2, max_rows=3))
    assert chunks == [[0, 1], [2]]
    assert list(iter_chunks([1, 2], 0)) == [[1], [2]]


def test_serialize_tabular_csv_and_json() -> None:
    records = [{"id": 1, "title": "Hi"}, {"id": 2, "title": "Bye", "extra": "x"}]
    csv_body, csv_mime = serialize_tabular(
        records, fmt="csv", columns=["id", "title"], column_map={"title": "Title"}
    )
    assert csv_mime == "text/csv"
    assert "Title" in csv_body
    json_body, json_mime = serialize_tabular(records, fmt="json")
    assert json_mime == "application/json"
    assert '"extra"' in json_body


def test_run_import_with_writer_and_importer() -> None:
    written: list[dict[str, Any]] = []
    action = ImportAction.make().column_map({"Title": "title"}).chunk_size(1).max_rows(2)
    report = run_import(
        action,
        "Title\nA\nB\nC\n",
        filename="posts.csv",
        writer=lambda chunk: written.extend(chunk),
    )
    assert report.imported == 2
    assert report.chunks == 2
    assert written == [{"title": "A"}, {"title": "B"}]

    seen: list[int] = []

    def importer(path: str, *, options=None, rows=None, **_: Any) -> None:
        seen.append(len(rows or []))

    counted = run_import(
        ImportAction.make().importer(importer).chunk_size(10),
        '[{"n": 1}, {"n": 2}]',
        filename="n.json",
    )
    assert counted.imported == 2
    assert seen == [2]

    skipped = run_import(ImportAction.make(), "a\n1\n")
    assert skipped.skipped == 1
    assert skipped.imported == 0


def test_run_import_reports_parse_and_chunk_failures() -> None:
    bad = run_import(ImportAction.make(), "{not json", filename="x.json")
    assert bad.errors and bad.imported == 0

    def boom(*_a: Any, **_k: Any) -> None:
        raise RuntimeError("nope")

    failed = run_import(
        ImportAction.make().importer(boom),
        "title\nA\n",
        filename="x.csv",
    )
    assert failed.failed == 1
    assert "nope" in failed.errors[0]


def test_run_export_default_and_custom_exporter() -> None:
    action = (
        ExportAction.make()
        .formats(["csv", "json"])
        .columns(["title"])
        .column_map({"title": "Title"})
        .filename("posts")
    )
    csv_report = run_export(action, [{"title": "Hi"}], fmt="csv")
    assert csv_report.filename == "posts.csv"
    assert csv_report.rows == 1
    assert "Title" in csv_report.content

    json_report = run_export(action, [{"title": "Hi"}], fmt="json")
    assert json_report.mime == "application/json"

    unknown = run_export(action, [{"title": "Hi"}], fmt="xlsx")
    assert unknown.format == "csv"

    def exp_report(records: Any, **_: Any) -> ExportReport:
        return ExportReport(
            filename="x.json", format="json", rows=0, content="[]", mime="application/json"
        )

    assert run_export(ExportAction.make().exporter(exp_report), []).filename == "x.json"

    def exp_dict(records: Any, **_: Any) -> dict[str, Any]:
        return {"content": "a,b", "filename": "out.csv", "rows": 3}

    dicted = run_export(ExportAction.make().exporter(exp_dict), [])
    assert dicted.content == "a,b" and dicted.rows == 3

    def exp_text(records: Any, **_: Any) -> str:
        return "raw"

    assert run_export(ExportAction.make().exporter(exp_text).filename("file.csv"), []).content == "raw"

    def exp_none(records: Any, **_: Any) -> None:
        return None

    empty = run_export(ExportAction.make().exporter(exp_none), [1])
    assert empty.content == "" and empty.rows == 1

    obj = type("Row", (), {"title": "Obj"})()
    body, _mime = serialize_tabular([obj, "x"])
    assert "title" in body or "value" in body


def test_job_runner_swap_and_reports() -> None:
    class QueueRunner:
        def run_import(self, action: Any, source: Any, **kwargs: Any) -> dict[str, Any]:
            return ImportReport(imported=9).to_dict()

        def run_export(self, action: Any, records: Any, **kwargs: Any) -> dict[str, Any]:
            return {
                "filename": "q.csv",
                "format": "csv",
                "rows": 0,
                "content": "",
                "mime": "text/csv",
            }

    set_job_runner(QueueRunner())
    assert get_job_runner().run_import(ImportAction.make(), "")["imported"] == 9
    set_job_runner(ImmediateJobRunner())
    assert isinstance(get_job_runner().run_export(ExportAction.make(), []), ExportReport)
    assert ImportReport().to_dict()["errors"] == []
    assert JobRunner.run_import(get_job_runner(), ImportAction.make(), "") is None
    assert JobRunner.run_export(get_job_runner(), ExportAction.make(), []) is None


class _TradeResource(Resource):
    model = type("Trade", (), {})
    slug = "trades"
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
        return table.columns([TextColumn.make("title")]).header_actions(
            [
                ImportAction.make().column_map({"Title": "title"}),
                ExportAction.make().columns(["title"]).filename("trades"),
            ]
        )


class _BrokenTableResource(Resource):
    model = type("Broken", (), {})
    slug = "broken"
    records: ClassVar[list[dict[str, Any]]] = []

    @classmethod
    def get_table(cls) -> Table:
        raise RuntimeError("no table")

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title")])


class _NoGetTableResource(Resource):
    model = type("Nope", (), {})
    slug = "nope"
    get_table = None  # type: ignore[assignment]

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title")])


def _list_host(resource: type[Resource]) -> ListRecordsHost:
    host_cls = ListRecordsHost.bind(panel=Panel.make("jobs").path("/admin"), resource=resource)
    host = host_cls()
    host.mount()
    return host


def test_list_host_imports_and_exports_records() -> None:
    _TradeResource.records = [{"id": "1", "title": "Seed"}]
    host = _list_host(_TradeResource)
    imported = host.mountAction("import", payload={"content": "Title\nNew\n", "filename": "t.csv"})
    assert imported["imported"] == 1
    assert any(r.get("title") == "New" for r in host.records)

    exported = host.mountAction("export", payload={"format": "csv"})
    assert exported["filename"] == "trades.csv"
    assert "New" in exported["content"]

    again = host.runImport({"content": "Title\nThird\n"})
    assert again["imported"] == 1


class _OtherHeaderResource(Resource):
    model = type("Other", (), {})
    slug = "other-header"
    records_mutable = True
    records: ClassVar[list[dict[str, Any]]] = [{"id": "abc", "title": "Odd"}]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title")])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")]).header_actions(
            [ImportAction.make("other").label("Other")]
        )


def test_list_host_skips_unmatched_header_actions_and_non_numeric_ids() -> None:
    _OtherHeaderResource.records = [{"id": "abc", "title": "Odd"}]
    host = _list_host(_OtherHeaderResource)
    assert host._header_action("import") is None
    imported = host.runImport({"content": "title\nZed\n"})
    assert imported["imported"] == 1
    assert any(r.get("title") == "Zed" for r in host.records)
    host_cls = ListRecordsHost.bind(
        panel=Panel.make("jobs-broken").path("/admin"), resource=_BrokenTableResource
    )
    host = host_cls()
    host.records = [{"id": "1", "title": "A"}]
    assert host._header_action("import") is None
    exported = host.runExport("not-a-dict")
    assert exported["rows"] == 1
    imported = host.runImport("not-a-dict")
    assert imported["imported"] == 0
    host_cls = ListRecordsHost.bind(
        panel=Panel.make("jobs-notable").path("/admin"), resource=_NoGetTableResource
    )
    assert host_cls()._header_action("import") is None
