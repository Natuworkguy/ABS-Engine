# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""Handles saving and loading of engine projects and data."""

import os
import sys
from json import dump, load
from tkinter import filedialog, messagebox
from typing import Any, Optional, Tuple


def resource_path(relative: str) -> str:
    """Convert a relative resource path into an absolute path.

    Args:
        relative (str): Relative path to a resource.

    Returns:
        str: Absolute path to the resource.
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)  # pyright: ignore[reportAttributeAccessIssue]
    return os.path.join(os.path.abspath("."), relative)


def save_project(engine: Any) -> Optional[str]:
    """Save the project as an absp file.

    Args:
        engine (Any): engine instance to extract the project information from

    Returns:
        Optional[str]: Path to the saved file or None
    """
    file_path = filedialog.asksaveasfilename(
        defaultextension=".absp",
        filetypes=[("ABS Project Files", "*.absp"), ("JSON Files", "*.json")],
        title="Save ABS Project",
        initialfile="game.absp",
    )

    if not file_path:
        return None

    with open(file_path, "w", encoding="utf-8") as file:
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
            indent=4,
        )

    messagebox.showinfo("Success", "Project saved successfully.")
    return file_path


def load_project() -> Optional[Tuple[dict, str]]:
    """Ask the user to open an absp file, then return the contents.

    Returns:
        Optional[Tuple[dict, str]]: A tuple containing the data dict and the file path, or None.
    """
    file_path = filedialog.askopenfilename(
        defaultextension=".absp",
        filetypes=[("ABS Project Files", "*.absp"), ("JSON Files", "*.json")],
        title="Load ABS Project",
    )

    if not file_path:
        return None

    with open(file_path, "r", encoding="utf-8") as file:
        data: dict = load(file)

    return data, file_path
