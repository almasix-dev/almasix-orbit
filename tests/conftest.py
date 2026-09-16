"""Pytest fixtures and path bootstrap for the Orbit monorepo."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_PACKAGE_SRC = [
    _ROOT / "packages" / "support" / "src",
    _ROOT / "packages" / "schemas" / "src",
    _ROOT / "packages" / "forms" / "src",
    _ROOT / "packages" / "tables" / "src",
    _ROOT / "packages" / "actions" / "src",
    _ROOT / "packages" / "infolists" / "src",
    _ROOT / "packages" / "notifications" / "src",
    _ROOT / "packages" / "widgets" / "src",
    _ROOT / "packages" / "query-builder" / "src",
    _ROOT / "packages" / "panels" / "src",
]

for _src in _PACKAGE_SRC:
    s = str(_src)
    if _src.is_dir() and s not in sys.path:
        sys.path.insert(0, s)


class User:
    """Simple auth stub with permissions and admin flag."""

    def __init__(
        self,
        *,
        permissions: set[str] | list[str] | None = None,
        is_admin: bool = False,
    ) -> None:
        self.permissions: set[str] = set(permissions or [])
        self.is_admin = is_admin

    def can(self, ability: str, record=None) -> bool:  # noqa: ANN001
        if self.is_admin or "*" in self.permissions:
            return True
        return ability in self.permissions
