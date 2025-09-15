import tkinter as tk
from ..tools.utils import center, world_to_screen
from .. import state
import math


class Segment_with_length:
    def __init__(
        self,
        root: tk.Tk,
        canvas: tk.Canvas,
        unit_size: int = 40,
        point_1=None,
        point_2=None,
        length: float = 1.0,
        angle: float = 0.0,
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
        
        self.length = length
        self.angle = angle

        self.tag = f"line_{id(self)}"
        self.point_1 = point_1
        self.point_2 = point_2

        self.canvas.bind("<Configure>", lambda e: self.update())

    def update(self, e=None):
        self.canvas.delete(self.tag)

        visual_scale = min(max(1, self.scale**0.5), 1.9)
        if (state.drag_target is self.point_2):
            self.angle = math.atan2(self.point_2.pos_y - self.point_1.pos_y, self.point_2.pos_x - self.point_1.pos_x)

        x1, y1 = self.point_1.pos_x, self.point_1.pos_y
        self.point_2.pos_x = x1 + self.length * math.cos(self.angle) / (self.unit_size)
        self.point_2.pos_y = y1 + self.length * math.sin(self.angle) / (self.unit_size)
        x2, y2 = self.point_2.pos_x, self.point_2.pos_y
        self.point_2.update()  
        

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


