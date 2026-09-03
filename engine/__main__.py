# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
ABS Engine entry module.
"""

from .logger import Status, logger

package = __package__ or ""

logger(
    f"The {package} module cannot be run directly to launch the GUI. "
    f"You might be trying to run {package}.gui.",
    status=Status.CRITICAL,
)
