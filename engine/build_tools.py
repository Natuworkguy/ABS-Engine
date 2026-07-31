# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Build and development utilities for the engine.
"""


import shutil

from tkinter import messagebox
from pathlib import Path

from .saveload import resource_path
from .logger import logger, Status

engine_path = Path(__file__).parent


def build(directory: Path, ENGINE_DATA_PATH: str) -> None:
    """Build the game.

    Args:
        directory (Path): Path to build the game to
        ENGINE_DATA_PATH (str): Path of the data directory
    """

    if not directory.exists():
        logger(
            f'Build directory "{str(directory.resolve())}" does not exist.', status=Status.WARNING
        )
        messagebox.showerror(
            "Build Error",
            f'Build directory "{str(directory.resolve())}" does not exist. Save the project to a valid location and try again.',
        )
        return

    launch_game_script = Path(resource_path("data/scripts/launch_game.py")).read_text(
        encoding="utf-8"
    )
    (directory / "run.py").write_text(launch_game_script, encoding="utf-8")

    ignore = shutil.ignore_patterns("*.pyc", "__pycache__")

    shutil.copytree(engine_path, directory / "engine", dirs_exist_ok=True, ignore=ignore)
    shutil.copytree(Path(ENGINE_DATA_PATH), directory / "data", dirs_exist_ok=True, ignore=ignore)
