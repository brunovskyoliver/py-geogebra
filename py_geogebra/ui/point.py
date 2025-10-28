import tkinter as tk
from ..tools.utils import snap
from .. import state
from .. import globals


class Point:

    def __init__(
        self,
        root: tk.Tk,
        e,
        label: str = "",
        unit_size: int = 40,
        pos_x: int = 0,
        pos_y: int = 0,
        color="blue",
    ):

        self.root = root
        self.canvas = globals.canvas
        self.color = color
        self.sidebar = globals.sidebar
        self.objects = globals.objects
        self.axes = globals.objects

        if not state.shift_pressed or e == None:
            self.pos_x = pos_x
            self.pos_y = pos_y
        else:
            self.pos_x, self.pos_y = snap(e=e)
        self.label = label

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0  # zoom factor
        self.unit_size = unit_size

        cx, cy = state.center
        self.cx = cx
        self.cy = cy
        self.x = 0
        self.y = 0

        self.translation = 0

        self.is_drawable = True
        self.is_detachable = False
        self.is_atachable = True

        self.parent_line = None

        self.tag = f"point_{id(self)}"
        self.selected = False
        self.highlight_tag = f"{self.tag}_highlight"

        self.sidebar.items.append(self)
        self.sidebar.update()

    def to_dict(self) -> dict:
        return {
            "type": "Point",
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
            "tag": self.tag,
        }

    @classmethod
    def from_dict(cls, root, data: dict):
        p = cls(
            root=root,
            e=None,
            label=data.get("label", ""),
            unit_size=data.get("unit_size", 40),
            pos_x=data.get("pos_x", 0),
            pos_y=data.get("pos_y", 0),
            color=data.get("color", "blue"),
        )
        p.scale = data.get("scale", 1.0)
        p.is_drawable = data.get("is_drawable", True)
        p.offset_x = data.get("offset_x", 0)
        p.offset_y = data.get("offset_y", 0)
        p.tag = data.get("tag", "")
        p.translation = data.get("translation", 0)
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
        self.canvas.delete(self.tag)
        self.canvas.delete(self.highlight_tag)

        x = self.cx + self.pos_x * self.unit_size * self.scale
        y = self.cy - self.pos_y * self.unit_size * self.scale
        self.x, self.y = x, y

        visual_scale = min(max(1, self.scale**0.5), 1.9)

        r = 6.0 * visual_scale

        if self.is_drawable:

            if self.selected:
                r_h = r * 1.4
                self.canvas.create_oval(
                    x - r_h,
                    y - r_h,
                    x + r_h,
                    y + r_h,
                    outline=self.color,
                    width=2,
                    fill="",  # no fill so it looks like a ring
                    tags=(self.highlight_tag,),  # must be a tuple
                )

            self.canvas.create_oval(
                x - r,
                y - r,
                x + r,
                y + r,
                fill=self.color,
                width=2,
                tags=(self.tag, "point"),
            )

            if self.label:
                self.canvas.create_text(
                    x + 10 * visual_scale,
                    y - 15 * visual_scale,
                    text=self.label,
                    font=("Arial", int(12 * visual_scale)),
                    fill="blue",
                    tags=(self.tag, "point_label"),
                )
