try:
    from engine.core import Game as CoreGame, Entity  # pyright: ignore[reportMissingImports]
except ModuleNotFoundError:
    print("Info:\nCould not import engine.core.\nMake sure that the engine directory is in the same folder as this script.\nRe-raising error.")
    raise

import os.path
import sys

from json import load
from pathlib import Path

PROJECT_FILE = "game.absp"


def resource_path(relative: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative) # pyright: ignore[reportAttributeAccessIssue]
    return os.path.join(os.path.abspath("."), relative)

def game_path(relative: str) -> str:
    if relative is None:
        return ''

    directory = Path(__file__).parent
    return resource_path(os.path.join(str(directory), relative))

if not os.path.exists(game_path(PROJECT_FILE)):
    print("Error:\ngame.absp project file does not exist in this directory.")
    sys.exit(1)

with open(game_path(PROJECT_FILE), "r") as f:
    data: dict = load(f)

game_dimensions = data["game"]["dimensions"]

core_game = CoreGame(data["name"], width=game_dimensions[0], height=game_dimensions[1])

for entity_name, entity_data in data["entities"].items():
    scriptfile = game_path(entity_data.get("scriptfile", None))
    if scriptfile == '':
        scriptfile = None

    entity = Entity(
        x=entity_data.get("x", 0),
        y=entity_data.get("y", 0),
        width=entity_data.get("width", 50),
        height=entity_data.get("height", 50),
        color=tuple(entity_data.get("color", (255, 255, 255))),
        scriptfile=scriptfile
    )
    core_game.scene.add(entity)

core_game.run()
