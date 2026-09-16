"""Parity matrix doc smoke tests."""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_CANDIDATES = [
    _ROOT / "docs" / "parity.md",
    _ROOT / "packages" / ".." / "docs" / "parity.md",
]


def _load_parity() -> str:
    for path in _CANDIDATES:
        resolved = path.resolve()
        if resolved.is_file():
            return resolved.read_text(encoding="utf-8")
    raise AssertionError(f"parity.md not found in {_CANDIDATES}")


def test_parity_matrix_lists_filament_packages() -> None:
    text = _load_parity().lower()
    required = [
        "support",
        "schemas",
        "forms",
        "tables",
        "actions",
        "infolists",
        "notifications",
        "widgets",
        "query-builder",
        "panels",
        "resources",
        "pages",
        "relation",
        "textinput",
        "select",
        "repeater",
        "done",
    ]
    for key in required:
        assert key in text, f"Expected {key!r} in parity.md"
