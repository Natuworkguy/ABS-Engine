# Copyright (C) Above and Below Studios
# See the LICENSE file for GPLv3

import os
import sys

import tkinter as tk

from typing import Optional
from pathlib import Path

from .logger import logger, Status

TCL_DIR = Path(__file__).parent / "tcl"

if not os.path.exists(TCL_DIR) or not os.path.isdir(TCL_DIR):
    logger("Could not find engine/tcl/ directory.", status=Status.CRITICAL)
    sys.exit(1)

def tcl_source(script_name: str, root: Optional[tk.Tk] = None) -> str:
    """Run a Tcl script from engine/tcl"""

    if root is None:
        root = tk.Tk()

    script_path = str(TCL_DIR / script_name)

    if not os.path.exists(script_path) or not os.path.isfile(script_path):
        logger(f"Could not find Tcl file {script_path}.", status=Status.CRITICAL)
        sys.exit(1)

    return root.tk.eval("source {" + script_path + "}")

def tcl_eval(tcl: str, root: Optional[tk.Tk] = None) -> str:
    """Evaluate a Tcl statement"""

    if root is None:
        root = tk.Tk()

    return root.tk.eval(tcl)
