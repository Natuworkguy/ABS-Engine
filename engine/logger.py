# Copyright (C) Above and Below Studios
# See the LICENSE file for GPLv3

import inspect

from enum import Enum
from colorama import Fore, Style


class Status(Enum):
    CRITICAL = "Critical"
    WARNING = "Warning"
    INFO = "Info"


def _get_caller_module():
    frame = inspect.currentframe()

    while frame:
        module_name = frame.f_globals.get("__name__")

        if module_name and not module_name.endswith("logger"):
            return module_name

        frame = frame.f_back

    return "Unknown"


def logger(message: str, *, status: Status = Status.INFO) -> None:
    source = _get_caller_module().upper()

    if status == Status.CRITICAL:
        print(Fore.RED, end="")
    elif status == Status.WARNING:
        print(Fore.YELLOW, end="")

    print(f"({status}) {source}: {message}{Style.RESET_ALL}")
