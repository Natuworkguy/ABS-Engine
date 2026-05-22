# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

import os
import sys

import tkinter as tk

from typing import Final, Any
from pathlib import Path

from .logger import logger, Status

TCL_DIR: Final[Path] = Path(__file__).parent / "tcl"

if not os.path.exists(TCL_DIR) or not os.path.isdir(TCL_DIR):
    logger("Could not find engine/tcl/ directory.", status=Status.CRITICAL)
    sys.exit(1)


def tcl_source(script_name: str, root: tk.Tk) -> Any:
    """Run a Tcl script from engine/tcl/"""

    script_path = str(TCL_DIR / script_name)

    if not os.path.exists(script_path) or not os.path.isfile(script_path):
        logger(f"Could not find Tcl file {script_path}.", status=Status.CRITICAL)
        sys.exit(1)

    return root.tk.call("source", script_path)


def tcl_eval(tcl: str, root: tk.Tk) -> Any:
    """Evaluate a Tcl statement"""

    return root.tk.eval(tcl)


def tcl_call_procedure(procedure_name: str, *args: Any, root: tk.Tk) -> Any:
    """
    Call a Tcl procedure with arguments and return result

    Example:
        result = tcl_call_procedure("show_info", "Title", "Message", root=tk_root)
    """

    return root.tk.call(procedure_name, *args)
