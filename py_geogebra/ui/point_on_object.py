import tkinter as tk
from ..tools.utils import snap, world_to_screen
from .. import state
from .. import globals


class Point_on_object:
    def __init__(
        self,
        root: tk.Tk,
        e,
        label: str = "",
        pos_x: int = 0,
        pos_y: int = 0,
        color="blue",
    ):

        self.canvas = globals.canvas
        self.color = color
        self.sidebar = globals.sidebar

        if not state.shift_pressed or e == None:
            self.pos_x = pos_x
            self.pos_y = pos_y
        else:
            self.pos_x, self.pos_y = snap(e=e)
        self.label = label

        self.scale = 1.0  # zoom factor

        self.screen_x = 0
        self.screen_y = 0

        self.translation = 0

        self.is_drawable = True
        self.is_detachable = False
        self.is_atachable = True

        self.parent_obj = None

        self.tag = f"point_on_object_{id(self)}"
        self.selected = False
        self.highlight_tag = f"{self.tag}_highlight"

        self.sidebar.items.append(self)
        self.sidebar.update()

    def to_dict(self) -> dict:
        return {
            "type": "Point_on_object",
            "label": self.label,
            "pos_x": self.pos_x,
            "pos_y": self.pos_y,
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
            label=data.get("label", ""),
            pos_x=data.get("pos_x", 0),
            pos_y=data.get("pos_y", 0),
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

    def snap_point(self, e):
        self.pos_x, self.pos_y = snap(e=e)
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

    def draw_point(self):
        self.canvas.create_oval(
            self.x - self.r,
            self.y - self.r,
            self.x + self.r,
            self.y + self.r,
            fill=self.color,
            width=2,
            tags=(self.tag, "point"),
        )

        if self.label:
            self.canvas.create_text(
                self.x + 10 * self.visual_scale,
                self.y - 15 * self.visual_scale,
                text=self.label,
                font=("Arial", int(12 * self.visual_scale)),
                fill="blue",
                tags=(self.tag, "point_label"),
            )


    def update(self):
        self.canvas.delete(self.tag)
        self.canvas.delete(self.highlight_tag)

        self.x, self.y = world_to_screen(self.pos_x, self.pos_y)



        self.visual_scale = min(max(1, self.scale**0.5), 1.9)

        self.r = 6.0 * self.visual_scale

        if self.is_drawable:
            if self.selected:
                self.draw_outline()
            self.draw_point()
