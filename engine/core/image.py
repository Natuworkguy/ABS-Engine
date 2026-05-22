# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

import pygame

from typing import Optional


class EntityImage:
    """
    Manage a pygame image surface for an entity.
    """

    surface: Optional[pygame.Surface]

    def __init__(self, image_path: str) -> None:
        """
        Initialize the EntityImage by loading the image at ``image_path``.

        Args:
            image_path (str): The path to the image file.
        """

        self.surface = None

        self.set_image(image_path)

    def set_image(self, image_path: str) -> None:
        """
        Load ``image_path`` and store it as an alpha-enabled pygame surface.

        Args:
            image_path (str): The path to the image file.
        """

        assert pygame.get_init(), (  # nosec B101
            "EntityImage: pygame must be initialized before loading images"
        )

        self.surface = pygame.image.load(image_path).convert_alpha()

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw the image scaled to ``rect`` onto ``surface``."""

        assert self.surface is not None, "EntityImage.surface was not initialized"  # nosec B101

        scaled_image = pygame.transform.scale(self.surface, (rect.width, rect.height))
        surface.blit(scaled_image, (rect.x, rect.y))
