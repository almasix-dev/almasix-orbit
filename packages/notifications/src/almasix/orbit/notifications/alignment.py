"""Toast alignment configuration (Filament ``Notifications`` Livewire class parity)."""

from __future__ import annotations

from enum import StrEnum
from typing import ClassVar


class Alignment(StrEnum):
    START = "start"
    CENTER = "center"
    END = "end"


class VerticalAlignment(StrEnum):
    START = "start"
    CENTER = "center"
    END = "end"


class Notifications:
    """Process-wide toast host alignment (call from a provider / middleware)."""

    _alignment: ClassVar[Alignment] = Alignment.END
    _vertical_alignment: ClassVar[VerticalAlignment] = VerticalAlignment.START

    @classmethod
    def alignment(cls, value: Alignment | str) -> None:
        cls._alignment = Alignment(str(value))

    @classmethod
    def vertical_alignment(cls, value: VerticalAlignment | str) -> None:
        cls._vertical_alignment = VerticalAlignment(str(value))

    @classmethod
    def get_alignment(cls) -> Alignment:
        return cls._alignment

    @classmethod
    def get_vertical_alignment(cls) -> VerticalAlignment:
        return cls._vertical_alignment

    @classmethod
    def reset(cls) -> None:
        cls._alignment = Alignment.END
        cls._vertical_alignment = VerticalAlignment.START

    @classmethod
    def host_classes(cls) -> str:
        return (
            f"or-notifications or-notifications-align-{cls._alignment.value} "
            f"or-notifications-valign-{cls._vertical_alignment.value}"
        )
