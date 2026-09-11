# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Squirrel integration utilities for the engine.
"""

import sys

import squirrel

from functools import cache
from typing import Final, Any
from pathlib import Path

from ..logger import logger, Status
from . import _ENGINE_DIR

NUT_DIR: Final[Path] = _ENGINE_DIR / "nut"

if not NUT_DIR.exists() or not NUT_DIR.is_dir():
    logger("Could not find engine/nut/ directory.", status=Status.CRITICAL)
    sys.exit(1)


@cache
def get_vm() -> squirrel.StaticVM:
    """
    Get the engine's Squirrel VM, opening it on first use.

    Exactly one VM exists per process, so every call returns the same object.
    Scripts sourced into it share a root table.

    Returns:
        squirrel.StaticVM: The Squirrel VM.
    """

    return squirrel.SQVM()


def nut_source(script_name: str) -> Any:
    """
    Run a Squirrel script from engine/nut/

    Args:
        script_name (str): file in engine/nut/ to source from

    Returns:
        Any: Value the script returns, or None if it returns nothing.

    Raises:
        FileNotFoundError: If no such script exists under engine/nut/.
        IsADirectoryError: If the path names a directory rather than a file.
    """

    script_path = NUT_DIR / script_name

    if not script_path.exists():
        raise FileNotFoundError(f"Could not find Squirrel file {script_path}.")

    if script_path.is_dir():
        raise IsADirectoryError(f"{script_path}: Invalid script path (Is a directory)")

    return nut_eval(script_path.read_text(encoding="utf-8"))


def nut_eval(nut: str) -> Any:
    """
    Evaluate a Squirrel statement

    Args:
        nut (str): source to evaluate

    Returns:
        Any: Result
    """

    return get_vm().execute(nut)


def nut_call_function(function_name: str, *args: Any) -> Any:
    """
    Call a Squirrel function from the root table with arguments and return result

    Example:
        result = nut_call_function("add", 3, 4)

    Args:
        function_name (str): function to call
        *args (Any): Arguments passed to the Squirrel function.

    Returns:
        Any: Result of the function
    """

    return get_vm().get_roottable()[function_name](*args)
