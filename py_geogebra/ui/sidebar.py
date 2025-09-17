import tkinter as tk
from ..tools.load_image import load_icon
from ..tools.utils import delete_object, set_cursor
from .. import state
from ..ui.point import Point
from ..ui.line import Line
from ..ui.segment import Segment
from ..ui.polyline import Polyline


class Sidebar:
    def __init__(self, root: tk.Tk, main_area: tk.Frame, widgets):
        self.frame = tk.Frame(main_area, width=200, bg="#dddddd")
        self.frame.pack_propagate(False)

        self.resizing = False
        self.items = []
        self.font = ("mathsans, Calibri, sans-serif", 16)

    def update(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        for item in self.items:
            if isinstance(item, Point):
                text = tk.Label(
                    self.frame,
                    text=f"{item.label} =  {round(item.pos_x,2), round(item.pos_y,2)}",
                    fg="black",
                    bg="#dddddd",
                    font=self.font,
                )
                text.pack(padx=10, pady=10, anchor="nw")
            elif isinstance(item, Segment):
                text = tk.Label(
                    self.frame,
                    text=(
                        f"{item.lower_label} = Segment({item.point_1.label}, {item.point_2.label})\n"
                        f"{' ' * (len(item.lower_label)-1)}= {item.length}"
                    ),
                    fg="black",
                    bg="#dddddd",
                    justify="left",
                    anchor="nw",
                    font=self.font,
                )
                text.pack(padx=10, pady=10, anchor="nw")
            elif isinstance(item, Polyline):
                text = tk.Label(
                    self.frame,
                    text=(
                        f"{item.lower_label} = Polyline({", ".join(p.label for p in item.points)})\n"
                        f"{' ' * (len(item.lower_label)-1)}= {round(item.length, 2)}"
                    ),
                    fg="black",
                    bg="#dddddd",
                    justify="left",
                    anchor="nw",
                    font=self.font,
                )
                text.pack(padx=10, pady=10, anchor="nw")
