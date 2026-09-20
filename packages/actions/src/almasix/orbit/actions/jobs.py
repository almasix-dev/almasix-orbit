"""In-process import / export job runner.

``ImportAction`` / ``ExportAction`` describe the job. This module actually runs it:
parse CSV or JSON, apply the column map, honour chunk size and row caps, then either
call the action's importer/exporter or a writer the host supplies.

Swap :func:`set_job_runner` if you want the same jobs on a queue; the default runner
executes inside the request.
"""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from almasix.orbit.actions.import_export import ExportAction, ImportAction


@dataclass
class ImportReport:
    """Outcome of one import job."""

    imported: int = 0
    failed: int = 0
    skipped: int = 0
    chunks: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "imported": self.imported,
            "failed": self.failed,
            "skipped": self.skipped,
            "chunks": self.chunks,
            "errors": list(self.errors),
        }


@dataclass
class ExportReport:
    """Outcome of one export job — includes the file body for download."""

    filename: str
    format: str
    rows: int
    content: str
    mime: str = "text/csv"

    def to_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "format": self.format,
            "rows": self.rows,
            "content": self.content,
            "mime": self.mime,
        }


class JobRunner(Protocol):
    """Where import/export jobs actually run."""

    def run_import(self, action: ImportAction, source: str | bytes, **kwargs: Any) -> Any: ...

    def run_export(self, action: ExportAction, records: Sequence[Any], **kwargs: Any) -> Any: ...


class ImmediateJobRunner:
    """Runs the job inside the current request — the default."""

    def run_import(self, action: ImportAction, source: str | bytes, **kwargs: Any) -> ImportReport:
        return run_import(action, source, **kwargs)

    def run_export(
        self, action: ExportAction, records: Sequence[Any], **kwargs: Any
    ) -> ExportReport:
        return run_export(action, records, **kwargs)


_runner: JobRunner = ImmediateJobRunner()


def set_job_runner(runner: JobRunner) -> None:
    """Replace the process-wide runner (queue, thread pool, …)."""
    global _runner
    _runner = runner


def get_job_runner() -> JobRunner:
    return _runner


def parse_tabular(
    source: str | bytes,
    *,
    filename: str = "",
    delimiter: str = ",",
) -> list[dict[str, Any]]:
    """Turn a CSV or JSON payload into a list of row dicts."""
    text = source.decode("utf-8-sig") if isinstance(source, (bytes, bytearray)) else str(source or "")
    text = text.strip()
    if not text:
        return []
    lowered = filename.lower()
    if lowered.endswith(".json") or text[:1] in "[{":
        data = json.loads(text)
        if isinstance(data, dict):
            data = data.get("rows") or data.get("data") or [data]
        if not isinstance(data, list):
            raise ValueError("JSON import must be a list of objects.")
        return [dict(row) if isinstance(row, dict) else {"value": row} for row in data]
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter or ",")
    return [dict(row) for row in reader]


def apply_column_map(
    rows: Sequence[MappingLike], mapping: dict[str, str] | None
) -> list[dict[str, Any]]:
    """Rename row keys using ``header → attribute`` pairs."""
    if not mapping:
        return [dict(row) for row in rows]
    out: list[dict[str, Any]] = []
    for row in rows:
        mapped: dict[str, Any] = {}
        for key, value in dict(row).items():
            mapped[mapping.get(str(key), str(key))] = value
        out.append(mapped)
    return out


MappingLike = Any


def iter_chunks(
    rows: Sequence[Any], size: int, *, max_rows: int | None = None
) -> Iterable[list[Any]]:
    """Yield row slices of ``size``, stopping at ``max_rows``."""
    limited = list(rows[: max_rows if max_rows is not None else None])
    chunk = max(1, int(size or 1))
    for start in range(0, len(limited), chunk):
        yield limited[start : start + chunk]


