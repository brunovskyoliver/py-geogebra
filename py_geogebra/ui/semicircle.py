import tkinter as tk


from py_geogebra.ui.point import Point
from ..tools.utils import (
    snap_to_circle,
    world_to_screen,
    snap_to_circle,
    find_translation_circle,
    dot,
)
from .. import state
from .lower_label import Lower_label
from .blank_point import Blank_point
import math
from .. import globals


class Semicircle:
    def __init__(
        self,
        root: tk.Tk,
        unit_size: int = 40,
        point_1 = None,
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

        self.tag = f"semicircle_{id(self)}"
        self.center = Blank_point(self.root)
        self.point_1 = point_1
        self.point_2 = None
        self.anchor_1 = Blank_point(self.root)
        self.anchor_2 = Blank_point(self.root)
        self.selected = False
        self.translation = None

        self.radius = 0

        self.vector = []
        self.n_vector = []

        self.points : list[Point] = [self.point_1]
        self.lower_label = ""
        self.lower_label_obj = Lower_label(self.root, obj=self)
        self.objects.register(self.lower_label_obj)


    def to_dict(self) -> dict:
        return {
            "type": "Semicircle",
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
        c = cls(root=root, point_1=p1, unit_size=data.get("unit_size", 40))
        c.point_2 = p2
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

        x1, y1 = self.point_1.pos_x, self.point_1.pos_y

        if state.drag_target is self:

            x_dif, y_dif = self.prev_x - self.pos_x, self.prev_y - self.pos_y
            x2, y2 = self.point_2.pos_x, self.point_2.pos_y

            for obj in self.points:
                if (obj is self.point_1) or (obj is self.point_2):
                    obj.pos_x -= x_dif
                    obj.pos_y -= y_dif
                    x1 -= x_dif
                    y1 -= y_dif
                    x2 -= x_dif
                    y2 -= y_dif
                    continue

        else:
            if self.point_2 is None and e is None:
                return

            if self.point_2 is None:
                cx, cy = state.center
                x2 = (e.x - cx) / (self.unit_size * self.scale)
                y2 = (cy - e.y) / (self.unit_size * self.scale)
            else:
                x2, y2 = self.point_2.pos_x, self.point_2.pos_y


        angle = math.atan2(y2 - y1, x2 - x1)
        angle = (angle / 6.28) * 360

        self.radius = math.hypot(x2-x1, y2-y1) / 2

        cx =( x1 + x2) / 2
        cy = (y1 + y2) / 2

        self.center.pos_x = cx
        self.center.pos_y = cy

        self.anchor_1.pos_x, self.anchor_1.pos_y = cx - self.radius, cy - self.radius
        self.anchor_2.pos_x, self.anchor_2.pos_y = cx + self.radius, cy + self.radius

        self.vector = [self.point_2.pos_x - self.point_1.pos_x, self.point_2.pos_y - self.point_1.pos_y]
        self.n_vector = [self.vector[1], -self.vector[0]]

        for obj in self.points:
            if (obj is not self.point_1) and (obj is not self.point_2):
                dot_product = dot(self.n_vector, [obj.pos_x - self.point_1.pos_x, obj.pos_y - self.point_1.pos_y])


                if dot_product < 0:
                    obj.color = "#349AFF"
                else:
                    obj.color = "red"
                    # pridem na to jak to clampnut teraz sa mi nechce tak to bude iba cervene

                find_translation_circle(obj, self)
                snap_to_circle(obj, self)
                obj.update()



        x1, y1 = world_to_screen(self.anchor_1.pos_x, self.anchor_1.pos_y)
        x2, y2 = world_to_screen(self.anchor_2.pos_x, self.anchor_2.pos_y)


        if not self.point_2:
            self.is_drawable = True
        elif self.point_1.is_drawable and self.point_2.is_drawable:
            self.is_drawable = True
        else:
            self.is_drawable = False

        self.lower_label_obj.is_drawable = self.is_drawable

        if self.is_drawable:

            if self.selected:
                self.canvas.create_arc(
                    x1,
                    y1,
                    x2,
                    y2,
                    start=angle,
                    extent=180,
                    style=tk.ARC,
                    outline="lightgrey",
                    width=2*3 * visual_scale,
                    tags=self.tag,
                )

            self.canvas.create_arc(
                x1,
                y1,
                x2,
                y2,
                start=angle,
                extent=180,
                style=tk.ARC,
                outline="black",
                width=2 * visual_scale,
                tags=self.tag,
            )
        self.canvas.tag_raise(self.point_1.tag)
        if self.point_2 is not None:
            self.canvas.tag_raise(self.point_2.tag)
            if self.point_2 not in self.points:
                self.points.append(self.point_2)

        for p in self.points:
            self.canvas.tag_raise(p.tag)


        self.prev_x, self.prev_y = self.pos_x, self.pos_y
        self.canvas.tag_raise(self.lower_label_obj.tag)
