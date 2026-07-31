# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""Handles saving and loading of engine projects and data."""

from json import dump, load
import os
from pathlib import Path
import sys
from tkinter import filedialog, messagebox
from typing import Any, Dict, Optional, Tuple

from .logger import Status as LoggerStatus, logger


def resource_path(relative: str) -> str:
    """Convert a relative resource path into an absolute path.

    Args:
        relative: The relative path to the resource file.

    Returns:
        The absolute file path as a string.
    """
    if hasattr(sys, "_MEIPASS"):
        meipass_path: str = sys._MEIPASS  # type: ignore[unused-ignore]
        return os.path.join(meipass_path, relative)
    return str(Path.cwd() / relative)


def save_project(engine: Any, dir: Optional[str] = None) -> Optional[str]:
    """Save the engine project to a .absp file.

    Args:
        engine: The engine instance containing project data and properties
            (e.g., project_name, game_dimensions, cursor_visible,
            fullscreen, and entities).
        dir: An optional explicit directory path to save into.

    Returns:
        The path to the saved project file as a string if saved, or None
        if the user cancelled the file dialog.
    """
    directory: str = dir if dir else filedialog.askdirectory()

    if not directory:
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


def load_project() -> Optional[Tuple[Dict[str, Any], str]]:
    """Ask the user for a project directory and return the loaded game data.

    Returns:
        A tuple of `(data_dict, file_path_str)`, or None if cancelled/failed.
    """
    directory: str = filedialog.askdirectory()

    if not directory:
        return None

    project_path = Path(directory) / "game.absp"

    if not project_path.exists():
        logger(
            "game.absp file not found in selected directory. Creating.",
            status=LoggerStatus.WARNING,
        )
        project_path.write_text("{}", encoding="utf-8")
        return {}, str(project_path)

    if project_path.is_dir():
        messagebox.showerror("Error", "game.absp project file is a directory.")
        return None

    with project_path.open("r", encoding="utf-8") as f:
        data: Dict[str, Any] = load(f)

    return data, str(project_path)
