# Copyright (C) Above and Below Studios
# See the LICENSE file for GPLv3

from tkinter import messagebox as messagebox
from tkinter import filedialog as filedialog
from json import dump, load
from typing import Optional, Any


def save_project(engine: Any) -> None:
    file = filedialog.asksaveasfile(
        defaultextension=".abs",
        filetypes=[("ABS Project Files", "*.absproj"), ("JSON Files", "*.json")],
        title="Save ABS Project",
        initialfile=f"{engine.project_name.replace(' ', '_')}.absproj"
    )

    if file:
        with open(file.name, "w") as f:
            dump({
                "name": engine.project_name,
                "entities": engine.entities
            }, f)
            f.close()
        messagebox.showinfo("Success", "Project saved successfully.")


def load_project() -> Optional[dict]:
    file = filedialog.askopenfile(
        defaultextension=".abs",
        filetypes=[("ABS Project Files", "*.absproj"), ("JSON Files", "*.json")],
        title="Load ABS Project"
    )

    if file:
        with open(file.name, "r") as f:
            data: dict = load(f)
            f.close()
        return data
