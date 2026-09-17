"""Evaluate static values or callables with a shared context (Filament-style)."""

from __future__ import annotations

from typing import Any, TypeVar

T = TypeVar("T")


def evaluate(candidate: T | Any, /, *args: Any, **ctx: Any) -> Any:
    """Return ``candidate`` or the result of calling it.

    Tries ``candidate(**ctx)``, then ``candidate(*args)``, then
    ``candidate(*args, **ctx)``, then ``candidate()``. If all fail, returns
    the callable unchanged (caller may treat that as invalid).
    """
    if not callable(candidate):
        return candidate
    try:
        return candidate(**ctx)
    except TypeError:
        pass
    if args:
        try:
            return candidate(*args)
        except TypeError:
            pass
        try:
            return candidate(*args, **ctx)
        except TypeError:
            pass
    try:
        return candidate()
    except TypeError:
        return candidate
