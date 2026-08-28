# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Build and development utilities for the engine.
"""

import os
import shutil
import stat
import time
from PyInstaller.__main__ import run as pyinstaller
from multiprocessing import Process

from tkinter import messagebox
from pathlib import Path
from typing import Optional, Any

from .saveload import resource_path
from .logger import logger, Status

engine_path = Path(__file__).parent


def _clear_readonly(func: Any, path: Any, exc: BaseException) -> None:
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _remove_previous_build(path: Path, retries: int = 5, delay: float = 0.5) -> None:
    if not path.exists():
        return

    for attempt in range(retries):
        try:
            shutil.rmtree(path, onexc=_clear_readonly)  # ty: ignore[unknown-argument]
            return
        except PermissionError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)


def _build_pyinstaller(name: str, directory: Path) -> None:
    _remove_previous_build(directory / "dist" / name)

    pyi_args = [
        "--onedir",
        "--noconsole",
        "--noconfirm",
        "--name",
        name,
        "--distpath",
        str(directory / "dist"),
        "--workpath",
        str(directory / "build"),
        "--specpath",
        str(directory),
        f"--add-data={directory / 'game.absp'!s}{os.pathsep}.",
    ]

    if (directory / "scripts").exists():
        pyi_args.append(f"--add-data={directory / 'scripts'!s}{os.pathsep}scripts")

    pyi_args.append(f"--add-data={directory / 'data'!s}{os.pathsep}data")
    pyi_args.append(str(directory / "run.py"))

    pyinstaller(pyi_args=pyi_args)


def build(name: str, directory: Path, ENGINE_DATA_PATH: str) -> Optional[Process]:
    """
    Build the game

    Args:
        name (str): The project's name
        directory (Path): Path to build the game to
        ENGINE_DATA_PATH (str): Path of the data directory

    Returns:
        Optional[Process]: The process running the PyInstaller build, or None if
        the build could not be started. Callers can poll `process.is_alive()` to
        know when the build has actually finished.
    """

    if not directory.exists():
        logger(
            f'Build directory "{str(directory.resolve())}" does not exist.', status=Status.WARNING
        )
        messagebox.showerror(
            "Build Error",
            f'Build directory "{str(directory.resolve())}" does not exist. Save the project to a valid location and try again.',
        )
        return None

    launch_game_script = Path(resource_path("data/scripts/launch_game.py")).read_text(
        encoding="utf-8"
    )
    (directory / "run.py").write_text(launch_game_script, encoding="utf-8")

    ignore = shutil.ignore_patterns("*.pyc", "__pycache__")

    shutil.copytree(engine_path, directory / "engine", dirs_exist_ok=True, ignore=ignore)
    shutil.copytree(Path(ENGINE_DATA_PATH), directory / "data", dirs_exist_ok=True, ignore=ignore)

    name = name.replace(" ", "-")

    process = Process(
        target=_build_pyinstaller,
        args=(
            name,
            directory,
        ),
    )
    process.start()

    return process
