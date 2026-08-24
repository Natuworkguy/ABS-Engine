"""ABS Engine's error module."""

import faulthandler
import os
import sys

from typing import Never
from colorama import Fore, Style


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

        isatty: bool = sys.stderr.isatty()

        if isatty:
            print(Fore.RED + Style.BRIGHT, end="", file=sys.stderr)

        print(f"ABS Engine hit a fatal exception: {message}\n", file=sys.stderr)

        if isatty:
            print(Style.RESET_ALL, end="", file=sys.stderr)

        faulthandler.enable()
        os.abort()
