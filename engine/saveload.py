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
    """Convert a relative resource path into an absolute path."""

    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)  # pyright: ignore[reportAttributeAccessIssue]
    return str(Path.cwd() / relative)


def save_project(engine: Any) -> Optional[str]:
    """Save the engine project to a .absp file."""

    directory = filedialog.askdirectory()

    if directory is None:
        return None

    project_path = Path(directory) / "game.absp"
    project_path.parent.mkdir(parents=True, exist_ok=True)

    with project_path.open("w", encoding="utf-8") as f:
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
            indent=2,
        )

    messagebox.showinfo("Success", "Project saved successfully.")
    return str(project_path)


def load_project() -> Optional[list]:
    """Ask the user for a project directory and return the loaded game data."""

    directory = filedialog.askdirectory()

    if directory is None:
        return None

    project_path = Path(directory) / "game.absp"

    if not project_path.exists():
        logger(
            "game.absp file not found in selected directory. Creating.",
            status=LoggerStatus.WARNING,
        )
        project_path.write_text("{}", encoding="utf-8")
        return [{}, str(project_path)]

    if project_path.is_dir():
        messagebox.showerror("Error", "game.absp project file is a directory.")
        return None

    with project_path.open("r", encoding="utf-8") as f:
        data: dict = load(f)

    return [data, str(project_path)]
