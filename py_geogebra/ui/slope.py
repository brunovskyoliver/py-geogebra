import tkinter as tk

from .. import globals
from ..tools.utils import world_to_screen


class Slope:
    def __init__(
        self,
        root: tk.Tk,
        target=None,
        unit_size: int = 40,
        lower_label: str = "",
    ):
        self.root = root
        self.canvas = globals.canvas
        self.target = target

        self.unit_size = unit_size
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.label_offset_x = 0.0
        self.label_offset_y = 0.0
        self.is_drawable = True
        self.selected = False

        self.value = 0.0
        self.display_value = "0"
        self.lower_label = lower_label
        self.tag = f"slope_{id(self)}"
        self.target_tag = getattr(target, "tag", None)

        self.canvas.bind("<Configure>", lambda e: self.update())

    def to_dict(self) -> dict:
        return {
            "type": "Slope",
            "tag": self.tag,
            "target_tag": getattr(self.target, "tag", self.target_tag),
            "lower_label": self.lower_label,
            "unit_size": self.unit_size,
            "scale": self.scale,
            "is_drawable": self.is_drawable,
            "label_offset_x": self.label_offset_x,
            "label_offset_y": self.label_offset_y,
        }

    @classmethod
    def from_dict(cls, root, data: dict):
        target = None
        target_tag = data.get("target_tag")
        for obj in globals.objects._objects:
            if getattr(obj, "tag", None) == target_tag:
                target = obj
                break

        slope = cls(
            root=root,
            target=target,
            unit_size=data.get("unit_size", 40),
            lower_label=data.get("lower_label", ""),
        )
        slope.tag = data.get("tag", f"slope_{id(slope)}")
        slope.target_tag = target_tag
        slope.scale = data.get("scale", 1.0)
        slope.is_drawable = data.get("is_drawable", True)
        slope.label_offset_x = data.get("label_offset_x", 0.0)
        slope.label_offset_y = data.get("label_offset_y", 0.0)
        slope.update()
        return slope

    def select(self):
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def _resolve_position(self):
        point_1 = getattr(self.target, "point_1", None)
        point_2 = getattr(self.target, "point_2", None)
        if point_1 is None or point_2 is None:
            return None, None
        return (
            (point_1.pos_x + point_2.pos_x) / 2,
            (point_1.pos_y + point_2.pos_y) / 2,
        )

    def update(self, e=None):
        self.canvas.delete(self.tag)

        if self.target is None or self.target not in globals.objects._objects:
            return

        point_1 = getattr(self.target, "point_1", None)
        point_2 = getattr(self.target, "point_2", None)
        if point_1 is None or point_2 is None:
            return
        if not (point_1.is_drawable and point_2.is_drawable):
            self.is_drawable = False
            return

        self.is_drawable = True
        dx = point_2.pos_x - point_1.pos_x
        dy = point_2.pos_y - point_1.pos_y
        if abs(dx) < 1e-12:
            self.value = float("inf")
            self.display_value = "undefined"
        else:
            self.value = round(dy / dx, 2)
            self.display_value = str(self.value)

        x, y = self._resolve_position()
        if x is None or y is None:
            return

        sx, sy = world_to_screen(x, y)
        sx += self.label_offset_x
        sy += self.label_offset_y
        visual_scale = min(max(1, self.scale**0.5), 1.9)

        label = self.lower_label or "m"
        text_id = self.canvas.create_text(
            sx,
            sy,
            text=f"{label} = {self.display_value}",
            font=("Arial", int(12 * visual_scale)),
            fill="black",
            tags=(self.tag, "slope", "slope_text"),
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
                tags=(self.tag, "slope", "slope_bg"),
            )
            self.canvas.tag_lower(bg_id, text_id)

        self.canvas.tag_raise(self.tag)
