# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Animation handling utilities for engine entities.
"""

import bisect
import pygame

from typing import Optional


class EntityAnim:
    """
    Manage an animation for an entity.

    Stands in for EntityImage when an entity should show a moving image (GIF
    or WebP) instead of a still one. It offers the same three methods, so an
    entity holding one needs no special handling, and frames advance off the
    clock on their own: drawing it is all the caller has to do. The animation
    loops for as long as it keeps being drawn, at the pace the file asks for.
    """

    frames: list[pygame.Surface]

    def __init__(self, anim_path: str) -> None:
        """
        Initialize the EntityAnim by loading the animation at ``anim_path``.

        Args:
            anim_path (str): The path to the animation file.
        """

        self.frames = []

        self._starts: list[float] = []
        self._duration: float = 0.0
        self._started_at: int = 0

        self._scaled: Optional[pygame.Surface] = None
        self._scaled_key: Optional[tuple[int, int, int]] = None

        self.set_image(anim_path)

    def set_image(self, anim_path: str) -> None:
        """
        Load ``anim_path`` and store it as an animation.

        The animation starts over from its first frame.

        Args:
            anim_path (str): The path to the animation file.
        """

        assert pygame.get_init(), (  # nosec B101
            "EntityAnim: pygame must be initialized before loading animations"
        )

        loaded: list[tuple[pygame.Surface, float]] = pygame.image.load_animation(anim_path)

        assert loaded, f'EntityAnim: "{anim_path}" holds no frames'  # nosec B101

        self.frames = [frame.convert_alpha() for frame, _ in loaded]

        self._starts = []
        self._duration = 0.0

        for _, delay in loaded:
            self._starts.append(self._duration)
            self._duration += max(0.0, delay)

        self._started_at = pygame.time.get_ticks()

        self._scaled = None
        self._scaled_key = None

    def _current_index(self) -> int:
        """
        Work out which frame is due, from how long the animation has been running.

        Returns:
            int: Index into ``frames`` of the frame to show right now.
        """

        if self._duration <= 0.0:
            return 0

        elapsed: float = (pygame.time.get_ticks() - self._started_at) % self._duration

        return bisect.bisect_right(self._starts, elapsed) - 1

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """
        Draw the current frame of the animation scaled to ``rect`` onto ``surface``.

        Args:
            surface (pygame.Surface): surface to draw onto
            rect (pygame.Rect): rect to scale image to
        """

        assert self.frames, "EntityAnim.frames was not initialized"  # nosec B101

        index: int = self._current_index()
        key: tuple[int, int, int] = (index, rect.width, rect.height)

        if key != self._scaled_key or self._scaled is None:
            self._scaled = pygame.transform.scale(self.frames[index], (rect.width, rect.height))
            self._scaled_key = key

        surface.blit(self._scaled, (rect.x, rect.y))
