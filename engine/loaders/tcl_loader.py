# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Tcl integration utilities for the engine.
"""

import sys

import tkinter as tk

from typing import Final
from pathlib import Path

from .. import logger
from . import _ENGINE_DIR

TCL_DIR: Final[Path] = _ENGINE_DIR / "tcl"

if not TCL_DIR.exists() or not TCL_DIR.is_dir():
    logger.error("Could not find engine/tcl/ directory.")
    sys.exit(1)


def tcl_source(script_name: str, root: tk.Tk, *, dir: Path = TCL_DIR) -> None:
    """
    Run a Tcl script from engine/tcl/, or from another directory

    Args:
        script_name (str): file to source from
        root (tk.Tk): Tk instance
        dir (Path): directory holding that file, engine/tcl/ by default

    Raises:
        FileNotFoundError: If no such script exists in that directory.
        IsADirectoryError: If the path names a directory rather than a file.
    """

    script_path = dir / script_name

    if not script_path.exists():
        raise FileNotFoundError(f"Could not find Tcl file {script_path}.")

    if script_path.is_dir():
        raise IsADirectoryError(f"{script_path}: Invalid script path (Is a directory)")

    root.tk.call("source", script_path)
