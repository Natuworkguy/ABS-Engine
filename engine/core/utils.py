# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Utility functions for the engine.
"""

from typing import TYPE_CHECKING
from functools import partial

from .. import logger
from ..loaders.c_loader import c_source
from ..loaders.nut_loader import nut_source, nut_call_function

if TYPE_CHECKING:
    from . import Game

try:
    _clamp = c_source("mathutil.c").clamp
except Exception as e:
    logger.warning(f'{e.__class__.__name__} when loading mathutil.c: "{e!s}"')
    nut_source("mathutil.nut")
    _clamp = partial(nut_call_function, "clamp")


def get_center(game: "Game") -> tuple[float, float]:
    """
    Get the center of the game window.

    Args:
        game (Game): The game instance.

    Returns:
        tuple[float, float]: The (x, y) coordinates of the center of the game window.
    """

    return (game.wsize[0] // 2, game.wsize[1] // 2)


def clamp(value: float, low: float, high: float) -> float:
    """
    Keep a number inside a range.

    Useful for holding an entity on screen, or keeping a color channel
    between 0 and 255.

    *Implemented in C*

    Args:
        value (float): The number to limit.
        low (float): Smallest value allowed.
        high (float): Largest value allowed.

    Returns:
        float: The number, or low or high if it fell outside them.
    """

    return float(_clamp(value, low, high))
