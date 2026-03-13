import math
import tkinter as tk

from .. import globals
from ..tools.utils import world_to_screen


class Area:
    def __init__(
        self,
        root: tk.Tk,
        target=None,
        unit_size: int = 40,
    ):
        self.root = root
        self.canvas = globals.canvas
        self.target = target

        self.unit_size = unit_size
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.is_drawable = True

        self.value = 0.0
        self.tag = f"area_{id(self)}"
        self.target_tag = getattr(target, "tag", None)

        self.canvas.bind("<Configure>", lambda e: self.update())

    def to_dict(self) -> dict:
        return {
            "type": "Area",
            "tag": self.tag,
            "target_tag": getattr(self.target, "tag", self.target_tag),
            "unit_size": self.unit_size,
            "scale": self.scale,
            "is_drawable": self.is_drawable,
        }

    @classmethod
    def from_dict(cls, root, data: dict):
        target = None
        target_tag = data.get("target_tag")
        for obj in globals.objects._objects:
            if getattr(obj, "tag", None) == target_tag:
                target = obj
                break

        area = cls(
            root=root,
            target=target,
            unit_size=data.get("unit_size", 40),
        )
        area.tag = data.get("tag", f"area_{id(area)}")
        area.target_tag = target_tag
        area.scale = data.get("scale", 1.0)
        area.is_drawable = data.get("is_drawable", True)
        area.update()
        return area

    def _polygon_area_and_center(self, points):
        if len(points) < 3:
            return None, None, None

        signed_twice_area = 0.0
        c_x = 0.0
        c_y = 0.0
        n = len(points)
        for i in range(n):
            x1, y1 = points[i].pos_x, points[i].pos_y
            x2, y2 = points[(i + 1) % n].pos_x, points[(i + 1) % n].pos_y
            cross = x1 * y2 - x2 * y1
            signed_twice_area += cross
            c_x += (x1 + x2) * cross
            c_y += (y1 + y2) * cross

        area = abs(signed_twice_area) / 2.0
        if abs(signed_twice_area) > 1e-12:
            c_x = c_x / (3.0 * signed_twice_area)
            c_y = c_y / (3.0 * signed_twice_area)
        else:
            c_x = sum(p.pos_x for p in points) / len(points)
            c_y = sum(p.pos_y for p in points) / len(points)

        return area, c_x, c_y

    def _circle_area_and_center(self, circle):
        if not hasattr(circle, "center") or circle.center is None:
            return None, None, None
        radius = getattr(circle, "radius", None)
        if radius is None:
            return None, None, None
        return math.pi * (radius**2), circle.center.pos_x, circle.center.pos_y

    def update(self, e=None):
        self.canvas.delete(self.tag)

        if self.target is None or self.target not in globals.objects._objects:
            return

        area = None
        x = None
        y = None

        if hasattr(self.target, "line_points") and getattr(self.target, "line_points", None):
            area, x, y = self._polygon_area_and_center(self.target.line_points)
        elif hasattr(self.target, "radius") and hasattr(self.target, "center"):
            area, x, y = self._circle_area_and_center(self.target)

        if area is None or x is None or y is None:
            return

        self.value = round(area, 2)
        sx, sy = world_to_screen(x, y)
        visual_scale = min(max(1, self.scale**0.5), 1.9)

        label = getattr(self.target, "lower_label", None) or getattr(self.target, "label", "area")
        text_id = self.canvas.create_text(
            sx,
            sy,
            text=f"{label} = {self.value}",
            font=("Arial", int(12 * visual_scale)),
            fill="black",
            tags=(self.tag, "area", "area_text"),
        )
        bbox = self.canvas.bbox(text_id)
        if bbox:
            pad = int(4 * visual_scale)
            bg_id = self.canvas.create_rectangle(
                bbox[0] - pad,
                bbox[1] - pad,
                bbox[2] + pad,
                bbox[3] + pad,
                fill="white",
                outline="black",
                tags=(self.tag, "area", "area_bg"),
            )
            self.canvas.tag_lower(bg_id, text_id)

        self.canvas.tag_raise(self.tag)
