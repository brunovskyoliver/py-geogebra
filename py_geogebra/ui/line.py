from os import fsencode
import tkinter as tk
from ..tools.utils import (
    screen_to_world,
    world_to_screen,
    snap_to_line,
    get_linear_fuction_prescription,
    calculate_vector,
    load_lines_from_labels,
)
from .. import state
from .lower_label import Lower_label
import math
from .. import globals



class Line:
    def __init__(
        self,
        root: tk.Tk,
        unit_size: int = 40,
        point_1=None,
    ):
        self.root = root
        self.canvas = globals.canvas
        self.objects = globals.objects

        self.pos_x = 0.0
        self.pos_y = 0.0
        self.prev_x = 0.0
        self.prev_y = 0.0

        self.scale = 1.0  # zoom factor
        self.unit_size = unit_size

        self.cx = 0
        self.cy = 0

        self.is_drawable = True
        self.deleted = False

        self.tag = f"line_{id(self)}"
        self.point_1 = point_1
        self.point_2 = None
        self.selected = False

        self.points = [self.point_1]
        self.child_lines_labels = []
        self.child_lines = []
        self.lower_label = ""
        self.lower_label_obj = Lower_label(self.root, obj=self)
        self.objects.register(self.lower_label_obj)
        self.prescription = ()
        self.angle = 0
        self.vector = (0, 0)

        self.canvas.bind("<Configure>", lambda e: self.update())

    def to_dict(self) -> dict:
        return {
            "type": "Line",
            "lower_label": self.lower_label,
            "pos_x": self.pos_x,
            "pos_y": self.pos_y,
            "unit_size": self.unit_size,
            "scale": self.scale,
            "is_drawable": self.is_drawable,
            "tag": self.tag,
            "points": [p.label for p in self.points],
            "point_1": self.point_1.label if self.point_1 else None,
            "point_2": self.point_2.label if self.point_2 else None,
            "prescription": [p for p in self.prescription],
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

        def find_line(label):
            for obj in globals.objects._objects:
                if getattr(obj, "lower_label", None) == label:
                    return obj
            return None

        p1 = find_point(data.get("point_1"))
        p2 = find_point(data.get("point_2"))
        line = cls(root=root, point_1=p1, unit_size=data.get("unit_size", 40))
        line.point_2 = p2
        line.scale = data.get("scale", 1.0)
        line.is_drawable = data.get("is_drawable", True)
        line.lower_label = data.get("lower_label", "")
        line.tag = data.get("tag", "")
        line.pos_x = data.get("pos_x", 0)
        line.pos_y = data.get("pos_y", 0)
        line.points = [find_point(lbl) for lbl in data.get("points", []) if lbl]
        cx, cy = state.center
        line.cx = cx
        line.cy = cy
        line.prescription = data.get("prescription", {})
        line.vector = data.get("vector")
        line.child_lines_labels = [lbl for lbl in data.get("child_lines_labels", [])]
        line.update()
        return line

    def select(self):
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()


    def resolve_coords(self, e=None) -> tuple[float, float, float, float]:
        w_x1, w_y1 = self.point_1.pos_x, self.point_1.pos_y

        if state.drag_target is self:

            x_dif, y_dif = self.prev_x - self.pos_x, self.prev_y - self.pos_y
            w_x2, w_y2 = self.point_2.pos_x, self.point_2.pos_y
            for obj in [self.point_1, self.point_2]:
                obj.pos_x -= x_dif
                obj.pos_y -= y_dif

            w_x1 -= x_dif
            w_y1 -= y_dif
            w_x2 -= x_dif
            w_y2 -= y_dif

        else:

            if self.point_2 is None:
                w_x2, w_y2 = screen_to_world(e)
            else:
                w_x2, w_y2 = self.point_2.pos_x, self.point_2.pos_y



        self.angle = math.atan2(w_y2 - w_y1, w_x2 - w_x1)
        span = max(self.canvas.winfo_width(), self.canvas.winfo_height()) / (
            self.unit_size * self.scale
        )
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)

        if self.point_2 is not None:
            self.lower_label_obj.update()

            self.vector = calculate_vector(self.point_1, self.point_2)

        self.prescription = get_linear_fuction_prescription(w_x1, w_y1, w_x2, w_y2)

        span *= 10
        w_x1 -= span * cos_a
        w_y1 -= span * sin_a
        w_x2 += span * cos_a
        w_y2 += span * sin_a

        x1, y1 = world_to_screen(w_x1, w_y1)
        x2, y2 = world_to_screen(w_x2, w_y2)

        return x1, y1, x2, y2

    def snap_points(self):
        for obj in self.points:
            if (obj is not self.point_1) and (obj is not self.point_2):
                snap_to_line(obj, self)
                obj.update()

    def _is_drawable(self) -> bool:
        if self.point_2 is None:
            return True
        return self.point_1.is_drawable and self.point_2.is_drawable

    def draw_outline(self):
        self.canvas.create_line(
            self.x1,
            self.y1,
            self.x2,
            self.y2,
            fill="lightgrey",
            width=2 * 3 * self.visual_scale,
            tags=self.tag,
        )

    def draw_line(self):
        self.canvas.create_line(
            self.x1,
            self.y1,
            self.x2,
            self.y2,
            fill="black",
            width=2 * self.visual_scale,
            tags=self.tag,
        )


    def update(self, e=None):
        if self.deleted or (self.point_2 is None and e is None):
            return
        self.canvas.delete(self.tag)

        self.visual_scale = min(max(1, self.scale**0.5), 1.9)

        self.x1,self.y1,self.x2,self.y2 = self.resolve_coords(e=e)

        self.snap_points()

        self.is_drawable = self._is_drawable()
        self.lower_label_obj.is_drawable = self.is_drawable

        if self.is_drawable:
            if self.selected:
                self.draw_outline()
            self.draw_line()


        if self.point_2 and self.point_2 not in self.points:
            self.points.append(self.point_2)

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
