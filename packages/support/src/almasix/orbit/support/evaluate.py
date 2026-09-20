"""Evaluate static values or callables with a shared render context."""

from __future__ import annotations

import inspect
from typing import Any, TypeVar

T = TypeVar("T")


def _callable_kwargs(candidate: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """Keep only kwargs the callable accepts (utility injection)."""
    try:
        sig = inspect.signature(candidate)
    except (TypeError, ValueError):
        return ctx
    params = sig.parameters.values()
    if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params):
        return ctx
    allowed = {
        p.name
        for p in params
        if p.kind
        in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
    }
    return {key: value for key, value in ctx.items() if key in allowed}


def evaluate(candidate: T | Any, /, *args: Any, **ctx: Any) -> Any:
    """Return ``candidate`` or the result of calling it.

    Keyword utilities are filtered to parameters the callable declares, so
    ``lambda record: …`` still works when callers pass a large render context.

    Tries ``candidate(**filtered_ctx)``, then ``candidate(*args)``, then
    ``candidate(*args, **filtered_ctx)``, then ``candidate()``. If all fail,
    returns the callable unchanged (caller may treat that as invalid).
    """
    if not callable(candidate):
        return candidate
    filtered = _callable_kwargs(candidate, ctx)
    try:
        return candidate(**filtered)
    except TypeError:
        pass
    if args:
        try:
            return candidate(*args)
        except TypeError:
            pass
        try:
            return candidate(*args, **filtered)
        except TypeError:
            pass
    try:
        return candidate()
    except TypeError:
        return candidate
