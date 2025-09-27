import tkinter as tk
from ..tools.utils import center, world_to_screen, snap_to_line
from .. import state
import math


class Lower_label:
    def __init__(
        self,
        root: tk.Tk,
        canvas: tk.Canvas,
        unit_size: int = 40,
        objects=None,
        obj=None,
    ):
        self.root = root
        self.canvas = canvas
        self.objects = objects
        self.obj = obj

        self.pos_x = 0.0
        self.pos_y = 0.0
        self.prev_x = 0.0
        self.prev_y = 0.0

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0  # zoom factor
        self.unit_size = unit_size

        self.cx = 0
        self.cy = 0

        self.is_drawable = True

        self.tag = f"lower_label_{id(self)}"

        self.canvas.bind("<Configure>", lambda e: self.update())

    def update(self, e=None):
        if self.obj is None:
            return
        self.canvas.delete(self.tag)

        visual_scale = min(max(1, self.scale**0.5), 1.9)

        from .line import Line
        from .ray import Ray

        if isinstance(self.obj, Line) or isinstance(self.obj, Ray):
            if self.obj.point_2 is None:
                return
            x1, y1 = self.obj.point_1.pos_x, self.obj.point_1.pos_y
            x2, y2 = self.obj.point_2.pos_x, self.obj.point_2.pos_y
            angle = math.atan2(y2 - y1, x2 - x1)
            span = max(self.canvas.winfo_width(), self.canvas.winfo_height()) / (
                self.unit_size * self.scale
            )
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            x, y = world_to_screen(self.objects, x2, y2)
            width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
            if angle > 0:
                if 0 < angle < math.pi / 2:
                    z = math.tan(math.pi / 2 - angle) * y
                    x += z
                    y = 10
                    if x > width - 10:
                        y = math.tan(angle) * (x - width + 10) + 20
                    x = min(x, width - 10)
                else:
                    z = math.tan(angle - math.pi / 2) * y
                    x -= z
                    y = 10
                    if x < 10:
                        y = math.tan(math.pi - angle) * (10 - x) + 20
                    x = max(10, x)
            else:
                angle *= -1
                if 0 < angle < math.pi / 2:
                    z = (height - y) / math.tan(angle)
                    x += z
                    y = height - 10
                    if x > width - 10:
                        y = height - (math.tan(angle) * (x - width + 10) + 20)
                    x = min(x, width - 10)

                else:
                    z = (height - y) / math.tan(math.pi - angle)
                    x -= z
                    y = height - 10
                    if x < 10:
                        y = height - (math.tan(math.pi - angle) * (10 - x) + 20)
                    x = max(10, x)

            self.canvas.create_text(
                x + 1 * visual_scale,
                y,
                text=self.obj.lower_label,
                font=("Arial", int(12 * visual_scale)),
                fill="blue",
                tags=self.obj.tag,
            )
