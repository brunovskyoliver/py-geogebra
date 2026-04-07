import math
import tkinter as tk

from py_geogebra.ui.line import Line
from py_geogebra.ui.perpendicular_bisector import Perpendicular_bisector
from py_geogebra.ui.point import Point

from .. import globals, state
from ..tools.utils import (
    distance,
    dot,
    find_2lines_intersection,
    find_translation_circle,
    screen_to_world,
    screen_to_world_float,
    snap_to_circle,
    world_to_screen,
    world_to_screen_float,
)
from .blank_point import Blank_point
from .lower_label import Lower_label


class Circumcircular_arc:
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

        self.tag = f"circumcircular_arc{id(self)}"
        self.center = Blank_point(self.root)
        self.point_1 = None
        self.point_2 = None
        self.point_3 = None
        self.selected = False
        self.translation = None

        self.bisector_1 = None
        self.bisector_2 = None

        self.s_radius = 0
        self.radius = 0

        self.vector = []
        self.n_vector = []

        self.points: list[Point] = []
        self.lower_label = ""
        self.lower_label_obj = Lower_label(self.root, obj=self)
        self.objects.register(self.lower_label_obj)

    def to_dict(self) -> dict:
        return {
            "type": "Circumcircular_arc",
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
            "center": self.center.label if self.center else None,
        }

    @classmethod
    def from_dict(cls, root, data: dict):
        def find_point(label):
            if label in (None, ""):
                return None
            for obj in globals.objects._objects:
                if getattr(obj, "label", None) == label:
                    return obj
            return None

        p1 = find_point(data.get("point_1"))
        p2 = find_point(data.get("point_2"))
        p3 = find_point(data.get("point_3"))
        pc = find_point(data.get("center"))
        c = cls(root=root, unit_size=data.get("unit_size", 40))
        c.point_1 = p1
        c.point_2 = p2
        c.point_3 = p3
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

        if self.point_1 is None or self.point_2 is None or self.point_3 is None:
            return

        x1, y1 = self.point_1.pos_x, self.point_1.pos_y

        if state.drag_target is self:
            x_dif, y_dif = self.prev_x - self.pos_x, self.prev_y - self.pos_y
            x2, y2 = self.point_2.pos_x, self.point_2.pos_y

            for obj in self.points:
                if (
                    (obj is self.point_1)
                    or (obj is self.point_2)
                    or (obj is self.point_3)
                    or (obj is self.center)
                ):
                    obj.pos_x -= x_dif
                    obj.pos_y -= y_dif
                    x1 -= x_dif
                    y1 -= y_dif
                    x2 -= x_dif
                    y2 -= y_dif
                    continue

        else:
            # idk ako toto cele funguje
            if self.point_3 is None and e is None:
                return

            if self.bisector_1 is None:
                self.bisector_1 = Perpendicular_bisector(
                    self.root,
                    unit_size=self.unit_size,
                    perp_point_1=self.point_1,
                )
                self.bisector_1.perp_point_2 = self.point_2
                self.bisector_1.hide = True
                globals.objects.register(self.bisector_1)

            self.bisector_1.update()

            if self.bisector_2 is None:
                self.bisector_2 = Perpendicular_bisector(
                    self.root,
                    unit_size=self.unit_size,
                    perp_point_1=self.point_2,
                )
                self.bisector_2.perp_point_2 = self.point_3
                self.bisector_2.hide = True
                globals.objects.register(self.bisector_2)
            else:
                self.bisector_2.perp_point_2 = self.point_3

            self.bisector_2.update()
            self.canvas.tag_raise(self.bisector_2.tag)

        if self.bisector_1 is not None and self.bisector_2 is not None:
            intersect = None
            intersect = find_2lines_intersection(
                [
                    self.bisector_1.point_1,
                    self.bisector_1.point_2,
                    self.bisector_2.point_1,
                    self.bisector_2.point_2,
                ]
            )
            if intersect is not None:
                px, py = intersect
                self.radius = abs(math.hypot(px - x1, py - y1))
                self.pos_x, self.pos_y = px, py

                self.center.pos_x, self.center.pos_y = px, py

                for obj in self.points:
                    if (
                        (obj is not self.point_1)
                        and (obj is not self.point_2)
                        and (obj is not self.point_3)
                        and (obj is not self.center)
                    ):
                        find_translation_circle(obj, self)
                        snap_to_circle(obj, self)
                        obj.update()

                center_x_screen, center_y_screen = world_to_screen(
                    self.center.pos_x, self.center.pos_y
                )
                point_1_x, point_1_y = world_to_screen(
                    self.point_1.pos_x, self.point_1.pos_y
                )
                point_2_x, point_2_y = world_to_screen(
                    self.point_2.pos_x, self.point_2.pos_y
                )
                point_3_x, point_3_y = world_to_screen(
                    self.point_3.pos_x, self.point_3.pos_y
                )

                radius_screen = world_to_screen_float(self.radius)

                sqaure_x = center_x_screen - radius_screen
                sqaure_y = center_y_screen - radius_screen
                square_x2 = center_x_screen + radius_screen
                square_y2 = center_y_screen + radius_screen

                self.lower_label_obj.is_drawable = self.is_drawable

                start_angle = (
                    math.degrees(
                        -math.atan2(
                            point_1_y - center_y_screen,
                            point_1_x - center_x_screen,
                        )
                    )
                    % 360
                )
                mid_angle = (
                    math.degrees(
                        -math.atan2(
                            point_2_y - center_y_screen,
                            point_2_x - center_x_screen,
                        )
                    )
                    % 360
                )
                end_angle = (
                    math.degrees(
                        -math.atan2(
                            point_3_y - center_y_screen,
                            point_3_x - center_x_screen,
                        )
                    )
                    % 360
                )
                ccw_extent = (end_angle - start_angle) % 360
                mid_offset = (mid_angle - start_angle) % 360
                if mid_offset <= ccw_extent:
                    extent_angle = ccw_extent
                else:
                    extent_angle = ccw_extent - 360

                if self.is_drawable:
                    if self.selected:
                        self.canvas.create_arc(
                            sqaure_x,
                            sqaure_y,
                            square_x2,
                            square_y2,
                            start=start_angle,
                            extent=extent_angle,
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
                        start=start_angle,
                        extent=extent_angle,
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

                if self.point_3 is not None:
                    self.canvas.tag_raise(self.point_3.tag)
                    if self.point_3 not in self.points:
                        self.points.append(self.point_3)

                for p in self.points:
                    self.canvas.tag_raise(p.tag)

                self.prev_x, self.prev_y = self.pos_x, self.pos_y
                self.canvas.tag_raise(self.lower_label_obj.tag)
