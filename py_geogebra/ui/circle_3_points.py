import tkinter as tk
from ..tools.utils import (
    find_2lines_intersection,
    screen_to_world,
    snap_to_circle,
    world_to_screen,
    snap_to_circle,
    find_translation_circle,
    load_lines_from_labels,
)
from .. import state
from .lower_label import Lower_label
from .blank_point import Blank_point
from .perpendicular_bisector import Perpendicular_bisector
import math
from .. import globals


class Circle_3_points:
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

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0  # zoom factor
        self.unit_size = unit_size

        self.cx = 0
        self.cy = 0
        self.radius = 0

        self.is_drawable = True

        self.tag = f"circle_3_points_{id(self)}"
        self.center = Blank_point(self.root)
        self.point_1 = point_1
        self.point_2 = None
        self.point_3 = None
        self.anchor_1 = Blank_point(self.root)
        self.anchor_2 = Blank_point(self.root)
        self.bisector_1 = None
        self.bisector_2 = None
        self._preview_p2 = None
        self._preview_p3 = None
        self.selected = False
        self.translation = None

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

    def blank_point(self, x, y):
        p = Blank_point(self.root)
        p.pos_x = x
        p.pos_y = y
        p.is_drawable = True
        return p


    def to_dict(self) -> dict:
        return {
            "type": "Circle_3_points",
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
            "point_3": self.point_3.label if self.point_3 else None,
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
        p3 = find_point(data.get("point_3"))
        c = cls(root=root, point_1=p1, unit_size=data.get("unit_size", 40))
        c.point_2 = p2
        c.point_3 = p3
        c.scale = data.get("scale", 1.0)
        c.is_drawable = data.get("is_drawable", True)
        c.offset_x = data.get("offset_x", 0)
        c.offset_y = data.get("offset_y", 0)
        c.lower_label = data.get("lower_label", "")
        c.tag = data.get("tag", "")
        c.pos_x = data.get("pos_x", 0)
        c.pos_y = data.get("pos_y", 0)
        c.points = [find_point(lbl) for lbl in data.get("points", []) if lbl]
        cx, cy = state.center
        c.cx = cx
        c.cy = cy
        c.prescription = data.get("prescription", {})
        c.vector = data.get("vector")
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

        x1, y1 = self.point_1.pos_x, self.point_1.pos_y

        if state.drag_target is self:

            x_dif, y_dif = self.prev_x - self.pos_x, self.prev_y - self.pos_y
            x2, y2 = self.point_2.pos_x, self.point_2.pos_y

            for obj in self.points:
                if (obj is self.point_1) or (obj is self.point_2) or (obj is self.point_3):
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
                if e is None:
                    return
                x2, y2 = screen_to_world(e)
                if self._preview_p2 is None:
                    self._preview_p2 = self.blank_point(x2, y2)
                else:
                    self._preview_p2.pos_x = x2
                    self._preview_p2.pos_y = y2
                p2 = self._preview_p2
            else:
                p2 = self.point_2

            if self.bisector_1 is None:
                self.bisector_1 = Perpendicular_bisector(
                    self.root,
                    unit_size=self.unit_size,
                    perp_point_1=self.point_1,
                )
                self.bisector_1.perp_point_2 = p2
                self.bisector_1.hide = True
                globals.objects.register(self.bisector_1)
            else:
                self.bisector_1.perp_point_2 = p2

            self.bisector_1.update()
            self.canvas.tag_raise(self.bisector_1.tag)

            if self.point_2 is None:
                return

            if self.point_3 is None:
                if e is None:
                    return
                x3, y3 = screen_to_world(e)
                if self._preview_p3 is None:
                    self._preview_p3 = self.blank_point(x3, y3)
                else:
                    self._preview_p3.pos_x = x3
                    self._preview_p3.pos_y = y3
                p3 = self._preview_p3
            else:
                p3 = self.point_3

            if self.bisector_2 is None:
                self.bisector_2 = Perpendicular_bisector(
                    self.root,
                    unit_size=self.unit_size,
                    perp_point_1=self.point_2,
                )
                self.bisector_2.perp_point_2 = p3
                self.bisector_2.hide = True
                globals.objects.register(self.bisector_2)
            else:
                self.bisector_2.perp_point_2 = p3

            self.bisector_2.update()
            self.canvas.tag_raise(self.bisector_2.tag)

        if self.bisector_1 is not None and self.bisector_2 is not None:
            intersect = None
            intersect = find_2lines_intersection([self.bisector_1.point_1, self.bisector_1.point_2, self.bisector_2.point_1, self.bisector_2.point_2])
            if intersect is not None:
                px, py = intersect
                self.radius = abs(math.hypot(px-x1, py-y1))
                self.pos_x, self.pos_y = px, py
                self.anchor_1.pos_x, self.anchor_1.pos_y = px - self.radius, py - self.radius
                self.anchor_2.pos_x, self.anchor_2.pos_y = px + self.radius, py + self.radius

                self.center.pos_x, self.center.pos_y = px, py

                for obj in self.points:
                    if (obj is not self.point_1) and (obj is not self.point_2) and (obj is not self.point_3):
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
                self.canvas.tag_raise(self.point_1.tag)

                if self.point_2 is not None:
                    self.canvas.tag_raise(self.point_2.tag)
                    if self.point_2 not in self.points:
                        self.points.append(self.point_2)

                if self.point_3 is not None:
                    self.canvas.tag_raise(self.point_3.tag)
                    if self.point_3 not in self.points:
                        self.points.append(self.point_3)

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
