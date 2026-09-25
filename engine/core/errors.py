# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""ABS Engine's error module."""

import faulthandler
import os
import sys
import dis

from typing import Never
from types import FrameType

from .. import logger


class ABSFatalError(RuntimeError):
    """
    An unrecoverable ABS Engine error. Cannot be caught or handled.

    Instantiating this logs the error, dumps a traceback, and immediately
    aborts the process. Nothing after it runs, do all cleanup first.
    """

    def __init__(self, message: str) -> Never:
        """
        Log, dump traceback, and abort. This does not return.

        Args:
            message (str): What went wrong.
        """

        super().__init__(message)

        logger.critical(f"ABS Engine hit a fatal error: {message}")

        frame: FrameType = sys._getframe(1)

        print(f"\nIn {frame.f_globals.get('__file__') or '<Unknown>'}:", file=sys.stderr)
        dis.disassemble(frame.f_code, frame.f_lasti, file=sys.stderr)
        print(file=sys.stderr)

        faulthandler.enable()
        os.abort()
