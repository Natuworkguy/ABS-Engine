# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Image handling utilities for engine entities.
"""

import pygame

from typing import Optional


class EntityImage:
    """
    Manage a pygame image surface for an entity.
    """

    surface: Optional[pygame.Surface]
    _scaled_surface: Optional[pygame.Surface]
    _scaled_size: tuple[int, int] | None

    def __init__(self, image_path: str) -> None:
        self.surface = None
        self._scaled_surface = None
        self._scaled_size = None
        self.set_image(image_path)

    def set_image(self, image_path: str) -> None:
        assert pygame.get_init(), (  # nosec B101
            "EntityImage: pygame must be initialized before loading images"
        )

        self.surface = pygame.image.load(image_path).convert_alpha()
        self._scaled_surface = None
        self._scaled_size = None

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        assert self.surface is not None, "EntityImage.surface was not initialized"  # nosec B101

        size = (rect.width, rect.height)
        if self._scaled_surface is None or self._scaled_size != size:
            self._scaled_surface = pygame.transform.scale(self.surface, size)
            self._scaled_size = size

        surface.blit(self._scaled_surface, (rect.x, rect.y))
