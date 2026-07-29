# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Utility functions for the engine.
"""

from . import Game


def get_center(game: Game) -> tuple[int, int]:
    """
    Get the center of the game window.

    Args:
        game (Game): The game instance.

    Returns:
        tuple[int, int]: The (x, y) coordinates of the center of the game window.
    """

    return (game.wsize[0] // 2, game.wsize[1] // 2)
