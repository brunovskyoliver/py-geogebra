import tkinter as tk
from ..tools.utils import (
    world_to_screen,
    find_2lines_intersection,
    find_translation,
    get_label,
    find_translation_between_points,
    find_circle_line_intersection,
    find_circle_circle_intersection,
)
from .segment import Segment
from .segment_with_lenght import Segment_with_length
from .polyline import Polyline
from .polygon import Polygon
from .regular_polygon import Regular_polygon
from .ray import Ray
from .circle_center_point import Circle_center_point
from .circle_center_radius import Circle_center_radius
from .. import globals
from .. import state

class Create_Intersect:
    def __init__(
        self,
        shape_1,
        shape_2,
        root: tk.Tk,
        unit_size: int = 40,
        color="grey",
    ):
        self.root = root
        self.color = color
        self.unit_size = unit_size

        shape_1.deselect()

        intersects = []


        segs_1 = self.expand_segments(shape_1)
        segs_2 = self.expand_segments(shape_2)

        if "circle" not in shape_1.tag and "circle" not in shape_2.tag:
            for p1, p2 in segs_1:
                for p3, p4 in segs_2:
                    intersect_point = find_2lines_intersection([p1, p2, p3, p4])
                    if intersect_point:
                        label = get_label(state)
                        intersect = Intersect(root, label=label, unit_size=unit_size)
                        intersect.point_1, intersect.point_2 = p1, p2
                        intersect.point_3, intersect.point_4 = p3, p4
                        intersect.line_1, intersect.line_2 = shape_1, shape_2
                        intersects.append(intersect)
                        globals.objects.register(intersect)


        if "circle" in shape_1.tag or "circle" in shape_2.tag:
            circle = shape_1 if "circle" in shape_1.tag else shape_2
            other = shape_2 if circle is shape_1 else shape_1

            if "circle" not in other.tag:
                for p1, p2 in self.expand_segments(other):
                    circle_points = find_circle_line_intersection(circle, p1, p2)
                    for i in range(len(circle_points)):
                        c_pt = circle_points[i]
                        label = get_label(state)
                        intersect = Intersect(root, label=label, unit_size=unit_size)
                        intersect.Index = i
                        intersect.line_1 = circle
                        intersect.line_2 = other
                        intersect.pos_x, intersect.pos_y = c_pt
                        intersects.append(intersect)
                        globals.objects.register(intersect)

            elif "circle" in other.tag:
                circle_points = find_circle_circle_intersection(circle, other)
                for i in range(len(circle_points)):
                    c_pt = circle_points[i]
                    label = get_label(state)
                    intersect = Intersect(root, label=label, unit_size=unit_size)
                    intersect.Index = i
                    intersect.line_1 = circle
                    intersect.line_2 = other
                    intersect.pos_x, intersect.pos_y = c_pt
                    intersects.append(intersect)
                    globals.objects.register(intersect)

    def expand_segments(self, shape):
        if isinstance(shape, Polyline) or isinstance(shape, Polygon) or isinstance(shape, Regular_polygon):
            return [(shape.line_points[i], shape.line_points[i + 1])
                    for i in range(len(shape.line_points) - 1)]
        elif hasattr(shape, "point_1") and hasattr(shape, "point_2"):
            return [(shape.point_1, shape.point_2)]
        else:
            return []