def serialize_tabular(
    records: Sequence[Any],
    *,
    fmt: str = "csv",
    columns: Sequence[str] | None = None,
    column_map: dict[str, str] | None = None,
) -> tuple[str, str]:
    """Return ``(body, mime)`` for CSV or JSON."""
    rows = [_record_to_dict(record) for record in records]
    keys = list(columns) if columns else _union_keys(rows)
    labels = {key: (column_map or {}).get(key, key) for key in keys}
    kind = (fmt or "csv").lower().lstrip(".")
    if kind == "json":
        payload = [{labels[key]: row.get(key, "") for key in keys} for row in rows]
        return json.dumps(payload, indent=2, default=str), "application/json"
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=[labels[key] for key in keys], extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({labels[key]: row.get(key, "") for key in keys})
    return buf.getvalue(), "text/csv"


def run_import(
    action: ImportAction,
    source: str | bytes,
    *,
    filename: str = "",
    options: dict[str, Any] | None = None,
    writer: Callable[[list[dict[str, Any]]], Any] | None = None,
) -> ImportReport:
    """Parse ``source`` and import it according to ``action``."""
    report = ImportReport()
    opts = dict(action.to_dict().get("options") or {})
    opts.update(options or {})
    delimiter = str(opts.get("delimiter") or ",")
    try:
        rows = parse_tabular(source, filename=filename, delimiter=delimiter)
    except (ValueError, json.JSONDecodeError, csv.Error) as exc:
        report.errors.append(str(exc))
        return report
    rows = apply_column_map(rows, action.get_column_map())
    importer = action.get_importer()
    for chunk in iter_chunks(rows, action.get_chunk_size(), max_rows=action.get_max_rows()):
        report.chunks += 1
        try:
            if importer is not None:
                importer(filename or "", options=opts, rows=chunk)
                report.imported += len(chunk)
            elif writer is not None:
                writer(chunk)
                report.imported += len(chunk)
            else:
                report.skipped += len(chunk)
        except Exception as exc:  # noqa: BLE001 — report per-chunk failures to the operator
            report.failed += len(chunk)
            report.errors.append(str(exc))
    return report


def run_export(
    action: ExportAction,
    records: Sequence[Any],
    *,
    fmt: str | None = None,
    options: dict[str, Any] | None = None,
) -> ExportReport:
    """Export ``records`` according to ``action``."""
    formats = list(action.to_dict().get("formats") or ["csv"])
    kind = (fmt or (formats[0] if formats else "csv")).lower().lstrip(".")
    if formats and kind not in {item.lower().lstrip(".") for item in formats}:
        kind = formats[0].lower().lstrip(".")
    exporter = action.get_exporter()
    if exporter is not None:
        result = exporter(
            records,
            format=kind,
            columns=list(action.to_dict().get("columns") or []),
            column_map=action.get_column_map(),
            options=options or {},
        )
        if isinstance(result, ExportReport):
            return result
        if isinstance(result, dict) and "content" in result:
            return ExportReport(
                filename=str(result.get("filename") or _export_filename(action, kind)),
                format=str(result.get("format") or kind),
                rows=int(result.get("rows") or len(records)),
                content=str(result["content"]),
                mime=str(result.get("mime") or _mime_for(kind)),
            )
        content = "" if result is None else str(result)
        return ExportReport(
            filename=_export_filename(action, kind),
            format=kind,
            rows=len(records),
            content=content,
            mime=_mime_for(kind),
        )
    body, mime = serialize_tabular(
        records,
        fmt=kind,
        columns=list(action.to_dict().get("columns") or []),
        column_map=action.get_column_map(),
    )
    return ExportReport(
        filename=_export_filename(action, kind),
        format=kind,
        rows=len(records),
        content=body,
        mime=mime,
    )


def _export_filename(action: ExportAction, fmt: str) -> str:
    base = action.get_filename().rstrip(".")
    suffix = fmt.lower().lstrip(".")
    if base.lower().endswith(f".{suffix}"):
        return base
    return f"{base}.{suffix}"


def _mime_for(fmt: str) -> str:
    return "application/json" if fmt.lower().lstrip(".") == "json" else "text/csv"


def _record_to_dict(record: Any) -> dict[str, Any]:
    if isinstance(record, dict):
        return dict(record)
    data = getattr(record, "__dict__", None)
    if isinstance(data, dict):
        return {key: value for key, value in data.items() if not str(key).startswith("_")}
    return {"value": record}


def _union_keys(rows: Sequence[dict[str, Any]]) -> list[str]:
    keys: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                keys.append(key)
    return keys
