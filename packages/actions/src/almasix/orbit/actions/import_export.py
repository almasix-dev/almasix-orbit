"""Import / export action helpers.

``ImportAction`` / ``ExportAction`` hold the job config (file types, column map,
chunk size, filename). The default :class:`~almasix.orbit.actions.jobs.ImmediateJobRunner`
parses CSV/JSON and writes rows inside the request. Swap
:func:`~almasix.orbit.actions.jobs.set_job_runner` to run the same jobs on a queue.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any, Self

from almasix.orbit.actions.action import Action
from almasix.orbit.support.component import Component
from almasix.orbit.support.evaluate import evaluate
from almasix.orbit.support.html import e


class Importer:
    """Optional per-chunk hook — the default runner calls this with ``rows=``."""

    def __call__(
        self, path: str, *, options: dict[str, Any] | None = None, **kwargs: Any
    ) -> Any:
        raise NotImplementedError("Implement Importer.__call__ or pass a callable.")


class Exporter:
    """Optional export hook — return CSV/JSON text, a dict, or an ``ExportReport``."""

    def __call__(self, records: Sequence[Any] | None = None, **kwargs: Any) -> Any:
        raise NotImplementedError("Implement Exporter.__call__ or pass a callable.")

class ImportAction(Action):
    """Import records from an uploaded file (CSV/JSON by default)."""

    def __init__(self, name: str | None = "import") -> None:
        super().__init__(name)
        self.label("Import").icon("heroicon-o-arrow-up-tray").color("gray")
        self._modal = True
        self._importer: Callable[..., Any] | None = None
        self._accepted_types: list[str] = [".csv", ".json"]
        self._options: dict[str, Any] = {}
        self._options_form: list[Component] = []
        self._column_map: dict[str, str] = {}
        self._chunk_size: int = 500
        self._max_rows: int | None = None

    def importer(self, callback: Callable[..., Any]) -> Self:
        self._importer = callback
        return self

    def get_importer(self) -> Callable[..., Any] | None:
        return self._importer

    def accepted_file_types(self, types: Sequence[str]) -> Self:
        self._accepted_types = list(types)
        return self

    def options(self, opts: dict[str, Any]) -> Self:
        self._options.update(opts)
        return self

    def options_form(self, schema: Sequence[Component]) -> Self:
        """Extra modal fields merged into the import form."""
        self._options_form = list(schema)
        # Merge into the action form surface so the modal host embeds fields.
        existing = list(self._form_schema)
        self._form_schema = existing + list(schema)
        return self

    def get_options_form(self) -> list[Component]:
        return list(self._options_form)

    def column_map(self, mapping: Mapping[str, str]) -> Self:
        self._column_map = dict(mapping)
        return self

    def get_column_map(self) -> dict[str, str]:
        return dict(self._column_map)

    def chunk_size(self, size: int) -> Self:
        self._chunk_size = size
        return self

    def get_chunk_size(self) -> int:
        return self._chunk_size

    def max_rows(self, limit: int | None) -> Self:
        self._max_rows = limit
        return self

    def get_max_rows(self) -> int | None:
        return self._max_rows

    def call(self, *args: Any, **kwargs: Any) -> Any:
        if self._using is not None or self._action is not None:
            return super().call(*args, **kwargs)
        if self._importer is not None:
            self._halted = False
            self._cancelled = False
            if self._before is not None:
                self._before(*args, **kwargs)
            if self._halted or self._cancelled:
                return None
            result = self._importer(*args, **kwargs)
            if not (self._halted or self._cancelled) and self._after is not None:
                self._after(*args, **kwargs)
            return result
        return None

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "accepted_file_types": list(self._accepted_types),
                "options": dict(self._options),
                "has_options_form": bool(self._options_form),
                "column_map": dict(self._column_map),
                "chunk_size": self._chunk_size,
                "max_rows": self._max_rows,
                "has_importer": self._importer is not None,
            }
        )
        return d

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx) or not self.can(**ctx):
            return ""
        base = super().render(state, **ctx)
        types = ",".join(self._accepted_types)
        return base.replace(
            "data-action=",
            f'data-import="true" data-accept="{e(types)}" data-action=',
            1,
        )


class ExportAction(Action):
    """Export table / query results to a downloadable file."""

    def __init__(self, name: str | None = "export") -> None:
        super().__init__(name)
        self.label("Export").icon("heroicon-o-arrow-down-tray").color("gray")
        self._exporter: Callable[..., Any] | None = None
        self._formats: list[str] = ["csv", "json"]
        self._columns: list[str] = []
        self._column_map: dict[str, str] = {}
        self._chunk_size: int = 500
        self._max_rows: int | None = None
        self._filename: str | Callable[..., str] = "export"

    def exporter(self, callback: Callable[..., Any]) -> Self:
        self._exporter = callback
        return self

    def get_exporter(self) -> Callable[..., Any] | None:
        return self._exporter

    def formats(self, values: Sequence[str]) -> Self:
        self._formats = list(values)
        return self

    def columns(self, names: Sequence[str]) -> Self:
        self._columns = list(names)
        return self

    def column_map(self, mapping: Mapping[str, str]) -> Self:
        self._column_map = dict(mapping)
        return self

    def get_column_map(self) -> dict[str, str]:
        return dict(self._column_map)

    def chunk_size(self, size: int) -> Self:
        self._chunk_size = size
        return self

    def get_chunk_size(self) -> int:
        return self._chunk_size

    def max_rows(self, limit: int | None) -> Self:
        self._max_rows = limit
        return self

    def get_max_rows(self) -> int | None:
        return self._max_rows

    def filename(self, name: str | Callable[..., str]) -> Self:
        self._filename = name
        return self

    def get_filename(self, **ctx: Any) -> str:
        result = evaluate(self._filename, **ctx)
        return "export" if result is None else str(result)

    def call(self, *args: Any, **kwargs: Any) -> Any:
        if self._using is not None or self._action is not None:
            return super().call(*args, **kwargs)
        if self._exporter is not None:
            self._halted = False
            self._cancelled = False
            if self._before is not None:
                self._before(*args, **kwargs)
            if self._halted or self._cancelled:
                return None
            result = self._exporter(*args, **kwargs)
            if not (self._halted or self._cancelled) and self._after is not None:
                self._after(*args, **kwargs)
            return result
        return None

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "formats": list(self._formats),
                "columns": list(self._columns),
                "column_map": dict(self._column_map),
                "chunk_size": self._chunk_size,
                "max_rows": self._max_rows,
                "filename": self._filename if not callable(self._filename) else None,
                "has_exporter": self._exporter is not None,
            }
        )
        return d

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx) or not self.can(**ctx):
            return ""
        base = super().render(state, **ctx)
        formats = ",".join(self._formats)
        return base.replace(
            "data-action=",
            f'data-export="true" data-formats="{e(formats)}" data-action=',
            1,
        )
