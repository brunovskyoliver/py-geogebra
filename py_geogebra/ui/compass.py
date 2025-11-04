import tkinter as tk
from ..tools.utils import (
    snap_to_circle,
    world_to_screen,
    snap_to_circle,
    find_translation_circle,
    calculate_vector,
    load_lines_from_labels,
)
from .. import state
from .lower_label import Lower_label
from .blank_point import Blank_point
import math
from .. import globals


class Compass:
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

        self.cx = 0
        self.cy = 0
        self.radius = 0

        self.is_drawable = True

        self.tag = f"circle_compass_{id(self)}"
        self.point_1 = None
        self.anchor_1 = Blank_point(self.root)
        self.anchor_2 = Blank_point(self.root)
        self.r_point_1 = None
        self.r_point_2 = None
        self.selected = False
        self.translation = None

        self.points = [self.point_1]
        self.child_lines_labels = []
        self.child_lines = []
        self.lower_label = ""
        self.lower_label_obj = Lower_label(self.root, obj=self)
        self.objects.register(self.lower_label_obj)

        self.canvas.bind("<Configure>", lambda e: self.update())

    def to_dict(self) -> dict:
        return {
            "type": "Compass",
            "lower_label": self.lower_label,
            "pos_x": self.pos_x,
            "pos_y": self.pos_y,
            "unit_size": self.unit_size,
            "scale": self.scale,
            "is_drawable": self.is_drawable,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "tag": self.tag,
            "points": [p.label for p in self.points if p],
            "point_1": self.point_1.label if self.point_1 else None,
            "child_lines_labels": [l.lower_label for l in self.child_lines],
            "point_1": self.point_1.label if self.point_1 else None,
            "r_point_1": self.r_point_1.label if self.r_point_1 else None,
            "r_point_2": self.r_point_2.label if self.r_point_2 else None
        }

    @classmethod
    def from_dict(cls, root, data: dict):
        def find_point(label):
            for obj in globals.objects._objects:
                if getattr(obj, "label", None) == label:
                    return obj
            return None

        def find_line(label):
            for obj in globals.objects._objects:
                if getattr(obj, "lower_label", None) == label:
                    return obj
            return None

        p1 = find_point(data.get("point_1"))
        c = cls(root=root, unit_size=data.get("unit_size", 40))
        c.scale = data.get("scale", 1.0)
        c.is_drawable = data.get("is_drawable", True)
        c.offset_x = data.get("offset_x", 0)
        c.offset_y = data.get("offset_y", 0)
        c.lower_label = data.get("lower_label", "")
        c.tag = data.get("tag", "")
        c.pos_x = data.get("pos_x", 0)
        c.pos_y = data.get("pos_y", 0)
        c.points = [find_point(lbl) for lbl in data.get("points", []) if lbl]
        c.r_point_1 = find_point(data.get("r_point_1"))
        c.r_point_2 = find_point(data.get("r_point_2"))
        c.point_1 = find_point(data.get("point_1"))
        cx, cy = state.center
        c.cx = cx
        c.cy = cy
        c.child_lines_labels = [lbl for lbl in data.get("child_lines_labels", [])]
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

        self.radius = math.hypot(self.r_point_2.pos_x - self.r_point_1.pos_x, self.r_point_2.pos_y - self.r_point_1.pos_y)

        if state.drag_target is self:

            x_dif, y_dif = self.prev_x - self.pos_x, self.prev_y - self.pos_y
            x1, y1 = self.point_1.pos_x, self.point_1.pos_y

            for obj in self.points:
                if (obj is self.point_1):
                    obj.pos_x -= x_dif
                    obj.pos_y -= y_dif
                    x1 -= x_dif
                    y1 -= y_dif
                    continue

        else:
            if self.point_1 is None and e is None:
                return
            if self.point_1 is None:
                cx, cy = state.center
                x1 = (e.x - cx) / (self.unit_size * self.scale)
                y1 = (cy - e.y) / (self.unit_size * self.scale)
            else:
                x1, y1 = self.point_1.pos_x, self.point_1.pos_y

            self.anchor_1.pos_x, self.anchor_1.pos_y = x1 - self.radius, y1 - self.radius
            self.anchor_2.pos_x, self.anchor_2.pos_y = x1 + self.radius, y1 + self.radius

        for obj in self.points:
            if (obj is not self.point_1) and obj:
                find_translation_circle(obj, self)
                snap_to_circle(obj, self)
                obj.update()


        x1, y1 = world_to_screen(self.anchor_1.pos_x, self.anchor_1.pos_y)
        x2, y2 = world_to_screen(self.anchor_2.pos_x, self.anchor_2.pos_y)

        if self.point_1:
            if self.point_1.is_drawable:
                self.is_drawable = True
            else:
                self.is_drawable = False
        if e:
            self.is_drawable = True

        self.lower_label_obj.is_drawable = self.is_drawable

        if self.is_drawable:

            if self.selected:
                self.canvas.create_oval(
                    x1,
                    y1,
                    x2,
                    y2,
                    outline="lightgrey",
                    width=2 * 3 * visual_scale,
                    tags=self.tag,
                )

            self.canvas.create_oval(
                x1,
                y1,
                x2,
                y2,
                outline="black",
                width=2 * visual_scale,
                tags=self.tag,
            )

        if len(self.child_lines) == 0:
            self.child_lines = load_lines_from_labels(self.child_lines_labels)

        for p in self.points:
            if p:
                self.canvas.tag_raise(p.tag)
        for l in self.child_lines:
            if l:
                l.parent_vector = self.vector
                l.update()
        self.prev_x, self.prev_y = self.pos_x, self.pos_y
        self.canvas.tag_raise(self.lower_label_obj.tag)
