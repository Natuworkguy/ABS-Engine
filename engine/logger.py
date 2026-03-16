# Copyright (C) Above and Below Studios
# See the LICENSE file for GPLv3

from enum import Enum
from typing import Literal

class Status:
    CRITICAL = "Critical"
    WARNING = "Warning"
    INFO = "Info"

def logger(source: str, message: str, *, status: Literal["Critical", "Warning", "Info"] = Status.INFO) -> None:
    print(f"({status}) {source}: {message}")
