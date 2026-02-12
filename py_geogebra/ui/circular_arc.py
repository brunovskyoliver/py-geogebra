import tkinter as tk


from py_geogebra.ui.line import Line
from py_geogebra.ui.point import Point
from ..tools.utils import (
    screen_to_world,
    snap_to_circle,
    world_to_screen,
    snap_to_circle,
    find_translation_circle,
    dot,
    distance,
)
from .. import state
from .lower_label import Lower_label
from .blank_point import Blank_point
import math
from .. import globals


class Circular_arc:
    def __init__(
        self,
        root: tk.Tk,
        unit_size: int = 40,
    ):
        self.root = root
        self.canvas = globals.canvas
        self.objects = globals.objects

        self.pos_x = 0.0
        self.pos_y = 0.0
        self.prev_x = 0.0
        self.prev_y = 0.0

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0  # zoom factor
        self.unit_size = unit_size

        self.is_drawable = True

        self.tag = f"circular_arc{id(self)}"
        self.center = None
        self.point_1 = None
        self.point_2 = None
        self.selected = False
        self.translation = None

        self.radius = 0

        self.vector = []
        self.n_vector = []

        self.points : list[Point] = []
        self.lower_label = ""
        self.lower_label_obj = Lower_label(self.root, obj=self)
        self.objects.register(self.lower_label_obj)


    def to_dict(self) -> dict:
        return {
            "type": "Circular_arc",
            "lower_label": self.lower_label,
            "pos_x": self.pos_x,
            "pos_y": self.pos_y,
            "unit_size": self.unit_size,
            "scale": self.scale,
            "is_drawable": self.is_drawable,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "tag": self.tag,
            "points": [p.label for p in self.points],
            "point_1": self.point_1.label if self.point_1 else None,
            "point_2": self.point_2.label if self.point_2 else None,
            "center": self.center.label if self.center else None,
        }

    @classmethod
    def from_dict(cls, root, data: dict):
        def find_point(label):
            for obj in globals.objects._objects:
                if getattr(obj, "label", None) == label:
                    return obj
            return None

        p1 = find_point(data.get("point_1"))
        p2 = find_point(data.get("point_2"))
        pc = find_point(data.get("center"))
        c = cls(root=root, unit_size=data.get("unit_size", 40))
        c.point_1 = p1
        c.point_2 = p2
        c.center = pc
        c.scale = data.get("scale", 1.0)
        c.is_drawable = data.get("is_drawable", True)
        c.offset_x = data.get("offset_x", 0)
        c.offset_y = data.get("offset_y", 0)
        c.lower_label = data.get("lower_label", "")
        c.tag = data.get("tag", "")
        c.pos_x = data.get("pos_x", 0)
        c.pos_y = data.get("pos_y", 0)
        c.points = [find_point(lbl) for lbl in data.get("points", []) if lbl]
        c.update()
        return c

    def select(self):
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def update(self, e=None):
        self.canvas.delete(self.tag)

        visual_scale = min(max(1, self.scale**0.5), 1.9)




        if state.drag_target is self:
            x_dif, y_dif = self.prev_x - self.pos_x, self.prev_y - self.pos_y

            for obj in self.points:
                if (obj is self.point_1) or (obj is self.point_2) or (obj is self.center):
                    obj.pos_x -= x_dif
                    obj.pos_y -= y_dif
                    continue

        x2, y2 = world_to_screen(self.point_2.pos_x, self.point_2.pos_y)
        x1, y1 = world_to_screen(self.point_1.pos_x, self.point_1.pos_y)
        x_c, y_c = world_to_screen(self.center.pos_x, self.center.pos_y)

        angle = -math.atan2(y1 - y_c, x1 - x_c)
        angle = (angle / 6.28) * 360
        vec1 = (x1 - x_c, y1 - y_c)
        vec2 = (x2 - x_c, y2 - y_c)
        angle_between = math.acos((vec1[0]*vec2[0] + vec1[1]*vec2[1]) / (distance(x_c, y_c, x1, y1) * distance(x_c, y_c, x2, y2)))
        angle_between = (angle_between / 6.28) * 360
        if (dot(vec1, (vec2[1], -vec2[0]))) > 0:
            angle_between = 360 - angle_between


        self.radius = distance(x_c, y_c, x1, y1)

        sqaure_x = x_c + self.radius
        sqaure_y = y_c + self.radius
        square_x2 = x_c - self.radius
        square_y2 = y_c - self.radius


        for obj in self.points:
            if (obj is not self.point_1) and (obj is not self.point_2) and (obj is not self.center):

                find_translation_circle(obj, self)
                snap_to_circle(obj, self)
                obj.update()

        if self.is_drawable:

            if self.selected:
                self.canvas.create_arc(
                    sqaure_x,
                    sqaure_y,
                    square_x2,
                    square_y2,
                    start=angle,
                    extent=angle_between,
                    style=tk.ARC,
                    outline="lightgrey",
                    width=2 * 3 * visual_scale,
                    tags=self.tag,
                )


            self.canvas.create_arc(
                sqaure_x,
                sqaure_y,
                square_x2,
                square_y2,
                start=angle,
                extent=angle_between,
                style=tk.ARC,
                outline="black",
                width=2 * visual_scale,
                tags=self.tag,
            )

        if self.center and self.center not in self.points:
            self.points.append(self.center)
        if self.point_1 and self.point_1 not in self.points:
            self.points.append(self.point_1)
        if self.point_2 and self.point_2 not in self.points:
            self.points.append(self.point_2)


        for p in self.points:
            self.canvas.tag_raise(p.tag)


        self.prev_x = self.pos_x
        self.prev_y = self.pos_y
