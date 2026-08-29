# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Tcl integration utilities for the engine.
"""

import os
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
    """

    script_path = str(TCL_DIR / script_name)

    if not os.path.exists(script_path) or not os.path.isfile(script_path):
        logger(f"Could not find Tcl file {script_path}.", status=Status.CRITICAL)
        sys.exit(1)

    root.tk.call("source", script_path)
