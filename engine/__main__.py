# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
ABS Engine entry module.
"""

from .logger import Status, logger

logger("The engine module cannot be run directly to launch the GUI. You might be trying to run engine.gui.", status=Status.CRITICAL)
