# Copyright (C) Above and Below Studios
# See the LICENSE file for GPLv3

import os

import shutil

from tkinter import messagebox
from pathlib import Path

from .saveload import resource_path
from .logger import logger, Status

engine_path = Path(__file__).parent


def build(dir: Path, ENGINE_DATA_PATH):
    launch_game_script = None

    if not os.path.exists(dir):
        logger(f"Build directory \"{str(dir.resolve())}\" does not exist.", status=Status.WARNING)
        messagebox.showerror("Build Error", f"Build directory \"{str(dir.resolve())}\" does not exist. Save the project to a valid location and try again.")
        return

    with open(resource_path("data/scripts/launch_game.py")) as f:
        launch_game_script = f.read()
        f.close()

    with open(os.path.join(dir, "run.py"), 'w') as f:
        f.write(launch_game_script)
        f.close()

    shutil.copytree(engine_path, os.path.join(dir, "engine"), dirs_exist_ok=True)
    shutil.copytree(ENGINE_DATA_PATH, os.path.join(dir, "data"), dirs_exist_ok=True)
