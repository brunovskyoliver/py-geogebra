import tkinter as tk
from ..tools.utils import center


class Point:
    def __init__(
        self,
        root: tk.Tk,
        canvas: tk.Canvas,
        label: str = "",
        unit_size: int = 40,
        pos_x: int = 0,
        pos_y: int = 0,
        color = "blue",
    ):

        self.root = root
        self.canvas = canvas
        self.color = color

        self.pos_x = pos_x
        self.pos_y = pos_y
        self.label = label

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0  # zoom factor
        self.unit_size = unit_size

        self.cx = 0
        self.cy = 0
        self.x = 0
        self.y = 0
        
        self.translation = 0

        self.tag = f"point_{id(self)}"
        self.selected = False
        self.highlight_tag = f"{self.tag}_highlight"


    def select(self):
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def update(self):
        self.canvas.delete(self.tag)
        self.canvas.delete(self.highlight_tag)

        x = self.cx + self.pos_x * self.unit_size * self.scale
        y = self.cy - self.pos_y * self.unit_size * self.scale
        self.x, self.y = x, y


        visual_scale = min(max(1, self.scale**0.5), 1.9)

        r = 6.0 * visual_scale

        if self.selected:
            r_h = r * 1.4
            self.canvas.create_oval(
                x - r_h,
                y - r_h,
                x + r_h,
                y + r_h,
                outline=self.color,
                width=2,
                fill="",  # no fill so it looks like a ring
                tags=(self.highlight_tag,),  # must be a tuple
            )

        self.canvas.create_oval(
            x - r, y - r, x + r, y + r, fill=self.color, width=2, tags=(self.tag, "point")
        )

        if self.label:
            self.canvas.create_text(
                x + 10 * visual_scale,
                y - 15 * visual_scale,
                text=self.label,
                font=("Arial", int(12 * visual_scale)),
                fill="blue",
                tags=self.tag,
            )
