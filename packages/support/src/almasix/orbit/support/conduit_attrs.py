"""Conduit / Livewire dual-attribute helpers.

Conduit prefers ``conduit:*`` and falls back to ``wire:*``. Emit both so
templates work with either client vocabulary.
"""

from __future__ import annotations

from almasix.orbit.support.html import e


def conduit_attr(directive: str, value: str | bool | None = True) -> str:
    """HTML attributes for one directive on both ``conduit:`` and ``wire:`` prefixes.

    Examples::

        conduit_attr("submit", "authenticate")
        # ' conduit:submit="authenticate" wire:submit="authenticate"'

        conduit_attr("model.live", "email")
        # ' conduit:model.live="email" wire:model.live="email"'
    """
    directive = directive.removeprefix("conduit:").removeprefix("wire:")
    if value is True:
        return f" conduit:{directive} wire:{directive}"
    if value is False or value is None:
        return ""
    v = e(str(value))
    return f' conduit:{directive}="{v}" wire:{directive}="{v}"'
