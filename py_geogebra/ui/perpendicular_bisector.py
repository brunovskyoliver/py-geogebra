from functools import partial
import tkinter as tk
from ..tools.utils import (
    world_to_screen,
    snap_to_line,
    get_linear_fuction_prescription,
    calculate_vector,
    load_lines_from_labels,
)
from .. import state
from .lower_label import Lower_label
from .blank_point import Blank_point
import math
from types import SimpleNamespace
from .. import globals


class Perpendicular_bisector:
    def __init__(
        self,
        root: tk.Tk,
        unit_size: int = 40,
        perp_point_1=None,
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

        self.tag = f"perpendicular_bisector_{id(self)}"
        self.point_1 = Blank_point(root)
        self.point_2 = Blank_point(root)
        self.perp_point_1 = perp_point_1
        self.perp_point_2 = None
        self.selected = False
        

        self.angle = 0
        self.points = [self.perp_point_1]
        self.child_lines_labels = []
        self.child_lines = []
        self.prescription = ()
        self.vector = (0, 0)
        self.parent_vector = (0,0)
        self.middle = (0,0)
        
        self.lower_label = ""
        self.lower_label_obj = Lower_label(self.root, obj=self)
        self.objects.register(self.lower_label_obj)


        self.canvas.bind("<Configure>", lambda e: self.update())

    def to_dict(self) -> dict:
        return {
            "type": "Perpendicular_bisector",
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
            "perp_point_1": self.perp_point_1.label if self.perp_point_1 else None,
            "perp_point_2": self.perp_point_2.label if self.perp_point_2 else None,
            "prescription": [p for p in self.prescription],
            "vector": self.vector,
            "parent_vector": self.parent_vector,
            "middle": self.middle,
            "child_lines_labels": [l.lower_label for l in self.child_lines]
        }

    @classmethod
    def from_dict(cls, root, data: dict):
        def find_point(label):
            for obj in globals.objects._objects:
                if getattr(obj, "label", None) == label:
                    return obj
            return None

        p1 = find_point(data.get("perp_point_1"))
        p2 = find_point(data.get("perp_point_2"))
        pb = cls(root=root, perp_point_1=p1, unit_size=data.get("unit_size", 40))
        pb.perp_point_2 = p2
        pb.scale = data.get("scale", 1.0)
        pb.is_drawable = data.get("is_drawable", True)
        pb.offset_x = data.get("offset_x", 0)
        pb.offset_y = data.get("offset_y", 0)
        pb.lower_label = data.get("lower_label", "")
        pb.tag = data.get("tag", "")
        pb.pos_x = data.get("pos_x", 0)
        pb.pos_y = data.get("pos_y", 0)
        pb.points = [find_point(lbl) for lbl in data.get("points", []) if lbl]
        cx, cy = state.center
        pb.cx = cx
        pb.cy = cy
        pb.prescription = data.get("prescription", {})
        pb.vector = data.get("vector")
        pb.parent_vector = data.get("parent_vector")
        pb.middle = data.get("middle")
        pb.child_lines_labels = [lbl for lbl in data.get("child_lines_labels", [])]
        pb.update()
        return pb

    def select(self):
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def update(self, e=None):
        self.canvas.delete(self.tag)
        self.vector = (self.parent_vector[1], -self.parent_vector[0])

        visual_scale = min(max(1, self.scale**0.5), 1.9)



        x1, y1 = self.perp_point_1.pos_x, self.perp_point_1.pos_y

        if self.perp_point_2 is None and e is None:
            return

        if self.perp_point_2 is None:
            cx, cy = state.center
            x2 = (e.x - cx) / (self.unit_size * self.scale)
            y2 = (cy - e.y) / (self.unit_size * self.scale)
        else:
            x2, y2 = self.perp_point_2.pos_x, self.perp_point_2.pos_y

        for obj in self.points:
            if (obj is not self.perp_point_1) and (obj is not self.perp_point_2):
                snap_to_line(obj, self)
                obj.update()

        vx, vy = x2 - x1, y2 - y1
        l = math.hypot(vx, vy)
        if l == 0:
            return
        rotated_x, rotated_y = -vy / l, vx / l
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2

        self.middle = (mid_x,mid_y)

        span = max(self.canvas.winfo_width(), self.canvas.winfo_height()) / (
            self.unit_size * self.scale
        ) * 10

        x1, y1 = mid_x - rotated_x * span, mid_y - rotated_y * span
        x2, y2 = mid_x + rotated_x * span, mid_y + rotated_y * span
        
        self.point_1.pos_x, self.point_1.pos_y = x1, y1
        self.point_2.pos_x, self.point_2.pos_y = x2, y2

        self.angle = math.atan2(rotated_y, rotated_x)
        self.vector = (rotated_x, rotated_y)
        self.prescription = get_linear_fuction_prescription(x1, y1, x2, y2)


        x1, y1 = world_to_screen(x1, y1)
        x2, y2 = world_to_screen(x2, y2)

        if self.perp_point_2 is not None:
            self.lower_label_obj.update()


        if not self.perp_point_2:
            self.is_drawable = True
        elif self.perp_point_1.is_drawable and self.perp_point_2.is_drawable:
            self.is_drawable = True
        else:
            self.is_drawable = False
            
        self.lower_label_obj.is_drawable = self.is_drawable 

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
        self.canvas.tag_raise(self.perp_point_1.tag)
        if self.perp_point_2 is not None:
            self.canvas.tag_raise(self.perp_point_2.tag)
            if self.perp_point_2 not in self.points:
                self.points.append(self.perp_point_2)

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

