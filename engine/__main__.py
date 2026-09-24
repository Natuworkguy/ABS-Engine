# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
ABS Engine entry module.
"""

from . import logger

package = __package__ or "engine"

logger.critical(
    f"The {package} module cannot be run directly to launch the GUI. "
    f"You might be trying to run {package}.gui."
)
