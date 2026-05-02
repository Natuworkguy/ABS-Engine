# Copyright (C) Above and Below Studios
# See the LICENSE file for GPLv3

import os
import sys

import tkinter as tk

from pathlib import Path

from .logger import logger, Status

TCL_DIR = Path(__file__).parent / "tcl"

if not os.path.exists(TCL_DIR) or not os.path.isdir(TCL_DIR):
    logger("Could not find engine/tcl/ directory.", status=Status.CRITICAL)
    sys.exit(1)


def tcl_source(script_name: str, root: tk.Tk) -> str:
    """Run a Tcl script from engine/tcl/"""

    assert root is not None, "Engine must provide root"

    script_path = str(TCL_DIR / script_name)

    if not os.path.exists(script_path) or not os.path.isfile(script_path):
        logger(f"Could not find Tcl file {script_path}.", status=Status.CRITICAL)
        sys.exit(1)

    return root.tk.eval("source {" + script_path + "}")


def tcl_eval(tcl: str, root: tk.Tk) -> str:
    """Evaluate a Tcl statement"""

    assert root is not None, "Engine must provide root"

    return root.tk.eval(tcl)


def tcl_call_procedure(procedure_name: str, *args, root: tk.Tk) -> str:
    """
    Call a Tcl procedure with arguments and return result

    Example:
        result = tcl_call_procedure("show_info", "Title", "Message", root=tk_root)
    """

    assert root is not None, "Engine must provide root"

    escaped_args = ["{" + str(arg) + "}" for arg in args]
    tcl_command = f"{procedure_name} {' '.join(escaped_args)}"

    return root.tk.eval(tcl_command)
