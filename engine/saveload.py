# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Handles saving and loading of engine projects and data.
"""

from tkinter import messagebox as messagebox
from tkinter import filedialog as filedialog
from json import dump, load
from typing import Optional, Any
from pathlib import Path

from .logger import logger, Status as LoggerStatus

import sys
import os


def resource_path(relative: str) -> str:
    """
    Convert a relative resource path into an absolute path.

    Args:
        relative (str): Relative path to a resource.

    Returns:
        str: Absolute path to the resource.
    """

    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)  # pyright: ignore[reportAttributeAccessIssue]
    return os.path.join(os.path.abspath("."), relative)


def save_project(engine: Any, dir_str: Optional[str] = None) -> Optional[str]:
    """
    Save the project as an absp file

    Args:
        engine (Any): engine instance to extract the project information from
        dir_str (Optional[str]): Directory to save the project in

    Returns:
        Optional[str]: Path to the saved file or None
    """

    if dir_str is None:
        dir_str = filedialog.askdirectory()

        if not dir_str:
            return None

    dir = Path(dir_str)

    if dir.exists():
        gamefile = dir / "game.absp"

        with open(gamefile, "w", encoding="utf-8") as f:
            dump(
                {
                    "name": engine.project_name,
                    "game": {
                        "dimensions": engine.game_dimensions,
                        "cursor_visible": engine.cursor_visible,
                        "fullscreen": engine.fullscreen,
                    },
                    "entities": engine.entities,
                },
                f,
            )

        with open(dir / ".gitignore", "w") as f:
            f.write(
                """
data/images/abs_*  # Remove if using ABS Engine's logo or other ABS assets
engine/
launch_game.py
run.py
build/
dist/
*.spec
            """.strip()
            )

        with open(dir / ".gitattributes", "w") as f:
            f.write(
                """
*.absp text linguist-language=JSON linguist-detectable=true diff=json
            """.strip()
            )

        messagebox.showinfo("Success", "Project saved successfully.")

        return str(gamefile)

    return None


def load_project() -> Optional[list]:
    """
    Ask the user to open an absp file, then return the contents

    Returns:
        Optional[list]: file content
    """

    dir = filedialog.askdirectory()

    if dir and os.path.exists(dir):
        gamefile = str(Path(dir) / "game.absp")

        if not os.path.exists(gamefile):
            logger(
                "game.absp file not found in selected directory. Creating.",
                status=LoggerStatus.WARNING,
            )

            with open(gamefile, "w", encoding="utf-8") as f:
                f.write("{}")

            return [{}, gamefile]

        if os.path.isdir(gamefile):
            messagebox.showerror("Error", "game.absp project file is a directory.")
            return None

        with open(gamefile, "r") as f:
            data: dict = load(f)

        return [data, gamefile]

    return None
