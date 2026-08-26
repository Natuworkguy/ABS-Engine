"""ABS Engine's error module."""

import faulthandler
import os
import sys

from typing import Never
from colorama import Fore, Style
from functools import partial


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
        eprint = partial(print, file=sys.stderr)

        if isatty:
            eprint(Fore.RED + Style.BRIGHT, end="")

        eprint(f"ABS Engine hit a fatal exception: \n\n{message}\nAborting.\n")

        if isatty:
            eprint(Style.RESET_ALL, end="")

        faulthandler.enable()
        os.abort()
