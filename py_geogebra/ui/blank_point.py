
import tkinter as tk
from ..tools.utils import snap
from .. import state
from .. import globals


class Blank_point:

    def __init__(
        self,
        root: tk.Tk,
        label: str = "",
        unit_size: int = 40,
        color="blue",
    ):

        self.root = root
        self.canvas = globals.canvas
        self.color = color
        self.sidebar = globals.sidebar
        self.objects = globals.objects
        self.axes = globals.objects


        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0  # zoom factor
        self.unit_size = unit_size
        self.label = label
        self.is_drawable = True

        self.cx = 0
        self.cy = 0
        self.x = 0
        self.y = 0

        self.pos_x = 0
        self.pos_y = 0



        self.parent_line = None


    def to_dict(self) -> dict:
        return {
            "type": "Blank_point",
            "pos_x": self.pos_x,
            "pos_y": self.pos_y,
            "color": self.color,
            "unit_size": self.unit_size,
            "scale": self.scale,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "label": self.label,
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
        p.offset_x = data.get("offset_x", 0)
        p.offset_y = data.get("offset_y", 0)
        cx, cy = state.center
        p.cx = cx
        p.cy = cy
        p.update()
        return p

    def select(self):
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def snap_point(self, e):
        self.pos_x, self.pos_y = snap(e=e)
        self.update()

    def update(self):

        x = self.cx + self.pos_x * self.unit_size * self.scale
        y = self.cy - self.pos_y * self.unit_size * self.scale
        self.x, self.y = x, y
