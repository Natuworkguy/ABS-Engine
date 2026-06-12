# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

import os

import shutil

from tkinter import messagebox
from pathlib import Path

from .saveload import resource_path
from .logger import logger, Status

engine_path = Path(__file__).parent


def build(directory: Path, ENGINE_DATA_PATH: str) -> None:
    launch_game_script = None

    if not os.path.exists(directory):
        logger(
            f'Build directory "{str(directory.resolve())}" does not exist.',
            status=Status.WARNING
        )
        messagebox.showerror(
            "Build Error",
            f'Build directory "{str(directory.resolve())}" does not exist. Save the project to a valid location and try again.',
        )
        return

    with open(resource_path("data/scripts/launch_game.py")) as f:
        launch_game_script = f.read()
        f.close()

    with open(os.path.join(directory, "run.py"), "w") as f:
        f.write(launch_game_script)
        f.close()

    ignore = shutil.ignore_patterns("*.pyc", "__pycache__")

    shutil.copytree(
        engine_path, os.path.join(directory, "engine"), dirs_exist_ok=True, ignore=ignore
    )
    shutil.copytree(
        ENGINE_DATA_PATH, os.path.join(directory, "data"), dirs_exist_ok=True, ignore=ignore
    )
