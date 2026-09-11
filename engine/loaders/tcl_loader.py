# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Tcl integration utilities for the engine.
"""

import sys

import tkinter as tk

from typing import Final
from pathlib import Path

from ..logger import logger, Status
from . import _ENGINE_DIR

TCL_DIR: Final[Path] = _ENGINE_DIR / "tcl"

if not TCL_DIR.exists() or not TCL_DIR.is_dir():
    logger("Could not find engine/tcl/ directory.", status=Status.CRITICAL)
    sys.exit(1)


def tcl_source(script_name: str, root: tk.Tk) -> None:
    """
    Run a Tcl script from engine/tcl/

    Args:
        script_name (str): file in engine/tcl/ to source from
        root (tk.Tk): Tk instance

    Raises:
        FileNotFoundError: If no such script exists under engine/tcl/.
        IsADirectoryError: If the path names a directory rather than a file.
    """

    script_path = TCL_DIR / script_name

    if not script_path.exists():
        raise FileNotFoundError(f"Could not find Tcl file {script_path}.")

    if script_path.is_dir():
        raise IsADirectoryError(f"{script_path}: Invalid script path (Is a directory)")

    root.tk.call("source", script_path)
