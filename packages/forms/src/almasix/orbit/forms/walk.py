"""Walk nested form schemas to collect Field instances."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from almasix.orbit.support.component import Component

if TYPE_CHECKING:
    from almasix.orbit.forms.components import Field


def iter_fields(components: Sequence[Component]) -> list[Field]:
    """Depth-first collect of ``Field`` instances inside layouts / repeaters / builders."""
    from almasix.orbit.forms.components import Field

    fields: list[Field] = []
    for component in components:
        if isinstance(component, Field):
            fields.append(component)
            # Nested schemas on repeaters / builders
            nested_schema = getattr(component, "get_schema", None)
            if callable(nested_schema):
                fields.extend(iter_fields(nested_schema()))
            nested_blocks = getattr(component, "get_blocks", None)
            if callable(nested_blocks):
                for block in nested_blocks():
                    block_schema = getattr(block, "get_schema", None)
                    if callable(block_schema):
                        fields.extend(iter_fields(block_schema()))
            continue
        tabs = getattr(component, "_tabs", None)
        if isinstance(tabs, list) and tabs:
            for entry in tabs:
                comps = entry[1] if isinstance(entry, (list, tuple)) and len(entry) >= 2 else []
                fields.extend(iter_fields(list(comps)))
            continue
        steps = getattr(component, "_steps", None)
        if isinstance(steps, list) and steps:
            for entry in steps:
                comps = entry[1] if isinstance(entry, (list, tuple)) and len(entry) >= 2 else []
                fields.extend(iter_fields(list(comps)))
            continue
        children = getattr(component, "get_components", None)
        if callable(children):
            fields.extend(iter_fields(children()))
            continue
        child_components = getattr(component, "get_child_components", None)
        if callable(child_components):
            fields.extend(iter_fields(child_components()))
            continue
        schema = getattr(component, "get_schema", None)
        if callable(schema):
            fields.extend(iter_fields(schema()))
            continue
        nested = getattr(component, "_schema", None)
        if isinstance(nested, list) and nested:
            fields.extend(iter_fields(nested))
    return fields
