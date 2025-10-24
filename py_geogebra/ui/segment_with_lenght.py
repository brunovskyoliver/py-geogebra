import tkinter as tk
from ..tools.utils import (
    world_to_screen,
    snap_to_line,
    calculate_vector,
    load_lines_from_labels,
)
from .. import state
import math
from .lower_label import Lower_label
from .. import globals


class Segment_with_length:
    def __init__(
        self,
        root: tk.Tk,
        unit_size: int = 40,
        point_1=None,
        point_2=None,
        length: float = 1.0,
        angle: float = 0.0,
        lower_label: str = "",
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

        self.length = length
        self.angle = angle

        self.tag = f"segment_with_length_{id(self)}"
        self.point_1 = point_1
        self.point_2 = point_2

        self.points = [self.point_1]

        self.selected = False

        self.is_drawable = True
        self.lower_label = lower_label
        self.lower_label_obj = Lower_label(self.root, obj=self)
        self.objects.register(self.lower_label_obj)
        self.vector = (0,0)
        self.child_lines = []
        self.child_lines_labels = []
        

        self.canvas.bind("<Configure>", lambda e: self.update())

    def to_dict(self) -> dict:
        return {
            "type": "Segment With Length",
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
            "length": self.length,
            "angle": self.angle,
            "vector": self.vector,
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
        p2 = find_point(data.get("point_2"))
        swl = cls(root=root, point_1=p1, unit_size=data.get("unit_size", 40))
        swl.point_2 = p2
        swl.scale = data.get("scale", 1.0)
        swl.is_drawable = data.get("is_drawable", True)
        swl.offset_x = data.get("offset_x", 0)
        swl.offset_y = data.get("offset_y", 0)
        swl.lower_label = data.get("lower_label", "")
        swl.tag = data.get("tag", "")
        swl.lower_label_obj = Lower_label(root, obj=swl)
        globals.objects.register(swl.lower_label_obj)
        swl.points = [find_point(lbl) for lbl in data.get("points", []) if lbl]
        cx, cy = state.center
        swl.cx = cx
        swl.cy = cy
        swl.length = data.get("length", 1.0)
        swl.angle = data.get("angle", 0.0)
        swl.vector = data.get("vector")
        swl.child_lines_labels = [lbl for lbl in data.get("child_lines_labels", [])]
        globals.sidebar.items.append(swl)
        swl.update()
        return swl

    def select(self):
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def update(self, e=None):
        self.canvas.delete(self.tag)

        visual_scale = min(max(1, self.scale**0.5), 1.9)
        if state.drag_target is self.point_2:
            self.angle = math.atan2(
                self.point_2.pos_y - self.point_1.pos_y,
                self.point_2.pos_x - self.point_1.pos_x,
            )

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
            self.point_2.pos_x = x1 + self.length * math.cos(self.angle) / (
                self.unit_size
            )
            self.point_2.pos_y = y1 + self.length * math.sin(self.angle) / (
                self.unit_size
            )
            x2, y2 = self.point_2.pos_x, self.point_2.pos_y
            self.point_2.update()

        for obj in self.points:
            if (obj is not self.point_1) and (obj is not self.point_2):
                if obj.translation > 1:
                    obj.translation = 1
                elif obj.translation < 0:
                    obj.translation = 0
                snap_to_line(obj, self)
                obj.update()

        x1, y1 = world_to_screen(x1, y1)
        x2, y2 = world_to_screen(x2, y2)

        if not self.point_2:
            self.is_drawable = True
        elif self.point_1.is_drawable and self.point_2.is_drawable:
            self.is_drawable = True
        else:
            self.is_drawable = False

        if self.point_2 is not None:
            self.lower_label_obj.update()
            
            self.vector = calculate_vector(self.point_1, self.point_2)

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

        if self.point_2 not in self.points:
            self.points.append(self.point_2)

        self.prev_x = self.pos_x
        self.prev_y = self.pos_y

        self.point_2.is_drawable = self.point_1.is_drawable
        self.point_2.update()
        
        if len(self.child_lines) == 0:
            self.child_lines = load_lines_from_labels(self.child_lines_labels)
        
        for p in self.points:
            self.canvas.tag_raise(p.tag)
            
        for l in self.child_lines:
            if l:
                l.parent_vector = self.vector
                l.update()
