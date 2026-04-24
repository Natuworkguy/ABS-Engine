# Copyright (C) Above and Below Studios
# See the LICENSE file for GPLv3

import sys
import os
import json

import tkinter as tk
from tkinter import DISABLED, NORMAL, ttk
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
from _tkinter import TclError

from typing import Optional
from io import TextIOWrapper

from .saveload import save_project as sl_save_project, load_project as sl_load_project, resource_path
from .core import Game as CoreGame, Entity
from .logger import logger, Status as LoggerStatus
from .build_tools import build
from .tcl_loader import tcl_source

from pathlib import Path

GP_BASE_PATH: str = str(Path(__file__).parent)
ENGINE_DATA_PATH = resource_path("data")

def game_path(relative: Optional[str]) -> Optional[str]:
    if relative is None:
        return

    return os.path.join(str(GP_BASE_PATH), relative)


class Engine:
    root: tk.Tk
    abs_section: tk.LabelFrame
    exit_button: ttk.Button
    view_popup: Optional[tk.Toplevel]
    entity_data: Optional[tk.Text]

    def __init__(self) -> None:
        self.core_game = None
        self.view_popup = None
        self.game_settings_popup = None
        self.entity_data = None

        self.project_name = "Untitled Project"
        self.game_dimensions = [800, 600]
        self.entities = {}

        self.root = tk.Tk()
        self.root.title("ABS Engine")
        self.root.geometry("530x700")
        self.load_theme()

        if '-noicon' not in sys.argv:
            try:
                self.root.iconphoto(True, tk.PhotoImage(file=os.path.join(ENGINE_DATA_PATH, "images", "abs_icon.png")))
            except TclError as e:
                logger("Could not load icon image.", status=LoggerStatus.CRITICAL)
                logger("Try running with the -noicon flag if this persists.", status=LoggerStatus.CRITICAL)
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
            command=lambda: self.save_name(self.project_name_input.get())
        )
        self.name_save_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.project_separator = ttk.Separator(self.project_section, orient='vertical')
        self.project_separator.pack(side=tk.LEFT, fill='y', padx=5, pady=5)

        self.project_save_button = ttk.Button(
            self.project_section,
            text="Save Project",
            command=self.save_project
        )
        self.project_save_button.pack(padx=5, pady=5)

        self.project_load_button = ttk.Button(
            self.project_section,
            text="Load Project",
            command=lambda: self.load_project()
        )
        self.project_load_button.pack(padx=5, pady=5)

        self.entities_section = tk.LabelFrame(self.root, width=200, height=200, text="Entities")
        self.entities_section.pack(fill="both", padx=5, pady=5)

        self.entity_list_label = tk.Label(self.entities_section, text="Entity List")
        self.entity_list_label.pack(padx=5, pady=5)

        self.entity_list = tk.Listbox(self.entities_section, height=5, selectmode=tk.SINGLE)
        self.entity_list.pack(padx=5, pady=5)

        self.view_entity_button = ttk.Button(
            self.entities_section,
            text="Edit Data",
            command=lambda: self.view_entity(self.entity_list)
        )
        self.view_entity_button.pack(padx=5, pady=5)

        self.delete_entity_button = ttk.Button(
            self.entities_section,
            text="Rename Entity",
            command=self.rename_entity
        )
        self.delete_entity_button.pack(padx=5, pady=5)

        self.delete_entity_button = ttk.Button(
            self.entities_section,
            text="Delete Entity",
            command=self.delete_entity
        )
        self.delete_entity_button.pack(padx=5, pady=5)

        self.entity_separator = ttk.Separator(self.entities_section, orient='horizontal')
        self.entity_separator.pack(fill='x', padx=5, pady=10)

        self.add_entity_input = ttk.Entry(self.entities_section)
        self.add_entity_input.pack(padx=5, pady=5)

        self.add_entity_button = ttk.Button(
            self.entities_section,
            text="Add Entity",
            command=lambda: self.add_entity(self.add_entity_input.get())
        )
        self.add_entity_button.pack(padx=5, pady=5)

        self.engine_section = tk.LabelFrame(self.root, width=200, height=200, text="Engine")
        self.engine_section.pack(fill="both", padx=5, pady=5)

        self.run_game_button = ttk.Button(self.engine_section, text='Run Game', command=self.run_game, width=25)
        self.run_game_button.pack(padx=5, pady=5)

        self.build_game_button = ttk.Button(self.engine_section, text='Build Game', command=self.build_game, width=25, state=DISABLED)
        self.build_game_button.pack(padx=5, pady=5)

        self.game_settings_button = ttk.Button(self.engine_section, text="Game Settings", command=self.game_settings, width=25)
        self.game_settings_button.pack(padx=5, pady=5)

        self.exit_button = ttk.Button(self.engine_section, text='Exit', command=self.quit, width=25)
        self.exit_button.pack(padx=5, pady=5)

    def load_theme(self) -> None:
        try:
            tcl_source("theme.tcl", self.root)
        except TclError as e:
            logger("Failed to load theme.", status=LoggerStatus.WARNING)
            logger(f"Error: {e}", status=LoggerStatus.WARNING)

    def build_game(self) -> None:
        do_build = messagebox.askyesno("Build Tools | ABS Engine", "This will build to the folder containing the .absp project file. Do you want to continue?")

        if not do_build:
            return

        logger("Build Tools: Starting build")

        build(Path(GP_BASE_PATH), ENGINE_DATA_PATH=ENGINE_DATA_PATH)

        logger("Build Tools: Waiting for root")
        self.root.after(3000, lambda: None)
        logger("Build Tools: Build completed")
        messagebox.showinfo("Build Tools | ABS Engine", "The build has been completed.")

    def game_settings(self) -> None:
        self.game_settings_popup = tk.Toplevel(self.root, height=150)
        self.game_settings_popup.wm_title("Game Settings | ABS Engine")

        self.game_settings_dimensions_section = ttk.LabelFrame(self.game_settings_popup, width=200, height=100, text="Dimensions")
        self.game_settings_dimensions_section.pack(padx=5, pady=5)

        self.game_settings_width_label = ttk.Label(self.game_settings_dimensions_section, text="Width")
        self.game_settings_width_label.pack(padx=5, pady=5)
        self.game_settings_width = ttk.Entry(self.game_settings_dimensions_section)
        self.game_settings_width.pack(padx=5, pady=5)
        self.game_settings_width.insert(tk.END, str(self.game_dimensions[0]))

        self.game_settings_height_label = ttk.Label(self.game_settings_dimensions_section, text="Height")
        self.game_settings_height_label.pack(padx=5, pady=5)
        self.game_settings_height = ttk.Entry(self.game_settings_dimensions_section)
        self.game_settings_height.pack(padx=5, pady=5)
        self.game_settings_height.insert(tk.END, str(self.game_dimensions[1]))

        def game_settings_dimensions_save() -> None:
            width = self.game_settings_width.get()
            height = self.game_settings_height.get()

            if self.game_settings_popup is not None:
                self.game_settings_popup.destroy()

            if width != '':
                try:
                    self.game_dimensions[0] = int(width)
                except ValueError:
                    messagebox.showerror("Error", "Width value must be an integer.")
                    return

            if height != '':
                try:
                    self.game_dimensions[1] = int(height)
                except ValueError:
                    messagebox.showerror("Error", "Width value must be an integer.")
                    return

            messagebox.showinfo("Success", "Settings saved")

        self.game_settings_dimensions_save_button = ttk.Button(self.game_settings_dimensions_section, text="Save and Close", command=game_settings_dimensions_save)
        self.game_settings_dimensions_save_button.pack(padx=5, pady=5)

    def delete_entity(self) -> None:
        try:
            selected_item = self.entity_list.get(self.entity_list.curselection()[0])
        except IndexError:
            messagebox.showerror("Error", "No entity selected.")
            return

        do_delete: bool = messagebox.askokcancel("Delete Entity", "Are you sure you want to delete the selected entity?", icon='warning', default='cancel')

        if not do_delete:
            return

        del self.entities[selected_item]
        self.entity_list.delete(self.entity_list.curselection()[0])

    def rename_entity(self) -> None:
        try:
            raw_selected_item = self.entity_list.curselection()[0]
            selected_item = self.entity_list.get(raw_selected_item)
        except IndexError:
            messagebox.showerror("Error", "No entity selected.")
            return

        new_name = simpledialog.askstring("Rename Entity", "Enter new entity name:", initialvalue=selected_item)

        if new_name is None:
            return

        if new_name.strip() == '':
            messagebox.showerror("Error", "Entity name cannot be empty.")
            return

        self.entities[new_name] = self.entities.pop(selected_item)
        self.entity_list.delete(raw_selected_item)
        self.entity_list.insert(tk.END, new_name)

    def add_entity(self, name: str) -> None:
        if name.strip() == '':
            messagebox.showerror("Error", "Entity name cannot be empty.")
            return

        self.add_entity_input.delete(0, tk.END)

        self.entities.update({name: {}})
        self.entity_list.insert(tk.END, name)

    def view_entity(self, entity_list: tk.Listbox) -> None:
        try:
            selected_item = entity_list.get(entity_list.curselection()[0])

            self.view_popup = tk.Toplevel(self.root)
            self.view_popup.wm_title("Entity Data | ABS Engine")

            self.entity_data = tk.Text(self.view_popup, width=50, height=20)
            self.entity_data.insert(tk.END, json.dumps(self.entities[selected_item], indent=4))
            self.entity_data.pack(padx=5, pady=5)

            def save_edits() -> None:
                if self.entity_data is None:
                    return
                elif self.view_popup is None:
                    return

                try:
                    self.entities[selected_item] = json.loads(
                            self.entity_data.get("1.0", tk.END + '-1c')
                    )
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save entity data: {e}\nPlease ensure the data is in valid JSON format.")
                    self.entity_data.focus_set()

                    return

                self.view_popup.destroy()

            self.entity_data_close_button = ttk.Button(
                self.view_popup,
                text="Close",
                command=self.view_popup.destroy
            )
            self.entity_data_close_button.pack(padx=5, pady=10)

            self.entity_data_save_button = ttk.Button(
                self.view_popup,
                text="Save",
                command=lambda: save_edits()
            )
            self.entity_data_save_button.pack(padx=5, pady=10)

        except IndexError:
            messagebox.showerror("Error", "No entity selected.")
    
    def load_project(self) -> None:
        global GP_BASE_PATH

        packed_data = sl_load_project()

        if packed_data is None:
            return

        data: dict = packed_data[0]
        file: TextIOWrapper = packed_data[1]

        GP_BASE_PATH = str(Path(str(file.name)).parent)

        self.entities = data.get("entities", {})
        game = data.get("game", {})
        self.game_dimensions = game.get("dimensions", [800, 600])
        self.project_name = data.get("name", "Untitled Project")
        self.project_name_input.delete(0, tk.END)
        self.project_name_input.insert(0, self.project_name)
        self.entity_list.delete(0, tk.END)

        for entity_name in self.entities.keys():
            self.entity_list.insert(tk.END, entity_name)

        messagebox.showinfo("Success", "Project loaded successfully.")
        self.build_game_button.config(state=NORMAL)

    def save_project(self):
        global GP_BASE_PATH

        file = sl_save_project(self)

        if file is None:
            return

        GP_BASE_PATH = str(Path(str(file.name)).parent)
        self.build_game_button.config(state=NORMAL)

    def save_name(self, name: str) -> None:
        self.project_name = name
        messagebox.showinfo("Info", f"Project name set to: {self.project_name}")

    def run_game(self) -> None:
        self.core_game = CoreGame(self.project_name, width=self.game_dimensions[0], height=self.game_dimensions[1], IS_EDITOR=True)

        for entity_name, entity_data in self.entities.items():
            entity = Entity(
                x=entity_data.get("x", 0),
                y=entity_data.get("y", 0),
                width=entity_data.get("width", 50),
                height=entity_data.get("height", 50),
                color=tuple(entity_data.get("color", (255, 255, 255))),
                scriptfile=game_path(entity_data.get("scriptfile", None))
            )
            self.core_game.scene.add(entity)

        def run_core_game():
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
    engine = Engine()
    engine.run()
