import tkinter as tk

from .. import globals
from ..tools.utils import distance, world_to_screen


class Length:
    def __init__(
        self,
        root: tk.Tk,
        unit_size: int = 40,
        point_1=None,
        point_2=None,
        lower_label: str = "",
        owns_label: bool = True,
    ):
        self.root = root
        self.canvas = globals.canvas

        self.point_1 = point_1
        self.point_2 = point_2
        self.lower_label = lower_label
        self.owns_label = owns_label

        self.unit_size = unit_size
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.is_drawable = True
        self.selected = False

        self.value = 0.0
        self.tag = f"length_{id(self)}"

        self.canvas.bind("<Configure>", lambda e: self.update())

    def to_dict(self) -> dict:
        return {
            "type": "Length",
            "tag": self.tag,
            "lower_label": self.lower_label,
            "point_1": self.point_1.label if self.point_1 else None,
            "point_2": self.point_2.label if self.point_2 else None,
            "unit_size": self.unit_size,
            "scale": self.scale,
            "is_drawable": self.is_drawable,
            "owns_label": self.owns_label,
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

        length = cls(
            root=root,
            unit_size=data.get("unit_size", 40),
            point_1=p1,
            point_2=p2,
            lower_label=data.get("lower_label", ""),
            owns_label=data.get("owns_label", True),
        )
        length.tag = data.get("tag", f"length_{id(length)}")
        length.scale = data.get("scale", 1.0)
        length.is_drawable = data.get("is_drawable", True)
        length.update()
        return length

    def select(self):
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def update(self, e=None):
        self.canvas.delete(self.tag)

        if self.point_1 is None or self.point_2 is None:
            return

        if not (self.point_1.is_drawable and self.point_2.is_drawable):
            self.is_drawable = False
            return

        self.is_drawable = True
        self.value = distance(
            self.point_1.pos_x,
            self.point_1.pos_y,
            self.point_2.pos_x,
            self.point_2.pos_y,
            2,
        )

        middle_x = (self.point_1.pos_x + self.point_2.pos_x) / 2
        middle_y = (self.point_1.pos_y + self.point_2.pos_y) / 2
        x, y = world_to_screen(middle_x, middle_y)
        x1, y1 = world_to_screen(self.point_1.pos_x, self.point_1.pos_y)
        x2, y2 = world_to_screen(self.point_2.pos_x, self.point_2.pos_y)

        visual_scale = min(max(1, self.scale**0.5), 1.9)
        text_id = self.canvas.create_text(
            x,
            y,
            text=f"{self.point_1.label}{self.point_2.label} = {self.value}",
            font=("Arial", int(14 * visual_scale)),
            fill="black",
            tags=(self.tag, "length", "length_text"),
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
                tags=(self.tag, "length", "length_bg"),
            )
            self.canvas.tag_lower(bg_id, text_id)

        self.canvas.tag_raise(self.tag)
