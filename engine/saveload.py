# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

from json import dump, load
from typing import Optional, Any
import sys
import os

from PySide6.QtWidgets import QFileDialog, QMessageBox


def resource_path(relative: str) -> str:
    _meipass: str | None = getattr(sys, "_MEIPASS", None)
    if _meipass is not None:
        return os.path.join(_meipass, relative)
    return os.path.join(os.path.abspath("."), relative)


def save_project(engine: Any, parent: Optional[Any] = None) -> Optional[Any]:
    file_path, _ = QFileDialog.getSaveFileName(
        parent,
        "Save ABS Project",
        "game.absp",
        "ABS Project Files (*.absp);;JSON Files (*.json)",
    )

    if file_path:
        with open(file_path, "w") as f:
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
        QMessageBox.information(parent, "Success", "Project saved successfully.")

        return open(file_path, "r")

    return None


def load_project(parent: Optional[Any] = None) -> Optional[list]:
    file_path, _ = QFileDialog.getOpenFileName(
        parent,
        "Load ABS Project",
        "",
        "ABS Project Files (*.absp);;JSON Files (*.json)",
    )

    if file_path:
        with open(file_path, "r") as f:
            data: dict = load(f)
        return [data, open(file_path, "r")]

    return None
