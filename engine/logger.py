# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Logging utilities for the engine.
"""

import inspect

from enum import Enum
from typing import Any
from colorama import Fore, Style


class Status(Enum):
    """
    Log severity levels used by the logger.
    """

    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


def _get_caller_module() -> Any:
    """
    Get the name of the module of the function that called the logger.

    Returns:
        Any: The name of the module
    """
    frame = inspect.currentframe()

    while frame:
        module_name = frame.f_globals.get("__name__")

        if module_name and not module_name.endswith("logger"):
            return module_name

        frame = frame.f_back

    return "Unknown"


def logger(message: str, *, status: Status = Status.INFO) -> None:
    """
    Log a message to the console

    Args:
        message (str): Message to log.
        status (Status): Log severity level. Defaults to Status.INFO.
    """

    source = _get_caller_module().upper()

    if status == Status.CRITICAL:
        print(Fore.RED, end="")
    elif status == Status.WARNING:
        print(Fore.YELLOW, end="")

    print(f"({status.value}) {source}: {message}{Style.RESET_ALL}")
