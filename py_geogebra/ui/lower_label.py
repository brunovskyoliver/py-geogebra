import tkinter as tk
from types import NoneType

from py_geogebra.ui import compass

from ..tools.utils import world_to_screen
from .. import globals
import math


class Lower_label:
    def __init__(
        self,
        root: tk.Tk,
        unit_size: int = 40,
        obj=None,
    ):
        self.root = root
        self.canvas = globals.canvas
        self.objects = globals.objects
        self.obj = obj
        self.scale = 1.0  # zoom factor
        self.unit_size = unit_size
        self.tag = f"lower_label_{id(self)}"
        self.canvas.bind("<Configure>", lambda e: self.update())
        self.is_drawable = True

    def to_dict(self) -> dict:
        return {
            "type": "Lower Label",
            "unit_size": self.unit_size,
            "scale": self.scale,
            "tag": self.tag,
            "parent_tag": getattr(self.obj, "tag", None),
        }

    @classmethod
    def from_dict(cls, root, data: dict):
        parent = None
        if "parent_tag" in data:
            for obj in globals.objects._objects:
                if getattr(obj, "tag", None) == data["parent_tag"]:
                    parent = obj
                    break

        ll = cls(
            root=root,
            unit_size=data.get("unit_size", 40),
            obj=parent,
        )
        ll.scale = data.get("scale", 1.0)
        ll.tag = data.get("tag", f"lower_label_{id(ll)}")
        globals.objects.register(ll)
        return ll

    def update(self, e=None):
        if self.obj is None or not self.is_drawable:
            return
        self.canvas.delete(self.tag)

        visual_scale = min(max(1, self.scale**0.5), 1.9)

        from .line import Line
        from .ray import Ray
        from .segment import Segment
        from .vector import Vector
        from .vector_from_point import Vector_from_point
        from .segment_with_lenght import Segment_with_length
        from .perpendicular_bisector import Perpendicular_bisector
        from .parallel_line import Parallel_line
        from .perpendicular_line import Perpendicular_line
        from .best_fit_line import Best_fit_line
        from .polyline import Polyline
        from .circle_center_point import Circle_center_point
        from .circle_center_radius import Circle_center_radius
        from .compass import Compass

        if (isinstance(self.obj, Line)
            or isinstance(self.obj, Ray)
            or isinstance(self.obj, Perpendicular_bisector)
            or isinstance(self.obj, Parallel_line)
            or isinstance(self.obj, Perpendicular_line)
            or isinstance(self.obj, Best_fit_line)
            ):
            if self.obj.point_2 is None:
                return
            x2, y2 = self.obj.point_2.pos_x, self.obj.point_2.pos_y
            angle = self.obj.angle
            x, y = world_to_screen(x2, y2)
            if isinstance(self.obj, Perpendicular_bisector):
                x,y = world_to_screen(*self.obj.middle)
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
        elif isinstance(self.obj, Segment) or isinstance(self.obj, Segment_with_length) or isinstance(self.obj, Vector) or isinstance(self.obj, Vector_from_point):
            if self.obj.point_2 is None:
                return
            middle_x = (
                self.obj.point_1.x - (self.obj.point_1.x - self.obj.point_2.x) / 2
            )
            middle_y = (
                self.obj.point_1.y - (self.obj.point_1.y - self.obj.point_2.y) / 2
            )
            dx = self.obj.point_2.x - self.obj.point_1.x
            dy = self.obj.point_2.y - self.obj.point_1.y
            length = math.hypot(dx, dy)
            if length == 0:
                return
            perp_x = -dy / length
            perp_y = dx / length
            self.canvas.create_text(
                middle_x + perp_x * visual_scale * 15,
                middle_y + perp_y * visual_scale * 15,
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

        elif (isinstance(self.obj, Circle_center_point) or
            isinstance(self.obj, Circle_center_radius) or
            isinstance(self.obj, Compass)
            ):
            if not self.obj.is_drawable:
                return

            angle = 1 # it is in radians
            pos = [self.obj.radius, 0]
            matrix = [[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]]
            pos = [matrix[0][0] * pos[0] + matrix[0][1] * pos[1], matrix[1][0] * pos[0] + matrix[1][1] * pos[1]]



            self.canvas.create_text(
                world_to_screen(pos[0] * visual_scale + self.obj.point_1.pos_x - 0.1, pos[1] * visual_scale + self.obj.point_1.pos_y - 0.1),
                text=self.obj.lower_label,
                font=("Arial", int(12 * visual_scale)),
                fill="blue",
                tags=self.tag,
            )
