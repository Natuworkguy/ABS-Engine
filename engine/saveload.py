# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Handles saving and loading of engine projects and data.
"""

from tkinter import messagebox as messagebox
from tkinter import filedialog as filedialog
from json import dump, load
from typing import Optional, Any
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


def save_project(engine: Any) -> Optional[Any]:
    """
    Save the project as an absp file

    Args:
        engine (Any): engine instance to extract the project information from

    Returns:
        Optional[Any]: IO object of the file or None
    """
    file = filedialog.asksaveasfile(
        defaultextension=".absp",
        filetypes=[("ABS Project Files", "*.absp"), ("JSON Files", "*.json")],
        title="Save ABS Project",
        initialfile="game.absp",
    )

    if not file:
        return None

    with file:
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
            file,
            indent=4,  # Optional: Makes the saved JSON human-readable
        )

    messagebox.showinfo("Success", "Project saved successfully.")
    return file


def load_project() -> Optional[list]:
    """
    Ask the user to open an absp file, then return the contents

    Returns:
        Optional[list]: file content
    """
    
    file = filedialog.askopenfile(
        defaultextension=".absp",
        filetypes=[("ABS Project Files", "*.absp"), ("JSON Files", "*.json")],
        title="Load ABS Project",
    )

    if not file:
        return None

    with file:
        data: dict = load(file)

    return data, file
