import tkinter as tk
from tkinter import font as tkfont
from ..ui.point import Point
from ..ui.line import Line
from ..ui.segment import Segment
from ..ui.polyline import Polyline
from ..ui.polygon import Polygon
from ..ui.ray import Ray
from ..ui.perpendicular_bisector import Perpendicular_bisector


class Sidebar:
    def __init__(self, root: tk.Tk, main_area: tk.Frame, width=200):
        self.frame = tk.Frame(main_area, width=width, bg="#dddddd")
        self.frame.pack_propagate(False)

        self.resizing = False
        self.items = []
        self.base_font_size = 16
        self.font_family = "Calibri, mathsans, sans-serif"
        self.font = tkfont.Font(family=self.font_family, size=self.base_font_size)

        self.frame.bind("<Configure>", self._on_resize)

    def to_dict(self) -> dict:
        return {
            "type": "Sidebar",
            "width": self.frame.winfo_width(),
            "order": [item.tag for item in self.items],
        }

    def load_from_dict(self, data: dict):
        if not data:
            return
        self.resize(data.get("width", 200))
        self.update()

    def resize(self, width):
        self.frame.configure(width=width)
        self.frame.pack_propagate(False)
        self.frame.update_idletasks()

    def _on_resize(self, event):
        new_width = event.width
        base_width = 200
        scale = new_width / base_width
        new_size = max(10, int(self.base_font_size * scale))
        self.font.configure(size=new_size)

        for widget in self.frame.winfo_children():
            widget.configure(font=self.font)

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
            elif isinstance(item, Line):
                a, b, c = item.prescription
                sign_a = "-" if a < 0 else ""
                sign_b = "-" if b < 0 else "+"
                text = tk.Label(
                    self.frame,
                    text=(
                        f"{item.lower_label}: Line({item.point_1.label}, {item.point_2.label})\n"
                        f"= {sign_a}{abs(a)}x {sign_b} {abs(b)}y = {c}"
                    ),
                    fg="black",
                    bg="#dddddd",
                    justify="left",
                    anchor="nw",
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

            elif isinstance(item, Ray):
                a, b, c = item.prescription
                sign_a = "-" if a < 0 else ""
                sign_b = "-" if b < 0 else "+"
                text = tk.Label(
                    self.frame,
                    text=(
                        f"{item.lower_label}: Ray({item.point_1.label}, {item.point_2.label})\n"
                        f"= {sign_a}{abs(a)}x {sign_b} {abs(b)}y = {c}"
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
                        f"{item.lower_label} = Polyline({', '.join(p.label for p in item.line_points)})\n"
                        f"{' ' * (len(item.lower_label)-1)}= {round(item.length, 2)}"
                    ),
                    fg="black",
                    bg="#dddddd",
                    justify="left",
                    anchor="nw",
                    font=self.font,
                )
                text.pack(padx=10, pady=10, anchor="nw")
            elif isinstance(item, Polygon):
                text = tk.Label(
                    self.frame,
                    text=(
                        f"{item.lower_label} = Polygon({', '.join(p.label for p in item.line_points)})\n"
                        f"{' ' * (len(item.lower_label)-1)}= {round(item.length, 2)}"
                    ),
                    fg="black",
                    bg="#dddddd",
                    justify="left",
                    anchor="nw",
                    font=self.font,
                )
                text.pack(padx=10, pady=10, anchor="nw")


            elif isinstance(item, Perpendicular_bisector):
                a, b, c = item.prescription
                sign_a = "-" if a < 0 else ""
                sign_b = "-" if b < 0 else "+"
                text = tk.Label(
                    self.frame,
                    text=(
                        f"{item.lower_label}: PerpendicularBisector({item.point_1.label}, {item.point_2.label})\n"
                        f"= {sign_a}{abs(a)}x {sign_b} {abs(b)}y = {c}"
                    ),
                    fg="black",
                    bg="#dddddd",
                    justify="left",
                    anchor="nw",
                    font=self.font,
                )
                text.pack(padx=10, pady=10, anchor="nw")

