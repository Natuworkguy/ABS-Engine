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
    Manage an animation for an :class:`~engine.core.Entity`.

    Stands in for :class:`~engine.core.image.EntityImage`
    when an entity should show a moving image (GIF or WebP)
    instead of a still one. It offers the same three methods, so an
    entity holding one needs no special handling, and frames advance off the
    clock on their own: drawing it is all the caller has to do. The animation
    loops for as long as it keeps being drawn, at the pace the file asks for.

    Pass ``loop=False`` for a one-shot animation, such as a jump: it plays
    through once, then holds its last frame and reports ``finished``, so the
    caller can swap in another animation or leave the pose standing. Calling
    ``restart`` plays it again from the top, which is how the same jump is
    re-triggered each time the entity leaves the ground.
    """

    frames: list[pygame.Surface]

    def __init__(self, anim_path: str, loop: bool = True) -> None:
        """
        Initialize the EntityAnim by loading the animation at ``anim_path``.

        Args:
            anim_path (str): The path to the animation file.
            loop (bool): Whether the animation repeats. Defaults to True.
        """

        self.frames = []
        self.loop: bool = loop

        self._starts: list[float] = []
        self._duration: float = 0.0
        self._started_at: int = 0

        self._scaled: Optional[pygame.Surface] = None
        self._scaled_key: Optional[tuple[int, int, int]] = None

        self.set_image(anim_path)

    def set_image(self, anim_path: str, loop: Optional[bool] = None) -> None:
        """
        Load ``anim_path`` and store it as an animation.

        The animation starts over from its first frame.

        Args:
            anim_path (str): The path to the animation file.
            loop (Optional[bool]): Whether the animation repeats. Keeps the
                current setting when None. Defaults to None.
        """

        assert pygame.get_init(), (  # nosec B101
            "EntityAnim: pygame must be initialized before loading animations"
        )

        loaded: list[tuple[pygame.Surface, float]] = pygame.image.load_animation(anim_path)

        assert loaded, f'EntityAnim: "{anim_path}" holds no frames'  # nosec B101

        self.frames = [frame.convert_alpha() for frame, _ in loaded]

        if loop is not None:
            self.loop = loop

        self._starts = []
        self._duration = 0.0

        for _, delay in loaded:
            self._starts.append(self._duration)
            self._duration += max(0.0, delay)

        self._started_at = pygame.time.get_ticks()

        self._scaled = None
        self._scaled_key = None

    def restart(self) -> None:
        """
        Play the animation again from its first frame.

        This is what re-triggers a one-shot animation: call it on every jump
        rather than reloading the file each time.
        """

        self._started_at = pygame.time.get_ticks()

    @property
    def finished(self) -> bool:
        """
        Whether a one-shot animation has already played through its last frame.

        A looping animation never finishes, so this is always False for one.

        Returns:
            bool: True once a non-looping animation has run its course.
        """

        if self.loop:
            return False

        if self._duration <= 0.0:
            return True

        return (pygame.time.get_ticks() - self._started_at) >= self._duration

    def _current_index(self) -> int:
        """
        Work out which frame is due, from how long the animation has been running.

        Returns:
            int: Index into ``frames`` of the frame to show right now.
        """

        if self._duration <= 0.0:
            return 0

        elapsed: float = float(pygame.time.get_ticks() - self._started_at)

        if not self.loop:
            if elapsed >= self._duration:
                return len(self.frames) - 1
        else:
            elapsed %= self._duration

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
