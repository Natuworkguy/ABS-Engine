# Copyright (C) Above and Below Studios
# See the LICENSE file for GPLv3

from tkinter import messagebox as messagebox
from tkinter import filedialog as filedialog
from json import dump, load
from typing import Optional, Any
import sys
import os

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative) # pyright: ignore[reportAttributeAccessIssue]
    return os.path.join(os.path.abspath("."), relative)


def save_project(engine: Any) -> None:
    file = filedialog.asksaveasfile(
        defaultextension=".abs",
        filetypes=[("ABS Project Files", "*.absp"), ("JSON Files", "*.json")],
        title="Save ABS Project",
        initialfile=f"{engine.project_name.replace(' ', '_')}.absproj"
    )

    if file:
        with open(file.name, "w") as f:
            dump({
                "name": engine.project_name,
                "entities": engine.entities,
            }, f)
            f.close()
        messagebox.showinfo("Success", "Project saved successfully.")


def load_project() -> Optional[dict]:
    file = filedialog.askopenfile(
        defaultextension=".abs",
        filetypes=[("ABS Project Files", "*.absp"), ("JSON Files", "*.json")],
        title="Load ABS Project"
    )

    if file:
        with open(file.name, "r") as f:
            data: dict = load(f)
            f.close()
        return data
