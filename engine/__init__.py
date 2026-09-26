# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Core engine package
"""

import os
import colorama

from .version import __version__

colorama.just_fix_windows_console()
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

__all__ = [
    "__version__"
]
