import tkinter as tk
from ..tools.utils import center, world_to_screen
from .. import state
import math


class Line:
    def __init__(
        self,
        root: tk.Tk,
        canvas: tk.Canvas,
        unit_size: int = 40,
        point_1=None,
        objects=None,
    ):
        self.root = root
        self.canvas = canvas
        self.objects = objects

        self.pos_x = 0.0
        self.pos_y = 0.0

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0  # zoom factor
        self.unit_size = unit_size

        self.cx = 0
        self.cy = 0

        self.tag = f"line_{id(self)}"
        self.point_1 = point_1
        self.point_2 = None

        self.canvas.bind("<Configure>", lambda e: self.update())

    def update(self, e=None):
        self.canvas.delete(self.tag)

        visual_scale = min(max(1, self.scale**0.5), 1.9)

        x1, y1 = self.point_1.pos_x, self.point_1.pos_y

        if self.point_2 is None and e is None:
            return

        if self.point_2 is None:
            cx, cy = center(self.canvas, self.objects)
            x2 = (e.x - cx) / (self.unit_size * self.scale)
            y2 = (cy - e.y) / (self.unit_size * self.scale)
        else:
            x2, y2 = self.point_2.pos_x, self.point_2.pos_y

        angle = math.atan2(y2 - y1, x2 - x1)
        span = (
            max(self.canvas.winfo_width(), self.canvas.winfo_height())
            * 10
            / (self.unit_size * self.scale)
        )
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        x1 -= span * cos_a
        y1 -= span * sin_a
        x2 += span * cos_a
        y2 += span * sin_a

        x1, y1 = world_to_screen(self.canvas, self.objects, x1, y1)
        x2, y2 = world_to_screen(self.canvas, self.objects, x2, y2)

        self.canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            fill="black",
            width=2 * visual_scale,
            tags=self.tag,
        )
        self.canvas.tag_raise(self.point_1.tag)
