# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Logging utilities for the engine.

Import the module and call the function for the level you need:

    from engine import logger

    logger.info("Initialized game")
    logger.warning("Save file was not found")
    logger.critical("Could not load icon image.")
"""

from typing import TextIO, Optional

import inspect
import sys
import time

from colorama import Fore, Style

_LONGEST_LEVEL_WIDTH = 8


def _get_caller_module() -> str:
    """
    Get the name of the first module outside of this one in the call stack.

    Returns:
        str: The name of the module, or "unknown" if it cannot be determined.
    """
    frame = inspect.currentframe()

    while frame:
        module_name = frame.f_globals.get("__name__")

        if isinstance(module_name, str) and module_name != __name__:
            return module_name

        frame = frame.f_back

    return "unknown"


def _log(level: str, color: str, message: str, file: Optional[TextIO]) -> None:
    """
    Write a formatted log line to the console.

    Args:
        level (str): Level name shown in the log line.
        color (str): Color of the level name when writing to a terminal.
        message (str): Message to log.
    """

    if file is None:
        return

    timestamp = time.strftime("%H:%M:%S")
    level = level.ljust(_LONGEST_LEVEL_WIDTH)
    source = _get_caller_module()

    if file.isatty():
        timestamp = f"{Style.DIM}{timestamp}{Style.RESET_ALL}"
        level = f"{color}{level}{Style.RESET_ALL}"
        source = f"{Style.DIM}{source}{Style.RESET_ALL}"

    print(f"{timestamp} {level} {source}: {message}", file=file)


def info(message: str, file: Optional[TextIO] = None) -> None:
    """
    Log a normal message.

    Args:
        message (str): Message to log.
    """
    _log("INFO", Fore.CYAN, message, file if file is not None else sys.stdout)


def warning(message: str, file: Optional[TextIO] = None) -> None:
    """
    Log a problem that can be recovered from.

    Args:
        message (str): Message to log.
    """
    _log("WARNING", Fore.YELLOW, message, file if file is not None else sys.stderr)


def critical(message: str, file: Optional[TextIO] = None) -> None:
    """
    Log an error that should be handled immediately.

    Args:
        message (str): Message to log.
    """
    _log(
        "CRITICAL",
        Style.BRIGHT + Fore.RED,
        message,
        file if file is not None else sys.stderr,
    )
