import tkinter as tk
import math
from ..tools.utils import snap, world_to_screen
from .. import state
from .. import globals


class Angle:

    def __init__(
        self,
        root: tk.Tk,
        e,
        point_1,
        label: str = "",
        unit_size = 40,
        color="green",
    ):

        self.canvas = globals.canvas
        self.color = color
        self.sidebar = globals.sidebar

        self.label = label

        self.scale = 1.0  # zoom factor

        self.screen_x = 0
        self.screen_y = 0
        self.point_1 = point_1
        self.point_2 = None
        self.anchor = None
        self.angle = 0

        self.translation = 0

        self.is_drawable = True
        self.is_detachable = False
        self.is_atachable = True

        # self.parent_line = None

        self.tag = f"angle_{id(self)}"
        self.selected = False
        self.highlight_tag = f"{self.tag}_highlight"


    def to_dict(self) -> dict:
        return {
            "type": "Angle",
            "label": self.label,
            "color": self.color,
            "scale": self.scale,
            "is_drawable": self.is_drawable,
            "translation": self.translation,
            "tag": self.tag,
        }

    @classmethod
    def from_dict(cls, root, data: dict):
        p = cls(
            root=root,
            e=None,
            point_1= None,
            label=data.get("label", ""),
            color=data.get("color", "blue"),
        )
        p.scale = data.get("scale", 1.0)
        p.is_drawable = data.get("is_drawable", True)
        p.tag = data.get("tag", "")
        p.translation = data.get("translation", 0)
        p.update()
        return p

    def select(self):
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def draw_outline(self):
        r_h = self.r * 1.4
        self.canvas.create_oval(
            self.x - r_h,
            self.y - r_h,
            self.x + r_h,
            self.y + r_h,
            outline=self.color,
            width=2,
            fill="",  # no fill so it looks like a ring
            tags=(self.highlight_tag,),  # must be a tuple
        )

    def draw_angle(self):
        pass


    def update(self):
        if self.anchor is None or self.point_1 is None:
            return
        self.canvas.delete(self.tag)
        self.canvas.delete(self.highlight_tag)

        if self.point_1 and self.point_2 and self.anchor:
            self.angle = math.degrees(math.atan2(self.point_2.pos_y - self.anchor.pos_y, self.point_2.pos_x - self.anchor.pos_x) - math.atan2(self.point_1.pos_y - self.anchor.pos_y, self.point_1.pos_x - self.anchor.pos_x))

            self.x, self.y = world_to_screen(self.anchor.pos_x, self.anchor.pos_y)

            self.visual_scale = min(max(1, self.scale**0.5), 1.9)

            self.r = 6.0 * self.visual_scale

            if self.is_drawable:
                if self.selected:
                    self.draw_outline()
                self.draw_angle()
