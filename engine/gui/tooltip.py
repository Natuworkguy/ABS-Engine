# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Hover tooltips for tkinter widgets.
"""

import tkinter as tk

from typing import Optional


class Tooltip:
    """
    Show a small popup with ``text`` when the mouse hovers over a widget.
    """

    def __init__(self, widget: tk.Widget, text: str) -> None:
        """
        Attach a hover tooltip to ``widget``.

        Args:
            widget (tk.Widget): The widget to show the tooltip for.
            text (str): The text to display in the tooltip.
        """

        self.widget = widget
        self.text = text
        self.tip_window: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _event: "tk.Event[tk.Widget]") -> None:
        """
        Create and display the tooltip popup below the widget.

        Args:
            _event (tk.Event[tk.Widget]): The ``<Enter>`` event that triggered the tooltip.
        """

        if self.tip_window is not None:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tip_window,
            text=self.text,
            justify="left",
            background="#f0f0f0",
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=3,
        )
        label.pack()

    def _hide(self, _event: "tk.Event[tk.Widget]") -> None:
        """
        Destroy the tooltip popup, if it is currently shown.

        Args:
            _event (tk.Event[tk.Widget]): The ``<Leave>`` event that triggered the tooltip to close.
        """

        if self.tip_window is not None:
            self.tip_window.destroy()
            self.tip_window = None
