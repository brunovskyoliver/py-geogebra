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
        self.scale = 1.0  # zoom factor
        self.unit_size = unit_size
        self.tag = f"lower_label_{id(self)}"
        self.canvas.bind("<Configure>", lambda e: self.update())

    def update(self, e=None):
        if self.obj is None:
            return
        self.canvas.delete(self.tag)

        visual_scale = min(max(1, self.scale**0.5), 1.9)

        from .line import Line
        from .ray import Ray
        from .segment import Segment
        from .segment_with_lenght import Segment_with_length
        from .polyline import Polyline

        if isinstance(self.obj, Line) or isinstance(self.obj, Ray):
            if self.obj.point_2 is None:
                return
            x1, y1 = self.obj.point_1.pos_x, self.obj.point_1.pos_y
            x2, y2 = self.obj.point_2.pos_x, self.obj.point_2.pos_y
            angle = self.obj.angle
            span = max(self.canvas.winfo_width(), self.canvas.winfo_height()) / (
                self.unit_size * self.scale
            )
            x, y = world_to_screen(x2, y2)
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
                tags=(self.obj.tag, self.tag),
            )
        elif isinstance(self.obj, Segment) or isinstance(self.obj, Segment_with_length):
            if self.obj.point_2 is None:
                return
            middle_x = (
                self.obj.point_1.x - (self.obj.point_1.x - self.obj.point_2.x) / 2
            )
            middle_y = (
                self.obj.point_1.y - (self.obj.point_1.y - self.obj.point_2.y) / 2
            )
            self.canvas.create_text(
                middle_x + 1 * visual_scale,
                middle_y - 15 * visual_scale,
                text=self.obj.lower_label,
                font=("Arial", int(12 * visual_scale)),
                fill="blue",
                tags=(self.obj.tag, self.tag),
            )
        elif isinstance(self.obj, Polyline):
            if self.obj.last_not_set or not self.obj.line_points:
                return
            mid = self.obj.line_points[len(self.obj.line_points) // 2]
            self.canvas.create_text(
                mid.x - 3 * visual_scale,
                mid.y + 25 * visual_scale,
                text=self.obj.lower_label,
                font=("Arial", int(12 * visual_scale)),
                fill="blue",
                tags=self.tag,
            )
