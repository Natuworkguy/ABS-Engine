# Copyright (C) Above and Below Studios
# See the LICENSE file for GPLv3
 
import os

from pathlib import Path
import shutil
from .saveload import resource_path

engine_path = Path(__file__).parent

def build(dir: Path):
    global engine_path

    launch_game_script = None

    with open(resource_path("data/scripts/launch_game.py")) as f:
        launch_game_script = f.read()
        f.close()

    with open(os.path.join(dir, "run.py"), 'w') as f:
        f.write(launch_game_script)
        f.close()

    shutil.copytree(engine_path, os.path.join(dir, "engine"), dirs_exist_ok=True)