class Intersect:
    def __init__(
        self,
        root: tk.Tk,
        label: str = "",
        unit_size: int = 40,
        color="grey",
    ):
        self.root = root
        self.canvas = globals.canvas
        self.color = color
        self.objects = globals.objects

        self.pos_x = 0
        self.pos_y = 0
        self.x = 0
        self.y = 0
        self.label = label

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0
        self.unit_size = unit_size

        self.point_1 = None
        self.point_2 = None
        self.point_3 = None
        self.point_4 = None
        self.line_1 = None
        self.line_2 = None
        self.point_1_label = ""
        self.point_2_label = ""
        self.point_3_label = ""
        self.point_4_label = ""
        self.line_1_label = ""
        self.line_2_label = ""

        self.is_drawable = True
        self.is_detatchable = False
        self.translation = 0

        self.tag = f"intersect_{id(self)}"
        self.selected = False

        self.Index = 0


    def select(self):
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def to_dict(self) -> dict:
        return {
            "type": "Intersect",
            "label": self.label,
            "pos_x": self.pos_x,
            "pos_y": self.pos_y,
            "color": self.color,
            "unit_size": self.unit_size,
            "scale": self.scale,
            "is_drawable": self.is_drawable,
            "translation": self.translation,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "point_1_label": self.point_1.label if self.point_1 else None,
            "point_2_label": self.point_2.label if self.point_2 else None,
            "point_3_label": self.point_3.label if self.point_3 else None,
            "point_4_label": self.point_4.label if self.point_4 else None,
            "line_1_label": self.line_1.lower_label if self.line_1 else None,
            "line_2_label": self.line_2.lower_label if self.line_2 else None,
            "tag": self.tag,
            "index": self.Index,
        }

    @classmethod
    def from_dict(cls, root, data: dict):
        p = cls(
            root=root,
            label=data.get("label", ""),
            unit_size=data.get("unit_size", 40),
            color=data.get("color", "blue"),
        )
        p.scale = data.get("scale", 1.0)
        p.is_drawable = data.get("is_drawable", True)
        p.offset_x = data.get("offset_x", 0)
        p.offset_y = data.get("offset_y", 0)
        p.tag = data.get("tag", "")
        p.translation = data.get("translation", 0)
        p.point_1_label = data.get("point_1_label", "")
        p.point_2_label = data.get("point_2_label", "")
        p.point_3_label = data.get("point_3_label", "")
        p.point_4_label = data.get("point_4_label", "")
        p.line_1_label = data.get("line_1_label", "")
        p.line_2_label = data.get("line_2_label", "")
        p.Index = data.get("index", 0)
        cx, cy = state.center
        p.cx = cx
        p.cy = cy
        p.update()
        return p

    def find_obj(self, label):
            for obj in globals.objects._objects:
                if getattr(obj, "label", None) == label:
                    return obj
                elif getattr(obj, "lower_label", None) == label:
                    return obj
            return None

    def update(self):
        self.canvas.delete(self.tag)
        self.is_drawable = True
        if not self.point_1:
            self.point_1 = self.find_obj(self.point_1_label)
        if not self.point_2:
            self.point_2 = self.find_obj(self.point_2_label)
        if not self.point_3:
            self.point_3 = self.find_obj(self.point_3_label)
        if not self.point_4:
            self.point_4 = self.find_obj(self.point_4_label)
        if not self.line_1:
            self.line_1 = self.find_obj(self.line_1_label)
        if not self.line_2:
            self.line_2 = self.find_obj(self.line_2_label)

        intersection_point = None

        if "circle" not in self.line_1.tag and "circle" not in self.line_2.tag:
            intersection_point = find_2lines_intersection(
                [self.point_1, self.point_2, self.point_3, self.point_4]
            )

        elif "circle" in self.line_1.tag or "circle" in self.line_2.tag:
            circle = self.line_1 if "circle" in self.line_1.tag else self.line_2
            other = self.line_2 if circle is self.line_1 else self.line_1

            if "circle" not in other.tag:
                for p1, p2 in self.get_segments(other):
                    pts = find_circle_line_intersection(circle, p1, p2)
                    if pts:
                        intersection_point = pts[self.Index]
                        break
            else:
                pts = find_circle_circle_intersection(circle, other)
                if pts:
                    intersection_point = pts[self.Index]

        if not intersection_point:
            self.is_drawable = False
            return

        if isinstance(self.line_1, Segment) or isinstance(
            self.line_1, Segment_with_length
        ):
            find_translation(self, self.line_1)
            if self.translation > 1 or self.translation < 0:
                self.is_drawable = False
        elif isinstance(self.line_1, Ray):
            find_translation(self, self.line_1)
            if self.translation < 0:
                self.is_drawable = False
        elif (isinstance(self.line_1, Polyline)
            or isinstance(self.line_1, Polygon)
            or isinstance(self.line_1, Regular_polygon)
        ):
            find_translation_between_points(self, self.point_1, self.point_2)
            if self.translation > 1 or self.translation < 0:
                self.is_drawable = False

        if isinstance(self.line_2, Segment) or isinstance(
            self.line_2, Segment_with_length
        ):
            find_translation(self, self.line_2)
            if self.translation > 1 or self.translation < 0:
                self.is_drawable = False
        elif isinstance(self.line_2, Ray):
            find_translation(self, self.line_2)
            if self.translation < 0:
                self.is_drawable = False
        elif (isinstance(self.line_2, Polyline)
            or isinstance(self.line_2, Polygon)
            or isinstance(self.line_2, Regular_polygon)
        ):
            find_translation_between_points(self, self.point_3, self.point_4)
            if self.translation > 1 or self.translation < 0:
                self.is_drawable = False

        self.pos_x, self.pos_y = intersection_point
        if self.is_drawable:
            self.draw_point()


    def get_segments(self, shape):
        if isinstance(shape, Polyline) or isinstance(shape, Polygon) or isinstance(shape, Regular_polygon):
            return [(shape.line_points[i], shape.line_points[i + 1])
                    for i in range(len(shape.line_points) - 1)]
        elif hasattr(shape, "point_1") and hasattr(shape, "point_2"):
            return [(shape.point_1, shape.point_2)]
        return []

    def draw_point(self):
        visual_scale = min(max(1, self.scale**0.5), 1.9)
        self.x, self.y = world_to_screen(self.pos_x, self.pos_y)
        r = 6.0 * visual_scale

        self.canvas.create_oval(
            self.x - r, self.y - r, self.x + r, self.y + r,
            fill=self.color,
            outline="",
            tags =self.tag,
        )

        if self.selected:
            r_h = r * 1.4
            self.canvas.create_oval(
                self.x - r_h, self.y - r_h, self.x + r_h, self.y + r_h,
                outline=self.color, width=2, fill="",
                tags=self.tag,
            )
        if self.label:
            self.canvas.create_text(
                self.x + 10 * visual_scale,
                self.y - 15 * visual_scale,
                text=self.label,
                font=("Arial", int(12 * visual_scale)),
                fill="blue",
                tags=self.tag,
            )
