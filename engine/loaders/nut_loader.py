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

from .. import logger
from . import _ENGINE_DIR

NUT_DIR: Final[Path] = _ENGINE_DIR / "nut"

if not NUT_DIR.exists() or not NUT_DIR.is_dir():
    logger.error("Could not find engine/nut/ directory.")
    sys.exit(1)


def _nut_include(path: str) -> Any:
    """
    Squirrel's include(): run a script relative to the calling script

    nut_source compiles each script under its own path, so the caller's
    stack frame names its file. Code with no file (e.g. nut_eval) resolves
    against engine/nut/.

    Args:
        path (str): script path, relative to the calling script's directory

    Returns:
        Any: Value the script returns, or None if it returns nothing.
    """

    caller = get_vm().get_roottable()["getstackinfos"](2)
    caller_path = Path(caller["src"]) if caller is not None else None

    if caller_path is not None and caller_path.is_file():
        base = caller_path.parent
    else:
        base = NUT_DIR

    script_path = base / path

    return nut_source(script_path.name, dir=script_path.parent)


BUILTINS: dict[str, Any] = {"include": _nut_include}


@cache
def get_vm() -> squirrel.StaticVM:
    """
    Get the engine's Squirrel VM, opening it on first use.

    Exactly one VM exists per process, so every call returns the same object.
    Scripts sourced into it share a root table.

    Returns:
        squirrel.StaticVM: The Squirrel VM.
    """

    vm = squirrel.SQVM()

    for name, func in BUILTINS.items():
        vm.bindfunc(funcname=name, func=func)

    return vm


def nut_source(script_name: str, *, dir: Path = NUT_DIR) -> Any:
    """
    Run a Squirrel script from engine/nut/, or from another directory

    Args:
        script_name (str): file to source from
        dir (Path): directory holding that file, engine/nut/ by default

    Returns:
        Any: Value the script returns, or None if it returns nothing.

    Raises:
        FileNotFoundError: If no such script exists in that directory.
        IsADirectoryError: If the path names a directory rather than a file.
    """

    script_path = dir / script_name

    if not script_path.exists():
        raise FileNotFoundError(f"Could not find Squirrel file {script_path}.")

    if script_path.is_dir():
        raise IsADirectoryError(f"{script_path}: Invalid script path (Is a directory)")

    script = get_vm().get_roottable()["compilestring"](
        script_path.read_text(encoding="utf-8"), str(script_path.resolve())
    )

    return script()


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
