"""Table enums (Filament ``Tables\\Enums`` parity)."""

from __future__ import annotations

from enum import StrEnum


class PaginationMode(StrEnum):
    """How pagination chrome behaves (cursor is decorative for in-memory tables)."""

    DEFAULT = "default"
    SIMPLE = "simple"
    CURSOR = "cursor"
