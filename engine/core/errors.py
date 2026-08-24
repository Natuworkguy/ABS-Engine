"""ABS Engine's error module."""

import faulthandler
import os

from typing import Never


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

        print(f"ABS Engine hit a fatal exception: {message}\n")

        faulthandler.enable()
        os.abort()
        faulthandler.disable()
