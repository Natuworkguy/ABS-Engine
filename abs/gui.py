import sys
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox

class Engine:
    root: tk.Tk
    abs_section: tk.LabelFrame
    exit_button: tk.Button

    def __init__(self) -> None:
        self.view_popup = None
        self.entity_data = None

        self.entities = {}

        self.root = tk.Tk()
        self.root.resizable(True, True)

        self.entities_section = tk.LabelFrame(self.root, width=200, height=200, text="Entities")
        self.entities_section.pack(fill="both", padx=5, pady=5)

        self.entity_list = tk.Listbox(self.entities_section, height=5, selectmode=tk.SINGLE)
        self.entity_list.pack(padx=5, pady=5)

        self.view_entity_button = ttk.Button(
            self.entities_section,
            text="View",
            command=lambda: self.view_entity(self.entity_list)
        )
        self.view_entity_button.pack(padx=5, pady=5)

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

        self.exit_button = ttk.Button(self.abs_section, text='Exit', command=self.quit, width=25)
        self.exit_button.pack(padx=5, pady=5)

    def add_entity(self, name: str) -> None:
        if name.strip() == '':
            return

        self.entities.update({name: {}})
        self.entity_list.insert(tk.END, name)

    def view_entity(self, entity_list: tk.Listbox) -> None:
        try:
            selected_item = entity_list.get(entity_list.curselection()[0])

            self.view_popup = tk.Toplevel(self.root)
            self.view_popup.wm_title("Entity Data")

            self.entity_data = ttk.Label(self.view_popup, text=self.entities[selected_item])
            self.entity_data.pack(padx=5, pady=5)

            # Add ttk close button calling self.view_popuip
        except IndexError:
            messagebox.showerror("Error", "No entity selected.")

    def run(self) -> None:
        self.root.mainloop()

    def quit(self) -> None:
        self.root.quit()
        sys.exit()


def run() -> None:
    engine = Engine()
    engine.run()
