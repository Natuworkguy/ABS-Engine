# Copyright (C) Above and Below Studios
# See the LICENSE file for GPLv3

import sys
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
from pprint import pformat
from typing import Optional
from .saveload import save_project, load_project as sl_load_project, resource_path
from .core import Game as CoreGame, Entity
import threading


class Engine:
    root: tk.Tk
    abs_section: tk.LabelFrame
    exit_button: ttk.Button
    view_popup: Optional[tk.Toplevel]
    entity_data: Optional[tk.Text]

    def __init__(self) -> None:
        self.core_game = None
        self.entity_data_save_button = None
        self.entity_data_close_button = None
        self.view_popup = None
        self.entity_data = None

        self.project_name = "Untitled Project"
        self.entities = {}

        self.root = tk.Tk()
        self.root.title("ABS Engine")
        self.root.geometry("450x600")

        if not '-noicon' in sys.argv:
            try:
                self.root.iconphoto(True, tk.PhotoImage(file=resource_path("assets/icon.png")))
            except tk.TclError:
                print("Warning: Could not load icon image.")
                print("Try running with the -noicon flag if this persists.")
                raise

        self.root.resizable(False, False)

        self.project_section = tk.LabelFrame(self.root, width=200, height=100, text="Project")
        self.project_section.pack(fill="both", padx=5, pady=5)

        self.project_name_label = tk.Label(self.project_section, text="Project Name: ")
        self.project_name_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.project_name_input = tk.Entry(self.project_section)
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
            command=lambda: save_project(self)
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

        self.add_entity_input = tk.Entry(self.entities_section)
        self.add_entity_input.pack(padx=5, pady=5)

        self.add_entity_button = ttk.Button(
            self.entities_section,
            text="Add Entity",
            command=lambda: self.add_entity(self.add_entity_input.get())
        )
        self.add_entity_button.pack(padx=5, pady=5)

        self.abs_section = tk.LabelFrame(self.root, width=200, height=200, text="ABS")
        self.abs_section.pack(fill="both", padx=5, pady=5)

        self.run_button = ttk.Button(self.abs_section, text='Run', command=self.run_game, width=25)
        self.run_button.pack(padx=5, pady=5)

        self.exit_button = ttk.Button(self.abs_section, text='Exit', command=self.quit, width=25)
        self.exit_button.pack(padx=5, pady=5)

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
            self.view_popup.wm_title("Entity Data")

            self.entity_data = tk.Text(self.view_popup, width=50, height=20)
            self.entity_data.insert(tk.END, pformat(self.entities[selected_item]))
            self.entity_data.pack(padx=5, pady=5)

            def save_edits() -> None:
                if self.entity_data == None:
                    return
                elif self.view_popup == None:
                    return

                try:
                    self.entities[selected_item] = dict(
                        eval(
                            self.entity_data.get("1.0", tk.END + '-1c')
                        )
                    )
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save entity data: {e}\nPlease ensure the data is in valid dictionary format.")
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
        data = sl_load_project()
        if data is None:
            return

        self.entities = data.get("entities", {})
        self.project_name = data.get("name", "Untitled Project")
        self.project_name_input.delete(0, tk.END)
        self.project_name_input.insert(0, self.project_name)
        self.entity_list.delete(0, tk.END)

        for entity_name in self.entities.keys():
            self.entity_list.insert(tk.END, entity_name)

        messagebox.showinfo("Success", "Project loaded successfully.")

    def save_name(self, name: str) -> None:
        self.project_name = name
        messagebox.showinfo("Info", f"Project name set to: {self.project_name}")

    def run_game(self) -> None:
        self.core_game = CoreGame(title=self.project_name)

        for entity_name, entity_data in self.entities.items():
            entity = Entity(
                x=entity_data.get("x", 0),
                y=entity_data.get("y", 0),
                width=entity_data.get("width", 50),
                height=entity_data.get("height", 50),
                color=tuple(entity_data.get("color", (255, 255, 255))),
                scriptfile=entity_data.get("scriptfile", None)
            )
            self.core_game.scene.add(entity)

        def run_core_game():
            if self.core_game is None:
                return

            self.core_game.run()

        game_thread = threading.Thread(target=run_core_game, daemon=True)
        game_thread.run()

    def run(self) -> None:
        self.root.mainloop()

    def quit(self) -> None:
        self.root.quit()
        sys.exit()


def run() -> None:
    engine = Engine()
    engine.run()
