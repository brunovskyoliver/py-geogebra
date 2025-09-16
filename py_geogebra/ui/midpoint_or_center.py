import tkinter as tk
from ..tools.utils import center, screen_to_world
from .. import state


class Midpoint_or_center:
    def __init__(
        self,
        root: tk.Tk,
        canvas: tk.Canvas,
        label: str = "",
        unit_size: int = 40,
        point_1=None,
        point_2=None,
        objects=None
    ):
        point_1.deselect()
        point_2.deselect()
        self.root = root
        self.canvas = canvas
        self.objects = objects
        self.color = "grey"
        
        self.point_1 = point_1
        self.point_2 = point_2

        self.pos_x = 0
        self.pos_y = 0
        self.label = label

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0  # zoom factor
        self.unit_size = unit_size

        self.cx = 0
        self.cy = 0
        self.x = 0
        self.y = 0

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

        self.x = self.point_1.x - (self.point_1.x - self.point_2.x) / 2
        self.y = self.point_1.y - (self.point_1.y - self.point_2.y) / 2
        
        cx, cy = state.center
        self.pos_x = (self.x - cx) / (self.objects.unit_size * self.objects.scale)
        self.pos_y = (cy - self.y) / (self.objects.unit_size * self.objects.scale)
        


        visual_scale = min(max(1, self.scale**0.5), 1.9)

        r = 6.0 * visual_scale

        if self.selected:
            r_h = r * 1.4
            self.canvas.create_oval(
                self.x - r_h,
                self.y - r_h,
                self.x + r_h,
                self.y + r_h,
                outline= self.color,
                width=2,
                fill="",  # no fill so it looks like a ring
                tags=(self.highlight_tag,),  # must be a tuple
            )

        self.canvas.create_oval(
            self.x - r, self.y - r, self.x + r, self.y + r, fill=self.color, width=2, tags=(self.tag, "point")
        )

        if self.label:
            self.canvas.create_text(
                self.x + 10 * visual_scale,
                self.y - 15 * visual_scale,
                text=self.label,
                font=("Arial", int(12 * visual_scale)),
                fill="blue",
                tags=self.tag,
            )
