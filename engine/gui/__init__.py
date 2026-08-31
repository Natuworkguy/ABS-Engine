# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

import sys
import os
import ctypes
import queue
import shutil

from functools import partial

import tkinter as tk
from tkinter import DISABLED, NORMAL, ttk
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
import tkinter.colorchooser as colorchooser
import tkinter.filedialog as filedialog
from _tkinter import TclError

from typing import Optional

from ..saveload import (
    save_project as sl_save_project,
    load_project as sl_load_project,
)
from ..core import Game as CoreGame, Entity
from ..logger import logger, Status as LoggerStatus
from ..build_tools import build
from ..loaders.tcl_loader import tcl_source
from .tooltip import Tooltip as _Tooltip

from pathlib import Path

GP_BASE_PATH: str = str(Path(__file__).parent.parent)
LAST_SAVE_DIR: Optional[str] = None
ENGINE_DATA_PATH = str(Path(__file__).parent.parent.parent / "data")
APP_ID: str = "ABSEngine"


def game_path(relative: Optional[str]) -> Optional[str]:
    if relative is None:
        return None

    return os.path.join(str(GP_BASE_PATH), relative)


class Editor:
    root: tk.Tk
    abs_section: tk.LabelFrame
    exit_button: ttk.Button
    view_popup: Optional[tk.Toplevel]
    entity_data: Optional[tk.Text]

    def __init__(self) -> None:
        self.core_game: Optional[CoreGame] = None
        self.view_popup = None
        self.game_settings_popup: Optional[tk.Toplevel] = None
        self.entity_data = None

        self.project_name = "Untitled Project"
        self.game_dimensions = [800, 600]
        self.cursor_visible = True
        self.fullscreen = False
        self.entities: dict = {}

        self.root = tk.Tk()
        self.root.title("ABS Engine")
        self.root.geometry("530x700")
        self.load_theme()

        try:
            ttk.Style(self.root).theme_use("vista")
        except TclError:
            pass

        self.root.bind("<Control-Shift-S>", lambda *args: self.save_project_as())
        self.root.bind("<Control-s>", lambda *args: self.save_project())
        self.root.bind("<Control-o>", lambda *args: self.load_project())
        self.root.bind("<F9>", lambda *args: self.run_game())

        self.menu = tk.Menu(self.root)

        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.file_menu.add_command(label="Open", command=self.load_project, accelerator="Ctrl+O")
        self.file_menu.add_command(
            label="Save As", command=self.save_project_as, accelerator="Ctrl+Shift+S"
        )
        self.file_menu.add_command(label="Save", command=self.save_project, accelerator="Ctrl+S")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit)

        self.menu.add_cascade(label="File", menu=self.file_menu)

        self.game_menu = tk.Menu(self.menu, tearoff=0)

        self.game_menu.add_command(label="Game Settings", command=self.game_settings)
        self.game_menu.add_command(label="Build Game", command=self.build_game, state=DISABLED)
        self.game_menu.add_command(label="Run Game", command=self.run_game, accelerator="F9")

        self.menu.add_cascade(label="Game", menu=self.game_menu)

        self.root.config(menu=self.menu)

        if "-noicon" not in sys.argv:
            if sys.platform == "win32":
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

            try:
                self.root.iconphoto(
                    True,
                    tk.PhotoImage(file=os.path.join(ENGINE_DATA_PATH, "images", "abs_icon.png")),
                )
            except TclError as e:
                logger("Could not load icon image.", status=LoggerStatus.CRITICAL)
                logger(
                    "Try running with the -noicon flag if this persists.",
                    status=LoggerStatus.CRITICAL,
                )
                logger(f"Error: {e}", status=LoggerStatus.CRITICAL)
                sys.exit(1)

        self.root.resizable(False, False)

        self.project_section = tk.LabelFrame(self.root, width=200, height=100, text="Project")
        self.project_section.pack(fill="both", padx=5, pady=5)

        self.project_name_label = tk.Label(self.project_section, text="Project Name: ")
        self.project_name_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.project_name_input = ttk.Entry(self.project_section)
        self.project_name_input.pack(side=tk.LEFT, padx=5, pady=5)
        self.project_name_input.insert(0, "Untitled Project")

        self.name_save_button = ttk.Button(
            self.project_section,
            text="Save Name",
            command=lambda: self.save_name(self.project_name_input.get()),
        )
        self.name_save_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.entities_section = tk.LabelFrame(self.root, width=200, height=200, text="Entities")
        self.entities_section.pack(fill="both", padx=5, pady=5)

        self.entity_list_label = tk.Label(self.entities_section, text="Entity List")
        self.entity_list_label.pack(padx=5, pady=5)

        self.entity_list = tk.Listbox(self.entities_section, height=5, selectmode=tk.SINGLE)
        self.entity_list.pack(padx=5, pady=5)

        self.view_entity_button = ttk.Button(
            self.entities_section,
            text="Edit Data",
            command=lambda: self.view_entity(self.entity_list),
        )
        self.view_entity_button.pack(padx=5, pady=5)

        self.rename_entity_button = ttk.Button(
            self.entities_section, text="Rename Entity", command=self.rename_entity
        )
        self.rename_entity_button.pack(padx=5, pady=5)

        self.delete_entity_button = ttk.Button(
            self.entities_section, text="Delete Entity", command=self.delete_entity
        )
        self.delete_entity_button.pack(padx=5, pady=5)

        self.entity_separator = ttk.Separator(self.entities_section, orient="horizontal")
        self.entity_separator.pack(fill="x", padx=5, pady=10)

        self.add_entity_input = ttk.Entry(self.entities_section)
        self.add_entity_input.pack(padx=5, pady=5)

        self.add_entity_button = ttk.Button(
            self.entities_section,
            text="Add Entity",
            command=lambda: self.add_entity(self.add_entity_input.get()),
        )
        self.add_entity_button.pack(padx=5, pady=5)

    def load_theme(self) -> None:
        try:
            tcl_source("theme.tcl", self.root)
        except TclError as e:
            logger("Failed to load theme.", status=LoggerStatus.WARNING)
            logger(f"Error: {e}", status=LoggerStatus.WARNING)

    def build_game(self) -> None:
        do_build = messagebox.askyesno(
            "Build Tools",
            "This will build to the folder containing the .absp project file. Do you want to continue?",
        )

        if not do_build:
            return

        logger("Build Tools: Starting build")

        build_handle = build(
            name=self.project_name_input.get(),
            directory=Path(GP_BASE_PATH),
            ENGINE_DATA_PATH=ENGINE_DATA_PATH,
        )

        if build_handle is None:
            return

        process, log_queue = build_handle

        progress_popup = tk.Toplevel(self.root)
        progress_popup.wm_title("Building Game")
        progress_popup.resizable(False, False)
        progress_popup.protocol("WM_DELETE_WINDOW", lambda: None)
        progress_popup.transient(self.root)

        progress_content = ttk.Frame(progress_popup, padding=(24, 20))
        progress_content.pack(fill="both", expand=True)

        ttk.Label(progress_content, text="Building Game", font=("Segoe UI", 12, "bold")).pack(
            anchor="w"
        )

        ttk.Label(
            progress_content,
            text="This may take a few moments, please wait...",
            foreground="#666666",
        ).pack(anchor="w", pady=(2, 14))

        progress_bar = ttk.Progressbar(progress_content, mode="indeterminate", length=300)
        progress_bar.pack(fill="x")
        progress_bar.start(10)

        ttk.Label(
            progress_content,
            text="Pyinstaller Output:",
            foreground="#999999",
            font=("Segoe UI", 8),
        ).pack(anchor="w", pady=(12, 4))

        log_frame = ttk.Frame(progress_content)
        log_frame.pack(fill="both", expand=True)

        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical")
        log_scrollbar.pack(side=tk.RIGHT, fill="y")

        log_text = tk.Text(
            log_frame,
            width=64,
            height=12,
            font=("Consolas", 8),
            background="#1e1e1e",
            foreground="#d4d4d4",
            wrap="word",
            state=DISABLED,
            yscrollcommand=log_scrollbar.set,
        )
        log_text.pack(side=tk.LEFT, fill="both", expand=True)
        log_scrollbar.config(command=log_text.yview)

        def drain_log_queue() -> None:
            while True:
                try:
                    line = log_queue.get_nowait()
                except queue.Empty:
                    return

                if line is None:
                    continue

                log_text.configure(state=NORMAL)
                log_text.insert(tk.END, line + "\n")
                log_text.see(tk.END)
                log_text.configure(state=DISABLED)

        progress_popup.update_idletasks()
        popup_x = (
            self.root.winfo_x() + (self.root.winfo_width() - progress_popup.winfo_width()) // 2
        )
        popup_y = (
            self.root.winfo_y() + (self.root.winfo_height() - progress_popup.winfo_height()) // 2
        )
        progress_popup.geometry(f"+{popup_x}+{popup_y}")

        progress_popup.grab_set()

        def poll_build() -> None:
            drain_log_queue()

            if process.is_alive():
                self.root.after(150, poll_build)
                return

            drain_log_queue()

            progress_bar.stop()
            progress_popup.grab_release()
            progress_popup.destroy()

            if process.exitcode == 0:
                logger("Build Tools: Build completed")
                messagebox.showinfo("Build Tools", "The build has been completed.")
            else:
                logger("Build Tools: Build failed", status=LoggerStatus.WARNING)
                messagebox.showerror(
                    "Build Tools",
                    "The build failed. Check the console/log output for details.",
                )

        self.root.after(200, poll_build)

    def game_settings(self) -> None:
        self.game_settings_popup = tk.Toplevel(self.root, height=150)
        self.game_settings_popup.wm_title("Game Settings")
        self.game_settings_popup.resizable(False, False)

        self.game_settings_dimensions_section = ttk.LabelFrame(
            self.game_settings_popup, width=200, height=100, text="Dimensions"
        )
        self.game_settings_dimensions_section.pack(padx=5, pady=5)

        self.game_settings_width_label = ttk.Label(
            self.game_settings_dimensions_section, text="Width"
        )
        self.game_settings_width_label.pack(padx=5, pady=5)
        self.game_settings_width = ttk.Entry(self.game_settings_dimensions_section)
        self.game_settings_width.pack(padx=5, pady=5)
        self.game_settings_width.insert(tk.END, str(self.game_dimensions[0]))

        self.game_settings_height_label = ttk.Label(
            self.game_settings_dimensions_section, text="Height"
        )
        self.game_settings_height_label.pack(padx=5, pady=5)
        self.game_settings_height = ttk.Entry(self.game_settings_dimensions_section)
        self.game_settings_height.pack(padx=5, pady=5)
        self.game_settings_height.insert(tk.END, str(self.game_dimensions[1]))

        self.game_settings_display_section = ttk.LabelFrame(
            self.game_settings_popup, width=200, height=100, text="Display"
        )
        self.game_settings_display_section.pack(padx=5, pady=5, fill="x")

        self.game_settings_cursor_visible = tk.BooleanVar(value=self.cursor_visible)
        self.game_settings_cursor_visible_checkbox = ttk.Checkbutton(
            self.game_settings_display_section,
            text="Cursor Visible",
            variable=self.game_settings_cursor_visible,
        )
        self.game_settings_cursor_visible_checkbox.pack(padx=5, pady=5)

        self.game_settings_fullscreen = tk.BooleanVar(value=self.fullscreen)
        self.game_settings_fullscreen_checkbox = ttk.Checkbutton(
            self.game_settings_display_section,
            text="Fullscreen",
            variable=self.game_settings_fullscreen,
        )
        self.game_settings_fullscreen_checkbox.pack(padx=5, pady=5)

        def game_settings_save() -> None:
            width = self.game_settings_width.get()
            height = self.game_settings_height.get()
            cursor_visible = self.game_settings_cursor_visible.get()
            fullscreen = self.game_settings_fullscreen.get()

            if self.game_settings_popup is not None:
                self.game_settings_popup.destroy()

            if width.strip() and height.strip():
                try:
                    self.game_dimensions[0] = int(width)
                    self.game_dimensions[1] = int(height)
                    self.cursor_visible = cursor_visible
                    self.fullscreen = fullscreen
                except ValueError:
                    messagebox.showerror(
                        "Error", "Width and height values must both be of type integer."
                    )
                    return
            else:
                messagebox.showerror("Error", "Width and height values must be given.")
                return

            messagebox.showinfo("Success", "Settings saved")

        self.game_settings_save_button = ttk.Button(
            self.game_settings_popup, text="Save and Close", command=game_settings_save
        )
        self.game_settings_save_button.pack(padx=5, pady=5)

    def delete_entity(self) -> None:
        try:
            selected_item = self.entity_list.get(self.entity_list.curselection()[0])  # type: ignore[no-untyped-call]
        except IndexError:
            messagebox.showerror("Error", "No entity selected.")
            return

        do_delete: bool = messagebox.askokcancel(
            "Delete Entity",
            "Are you sure you want to delete the selected entity?",
            icon="warning",
            default="cancel",
        )

        if not do_delete:
            return

        del self.entities[selected_item]
        self.entity_list.delete(self.entity_list.curselection()[0])  # type: ignore[no-untyped-call]

    def rename_entity(self) -> None:
        try:
            raw_selected_item = self.entity_list.curselection()[0]  # type: ignore[no-untyped-call]
            selected_item = self.entity_list.get(raw_selected_item)
        except IndexError:
            messagebox.showerror("Error", "No entity selected.")
            return

        new_name = simpledialog.askstring(
            "Rename Entity", "Enter new entity name:", initialvalue=selected_item
        )

        if new_name is None:
            return

        if not new_name.strip():
            messagebox.showerror("Error", "Entity name cannot be empty.")
            return

        self.entities[new_name] = self.entities.pop(selected_item)
        self.entity_list.delete(raw_selected_item)
        self.entity_list.insert(tk.END, new_name)

    def add_entity(self, name: str) -> None:
        if not name.strip():
            messagebox.showerror("Error", "Entity name cannot be empty.")
            return
        elif name in self.entities:
            messagebox.showerror("Error", "Entity already exists.")
            return

        self.add_entity_input.delete(0, tk.END)

        self.entities.update({name: {}})
        self.entity_list.insert(tk.END, name)

    def view_entity(self, entity_list: tk.Listbox) -> None:
        try:
            selected_item = entity_list.get(entity_list.curselection()[0])  # type: ignore[no-untyped-call]

            self.view_popup = tk.Toplevel(self.root)
            self.view_popup.wm_title("Entity Data")
            self.view_popup.resizable(False, False)

            fields = {
                "x": int,
                "y": int,
                "width": int,
                "height": int,
                "scriptfile": str,
                "image": str,
            }
            field_hints = {
                "scriptfile": "path, relative to the project root",
                "image": "path, relative to the project root",
            }
            file_filters = {
                "scriptfile": [("Python scripts", "*.py"), ("All files", "*.*")],
                "image": [
                    ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("All files", "*.*"),
                ],
            }
            field_objs: dict[str, ttk.Entry] = {}

            fields_section = ttk.LabelFrame(self.view_popup, text=f"Editing: {selected_item}")
            fields_section.pack(fill="both", padx=10, pady=10)

            def pick_file(field_name: str) -> None:
                if LAST_SAVE_DIR is None:
                    messagebox.showerror(
                        "Error",
                        "Save or load the project first so file paths can be stored "
                        "relative to the project root.",
                    )
                    return

                root_dir = Path(GP_BASE_PATH).resolve()

                initial_dir = root_dir
                current = field_objs[field_name].get().strip()
                if current:
                    current_dir = (root_dir / current).parent
                    if current_dir.is_dir():
                        initial_dir = current_dir

                chosen = filedialog.askopenfilename(
                    title=f"Select {field_name}",
                    initialdir=str(initial_dir),
                    filetypes=file_filters[field_name],
                )

                if self.view_popup is not None:
                    self.view_popup.lift()
                    self.view_popup.focus_force()

                if not chosen:
                    return

                chosen_path = Path(chosen).resolve()

                if not chosen_path.is_relative_to(root_dir):
                    messagebox.showerror(
                        "Error",
                        f"{chosen_path.name} is outside the project folder.\n"
                        f"Choose a file inside {root_dir}.",
                    )
                    return

                field_objs[field_name].delete(0, tk.END)
                field_objs[field_name].insert(0, chosen_path.relative_to(root_dir).as_posix())

            row = 0
            for name in fields.keys():
                label_cell = ttk.Frame(fields_section)
                label_cell.grid(row=row, column=0, sticky="w", padx=(10, 10), pady=6)

                label = ttk.Label(label_cell, text=name, anchor="w")
                label.pack(side="left")

                if name in field_hints:
                    info_icon = ttk.Label(label_cell, text=" \u24d8", foreground="#4a90d9")
                    info_icon.pack(side="left")
                    _Tooltip(info_icon, field_hints[name])

                if name in file_filters:
                    entry_cell = ttk.Frame(fields_section)
                    entry_cell.grid(row=row, column=1, sticky="ew", padx=(0, 10), pady=6)

                    field_objs[name] = ttk.Entry(entry_cell, width=30)
                    field_objs[name].pack(side="left", expand=True, fill="x")

                    browse_button = ttk.Button(
                        entry_cell,
                        text="Browse...",
                        command=partial(pick_file, name),
                    )
                    browse_button.pack(side="left", padx=(4, 0))
                    _Tooltip(browse_button, "Pick a file inside the project folder", 1000)
                else:
                    field_objs[name] = ttk.Entry(fields_section, width=30)
                    field_objs[name].grid(row=row, column=1, sticky="ew", padx=(0, 10), pady=6)

                field_objs[name].insert(0, str(self.entities[selected_item].get(name, "")))

                row += 1

            color_label = ttk.Label(fields_section, text="color", anchor="w")
            color_label.grid(row=row, column=0, sticky="w", padx=(10, 10), pady=6)

            color_frame = ttk.Frame(fields_section)
            color_frame.grid(row=row, column=1, sticky="ew", padx=(0, 10), pady=6)

            default_color = self.entities[selected_item].get("color", (255, 255, 255))
            color_objs = []
            for i in range(3):
                try:
                    default_component = str(default_color[i])
                except (IndexError, TypeError):
                    default_component = "255"

                color_entry = ttk.Entry(color_frame, width=6)
                color_entry.insert(0, default_component)
                color_entry.pack(
                    side="left", expand=True, fill="x", padx=(0, 4) if i < 2 else (0, 0)
                )
                color_objs.append(color_entry)

            def pick_color() -> None:
                initial = []
                for c in color_objs:
                    try:
                        initial.append(max(0, min(255, int(c.get()))))
                    except ValueError:
                        initial.append(255)

                _rgb, hex_color = colorchooser.askcolor(
                    color="#%02x%02x%02x" % tuple(initial),
                    title="Pick Color",
                )

                if self.view_popup is not None:
                    self.view_popup.lift()
                    self.view_popup.focus_force()

                if hex_color is None:
                    return

                hex_color = hex_color.lstrip("#")
                for i, c in enumerate(color_objs):
                    c.delete(0, tk.END)
                    c.insert(0, str(int(hex_color[i * 2 : i * 2 + 2], 16)))  # noqa: E203

            color_picker_button = ttk.Button(color_frame, text="Pick...", command=pick_color)
            color_picker_button.pack(side="left", padx=(4, 0))
            _Tooltip(color_picker_button, "Open a color picker to choose the RGB values", 1000)

            fields_section.columnconfigure(1, weight=1)

            def save_edits() -> None:
                if self.view_popup is None:
                    return

                updates = {}

                # A blank field means "use the default", and a key this entity does
                # not carry is exactly what every reader falls back to a default on.
                cleared = []

                try:
                    for name, obj in field_objs.items():
                        value = obj.get().strip()

                        if value == "":
                            cleared.append(name)
                            continue

                        updates[name] = fields[name](value)

                    color_values = [c.get().strip() for c in color_objs]
                    if any(color_values):
                        # A blank component falls back to its own default rather
                        # than dragging the whole color back to white.
                        parsed_color = tuple(int(c) if c else 255 for c in color_values)
                        if any(component < 0 or component > 255 for component in parsed_color):
                            raise ValueError("Color values must be between 0 and 255")
                        updates["color"] = parsed_color
                    else:
                        cleared.append("color")
                except ValueError as e:
                    messagebox.showerror(
                        "Error",
                        f"Failed to save entity data: {e}\nPlease ensure all fields contain valid values.",
                    )
                    return

                for name in cleared:
                    self.entities[selected_item].pop(name, None)

                self.entities[selected_item].update(updates)
                self.view_popup.destroy()

            button_row = ttk.Frame(self.view_popup)
            button_row.pack(fill="x", padx=10, pady=(0, 10))
            button_row.columnconfigure(0, weight=1)
            button_row.columnconfigure(1, weight=1)

            self.entity_data_close_button = ttk.Button(
                button_row, text="Close", command=self.view_popup.destroy
            )
            self.entity_data_close_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

            self.entity_data_save_button = ttk.Button(
                button_row, text="Save", command=lambda: save_edits()
            )
            self.entity_data_save_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        except IndexError:
            messagebox.showerror("Error", "No entity selected.")

    def load_project(self) -> None:
        global GP_BASE_PATH, LAST_SAVE_DIR

        packed_data = sl_load_project()

        if packed_data is None:
            return

        data: dict = packed_data[0]
        file: str = packed_data[1]

        GP_BASE_PATH = str(Path(file).parent)
        LAST_SAVE_DIR = str(Path(file).parent)

        self.entities = data.get("entities", {})
        game = data.get("game", {})
        self.game_dimensions = game.get("dimensions", [800, 600])
        self.cursor_visible = game.get("cursor_visible", True)
        self.fullscreen = game.get("fullscreen", False)
        self.project_name = data.get("name", "Untitled Project")
        self.project_name_input.delete(0, tk.END)
        self.project_name_input.insert(0, self.project_name)
        self.entity_list.delete(0, tk.END)

        for entity_name in self.entities.keys():
            self.entity_list.insert(tk.END, entity_name)

        messagebox.showinfo("Success", "Project loaded successfully.")
        self.game_menu.entryconfig("Build Game", state=NORMAL)

    def save_project(self) -> None:
        global GP_BASE_PATH, LAST_SAVE_DIR

        if LAST_SAVE_DIR is None:
            self.save_project_as()
            return

        file = sl_save_project(self, dir_str=LAST_SAVE_DIR)

        if file is None:
            return

        GP_BASE_PATH = str(Path(file).parent)
        LAST_SAVE_DIR = str(Path(file).parent)

    def save_project_as(self) -> None:
        global GP_BASE_PATH, LAST_SAVE_DIR

        file = sl_save_project(self)

        if file is None:
            return

        GP_BASE_PATH = str(Path(file).parent)
        LAST_SAVE_DIR = str(Path(file).parent)
        self.game_menu.entryconfig("Build Game", state=NORMAL)

    def save_name(self, name: str) -> None:
        self.project_name = name
        messagebox.showinfo("Info", f"Project name set to: {self.project_name}")

    def _reload_scripts(self) -> None:
        """
        Forget the scripts the last run loaded, so this run reads them again.

        Scripts get edited outside the editor while it stays open. Anything a
        script imports stays cached in sys.modules under its own name, and its
        compiled bytecode stays cached in __pycache__, so without clearing both
        a run keeps using whatever was on disk when the editor started.
        """

        script_dirs = {
            str(Path(script).resolve().parent)
            for script in (
                game_path(entity_data.get("scriptfile")) for entity_data in self.entities.values()
            )
            if script is not None
        }

        for name, module in list(sys.modules.items()):
            if name.split(".")[0] == "engine":
                continue

            file = getattr(module, "__file__", None)

            if file is not None and str(Path(file).resolve().parent) in script_dirs:
                del sys.modules[name]

        for script_dir in script_dirs:
            shutil.rmtree(Path(script_dir) / "__pycache__", ignore_errors=True)

    def run_game(self, is_editor: bool = True) -> None:
        self._reload_scripts()

        self.core_game = CoreGame(
            self.project_name,
            width=self.game_dimensions[0],
            height=self.game_dimensions[1],
            cursor_visible=self.cursor_visible,
            fullscreen=self.fullscreen,
            IS_EDITOR=is_editor,
            GP_BASE_PATH=GP_BASE_PATH,
        )

        for _entity_name, entity_data in self.entities.items():
            scriptfile = game_path(entity_data.get("scriptfile", None))
            image_path = entity_data.get("image")

            if image_path:
                image = game_path(image_path)
            else:
                image = None

            entity = Entity(
                x=entity_data.get("x", 0),
                y=entity_data.get("y", 0),
                width=entity_data.get("width", 50),
                height=entity_data.get("height", 50),
                color=tuple(entity_data.get("color", (255, 255, 255))),
                scriptfile=scriptfile,
                image=image,
            )
            self.core_game.add_to_current_scene(entity)

        def run_core_game() -> None:
            if self.core_game is None:
                return

            self.core_game.run()

        run_core_game()

    def run(self) -> None:
        self.root.mainloop()

    def quit(self) -> None:
        self.root.quit()
        sys.exit()


def run() -> None:
    editor = Editor()
    editor.run()
