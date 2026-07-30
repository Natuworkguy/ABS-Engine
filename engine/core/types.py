# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""Shared type aliases for ABS Engine."""

import pygame

from typing import Protocol

from .image import EntityImage

RGBType = tuple[int, int, int]
EntityImageType = EntityImage


class EntityScript(Protocol):
    """Protocol for entity script objects."""

    def init(self) -> None: ...  # noqa: E704

    def update(self, dt: float) -> None: ...  # noqa: E704

    def event(self, event: pygame.event.Event) -> None: ...  # noqa: E704


EntityScriptType = type[EntityScript]
