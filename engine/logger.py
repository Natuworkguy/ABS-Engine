# Copyright (C) Above and Below Studios
# See the LICENSE file for GPLv3

from enum import Enum
from colorama import Fore, Style

class Status(Enum):
    CRITICAL = "Critical"
    WARNING = "Warning"
    INFO = "Info"

def logger(source: str, message: str, *, status: Status = Status.INFO) -> None:
    if status == Status.CRITICAL:
        print(Fore.RED)
    elif status == Status.WARNING:
        print(Fore.YELLOW)

    print(f"({status}) {source}: {message}")
    print(Style.RESET_ALL)
