from os import confstr
import tkinter as tk
from typing import ChainMap
from ..tools.load_image import load_icon
from ..tools.utils import delete_object, set_cursor
from .. import state


class Sidebar:
    def __init__(self, root: tk.Tk, main_area: tk.Frame, widgets):
        self.frame = tk.Frame(main_area, width=200, bg="#dddddd")
        self.frame.pack_propagate(False)

        self.resizing = False
        self.items = []

    def update(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        for item in self.items:
            text = tk.Label(
                self.frame,
                text=f"{item.label} =  {round(item.pos_x, 2), round(item.pos_y, 2)}",
                fg="black",
                bg="#dddddd",
            )
            text.pack(padx=10, pady=10, anchor="nw")
