# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Text entity for rendering strings in the engine.
"""

import pygame

from typing import Optional

from . import Entity
from .types import RGBType


class Text(Entity):
    """
    An entity that renders a string of text.
    """

    def __init__(
        self,
        text: str = "",
        x: float = 0,
        y: float = 0,
        size: int = 50,
        font: Optional[str] = None,
        color: RGBType = (255, 255, 255),
        bgcolor: RGBType = (0, 0, 0),
        antialias: bool = True,
        dynamic: bool = True,
    ) -> None:
        """
        Initialize a text entity.

        Text entities behave like any other entity, but they render a string of text instead of an image or colored box.

        Args:
            text (str): The string to render. Defaults to "".
            x (float): X position. Defaults to 0.
            y (float): Y position. Defaults to 0.
            size (int): Font size in points. Defaults to 50.
            font (Optional[str]): Path to a font file. Defaults to None (pygame's
                default font). If the file cannot be found, Text falls back to
                pygame's system-font lookup with the same name.
            color (RGBType): RGB color of the text. Defaults to (255, 255, 255).
            bgcolor (RGBType): RGB background color behind the text. Defaults to (0, 0, 0).
            antialias (bool): Whether to render the text with antialiasing. Defaults to True.
            dynamic (bool): Whether to rebuild the text surface every frame so it
                tracks changes to text/color/position. Set to False for static text
                to avoid the per-frame re-render cost. Defaults to True.
        """

        self.text: str = text
        self.x: float = x
        self.y: float = y
        self.color: RGBType = color
        self.bgcolor: RGBType = bgcolor
        self.antialias: bool = antialias
        self.dynamic: bool = dynamic

        try:
            self.font = pygame.font.Font(font, size)
        except FileNotFoundError:
            self.font = pygame.font.SysFont(font, size)

        self._update_text_surface()

        super().__init__(x, y, width=self.text_rect.width, height=self.text_rect.height)

    def _update_text_surface(self) -> None:
        """
        Rebuild the rendered text surface and rect from the entity's current
        text, color, bgcolor, antialias, and position.
        """

        self.text_surface = self.font.render(self.text, self.antialias, self.color, self.bgcolor)
        self.text_rect = self.text_surface.get_rect(x=self.x, y=self.y)

    def center(self, pos: tuple[float, float]) -> None:
        """
        Center the text on a position and rebuild its rendered surface.

        Args:
            pos (tuple[float, float]): The (x, y) point to center the text on.
        """

        super().center(pos)
        self._update_text_surface()

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the rendered text onto the given surface.

        Args:
            surface (pygame.Surface): The surface to draw the text on.
        """

        if self.visible:
            if self.dynamic:
                self._update_text_surface()

            surface.blit(self.text_surface, self.text_rect)
