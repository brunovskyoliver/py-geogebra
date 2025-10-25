import tkinter as tk
from ..tools.utils import (
    world_to_screen,
    snap_to_line,
    get_linear_fuction_prescription,
    load_lines_from_labels,
    get_label,
)
from .. import state
from .lower_label import Lower_label
import math
from .. import globals
from .blank_point import Blank_point


class Perpendicular_line:
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

        self.is_drawable = True

        self.tag = f"perpendicular_line_{id(self)}"
        self.point_1 = None
        self.point_2 = Blank_point(root, get_label(state))
        self.selected = False

        self.child_lines = []
        self.child_lines_labels = []
        self.points = []
        self.lower_label = ""
        self.lower_label_obj = Lower_label(self.root, obj=self)
        self.objects.register(self.lower_label_obj)
        self.prescription = ()
        self.angle = 0
        self.vector = (0,0)
        self.parent_vector = (0,0)

        self.canvas.bind("<Configure>", lambda e: self.update())

    def to_dict(self) -> dict:
        return {
            "type": "Perpendicular_line",
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
            "prescription": [p for p in self.prescription],
            "parent_vector": self.parent_vector,
            "child_lines_labels": [l.lower_label for l in self.child_lines]
        }

    @classmethod
    def from_dict(cls, root, data: dict):
        def find_point(label):
            for obj in globals.objects._objects:
                if getattr(obj, "label", None) == label:
                    return obj
            return None

        p1 = find_point(data.get("point_1"))
        line = cls(root=root, unit_size=data.get("unit_size", 40))

        line.point_1 = p1
        line.scale = data.get("scale", 1.0)
        line.is_drawable = data.get("is_drawable", True)
        line.offset_x = data.get("offset_x", 0)
        line.offset_y = data.get("offset_y", 0)
        line.lower_label = data.get("lower_label", "")
        line.tag = data.get("tag", "")
        line.pos_x = data.get("pos_x", 0)
        line.pos_y = data.get("pos_y", 0)
        line.points = [find_point(lbl) for lbl in data.get("points", []) if lbl]
        cx, cy = state.center
        line.cx = cx
        line.cy = cy
        line.prescription = data.get("prescription", {})
        line.parent_vector = data.get("parent_vector")
        line.child_lines_labels = [lbl for lbl in data.get("child_lines_labels", [])]
        line.update()
        return line

    def select(self):
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def update(self, e=None):
        self.canvas.delete(self.tag)
        self.vector  = (self.parent_vector[1], -self.parent_vector[0])
        self.point_2.pos_x = self.point_1.pos_x + self.vector[0]
        self.point_2.pos_y = self.point_1.pos_y + self.vector[1]


        visual_scale = min(max(1, self.scale**0.5), 1.9)

        if state.drag_target is self:

            x_dif, y_dif = self.prev_x - self.pos_x, self.prev_y - self.pos_y
            x1, y1 = self.point_1.pos_x, self.point_1.pos_y
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
            x1, y1 = self.point_1.pos_x, self.point_1.pos_y

            if self.point_1 is None:
                return

            if self.point_2 is None:
                cx, cy = state.center
                x2 = (e.x - cx) / (self.unit_size * self.scale)
                y2 = (cy - e.y) / (self.unit_size * self.scale)
            else:
                x2, y2 = self.point_2.pos_x, self.point_2.pos_y

        for obj in self.points:
            if (obj is not self.point_1) and (obj is not self.point_2):
                snap_to_line(obj, self)
                obj.update()

        self.angle = math.atan2(y2 - y1, x2 - x1)
        span = max(self.canvas.winfo_width(), self.canvas.winfo_height()) / (
            self.unit_size * self.scale
        )
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)

        if self.point_2 is not None:
            self.lower_label_obj.update()

        self.prescription = get_linear_fuction_prescription(x1, y1, x2, y2)

        span *= 10
        x1 -= span * cos_a
        y1 -= span * sin_a
        x2 += span * cos_a
        y2 += span * sin_a

        x1, y1 = world_to_screen(x1, y1)
        x2, y2 = world_to_screen(x2, y2)

        if self.point_1.is_drawable:
            self.is_drawable = True
        else:
            self.is_drawable = False

        if self.is_drawable:

            if self.selected:
                self.canvas.create_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill="lightgrey",
                    width=2 * 3 * visual_scale,
                    tags=self.tag,
                )

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

        if len(self.child_lines) == 0:
            self.child_lines = load_lines_from_labels(self.child_lines_labels)

        for p in self.points:
            self.canvas.tag_raise(p.tag)
        for l in self.child_lines:
            if l:
                l.parent_vector = self.vector
                l.update()
        self.prev_x, self.prev_y = self.pos_x, self.pos_y
        self.canvas.tag_raise(self.lower_label_obj.tag)
