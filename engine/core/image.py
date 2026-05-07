# Copyright (C) Above and Below Studios
# See the LICENSE file for GPLv3

import pygame


class EntityImage:
    """Manage a pygame image surface for an entity."""

    surface: pygame.Surface

    def __init__(self, image_path: str):
        """Create an entity image by loading ``image_path``."""
        self.set_image(image_path)

    def set_image(self, image_path: str):
        """Load ``image_path`` and store it as an alpha-enabled pygame surface."""

        assert pygame.get_init(), (  # nosec B101
            "EntityImage: pygame must be initialized before loading images"
        )

        self.surface = pygame.image.load(image_path).convert_alpha()

    def draw(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw the image scaled to ``rect`` onto ``surface``."""

        assert self.surface is not None, "EntityImage.surface was not initialized"  # nosec B101

        scaled_image = pygame.transform.scale(self.surface, (rect.width, rect.height))
        surface.blit(scaled_image, (rect.x, rect.y))
