# Copyright (C) Above and Below Studios
# See the LICENSE file for GPLv3

import os
import sys

import tkinter as tk

from typing import Final
from pathlib import Path

from .logger import logger, Status

TCL_DIR: Final[Path] = Path(__file__).parent / "tcl"

if not os.path.exists(TCL_DIR) or not os.path.isdir(TCL_DIR):
    logger("Could not find engine/tcl/ directory.", status=Status.CRITICAL)
    sys.exit(1)


def _no_root() -> None:
    raise ValueError("Engine must provide root")


def tcl_source(script_name: str, root: tk.Tk) -> str:
    """Run a Tcl script from engine/tcl/"""

    if root is None:
        _no_root()

    script_path = str(TCL_DIR / script_name)

    if not os.path.exists(script_path) or not os.path.isfile(script_path):
        logger(f"Could not find Tcl file {script_path}.", status=Status.CRITICAL)
        sys.exit(1)

    return root.tk.call("source", script_path)


def tcl_eval(tcl: str, root: tk.Tk) -> str:
    """Evaluate a Tcl statement"""

    if root is None:
        _no_root()

    return root.tk.eval(tcl)


def tcl_call_procedure(procedure_name: str, *args, root: tk.Tk) -> str:
    """
    Call a Tcl procedure with arguments and return result

    Example:
        result = tcl_call_procedure("show_info", "Title", "Message", root=tk_root)
    """

    if root is None:
        _no_root()

    return root.tk.call(procedure_name, *args)
