# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Background music playback for the engine.
"""

import os

import pygame

from typing import Optional

from ..logger import logger, Status as LoggerStatus


class Music:
    """
    Plays one background track at a time.

    Every game owns one of these as ``game.music``. A machine without a working
    audio device leaves it unavailable rather than failing: nothing plays, but
    the game still runs and every method here stays safe to call.
    """

    def __init__(self, base_path: str) -> None:
        """
        Open the mixer, if this machine has an audio device to open.

        Args:
            base_path (str): Project root that track paths are given relative to.
        """

        self.base_path: str = base_path
        self.available: bool = True

        self.track: Optional[str] = None

        self._volume: float = 1.0
        self._paused: bool = False

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
        except pygame.error as e:
            self.available = False
            logger(f"No audio device available, music is off: {e}", status=LoggerStatus.WARNING)

    def play(self, track: str, *, loops: int = -1, fade_ms: int = 0) -> None:
        """
        Start a track, replacing whatever was playing.

        Args:
            track (str): Path to an audio file, relative to the project root.
            loops (int): Extra times to repeat it. -1 repeats forever. Defaults to -1.
            fade_ms (int): Milliseconds to fade in over. Defaults to 0.
        """

        if not self.available:
            return

        try:
            pygame.mixer.music.load(os.path.join(self.base_path, track))
        except (pygame.error, FileNotFoundError) as e:
            logger(f'Could not load music "{track}": {e}', status=LoggerStatus.WARNING)
            return

        self.track = track
        self._paused = False

        pygame.mixer.music.set_volume(self._volume)
        pygame.mixer.music.play(loops, fade_ms=fade_ms)

    def stop(self, *, fade_ms: int = 0) -> None:
        """
        Stop the current track and forget it.

        Args:
            fade_ms (int): Milliseconds to fade out over. Defaults to 0.
        """

        if not self.available:
            return

        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()

        self.track = None
        self._paused = False

    def pause(self) -> None:
        """
        Hold the current track where it is. Resuming picks it up from there.
        """

        if not self.available or self._paused:
            return

        pygame.mixer.music.pause()
        self._paused = True

    def resume(self) -> None:
        """
        Carry on with a paused track.
        """

        if not self.available or not self._paused:
            return

        pygame.mixer.music.unpause()
        self._paused = False

    def set_volume(self, volume: float) -> None:
        """
        Set how loud music plays, now and for tracks played later.

        Args:
            volume (float): Loudness from 0.0 to 1.0. Values outside are clamped.
        """

        self._volume = max(0.0, min(1.0, float(volume)))

        if self.available:
            pygame.mixer.music.set_volume(self._volume)

    def get_volume(self) -> float:
        """
        Get how loud music is set to play.

        Returns:
            float: Loudness from 0.0 to 1.0.
        """

        return self._volume

    def is_playing(self) -> bool:
        """
        Check whether a track is audible right now.

        A paused track is not playing, though the mixer still holds it.

        Returns:
            bool: True if a track is currently being heard.
        """

        return self.available and not self._paused and pygame.mixer.music.get_busy()
