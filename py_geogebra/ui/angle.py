import tkinter as tk
import math
from ..tools.utils import world_to_screen
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
            fill="",
            tags=(self.highlight_tag,),
        )

    def draw_angle(self):
        if self.anchor is None or self.point_1 is None:
            return

        ax, ay = world_to_screen(self.anchor.pos_x, self.anchor.pos_y)
        p1x, p1y = world_to_screen(self.point_1.pos_x, self.point_1.pos_y)

        if self.point_2 is not None:
            p2x, p2y = world_to_screen(self.point_2.pos_x, self.point_2.pos_y)
        elif self.preview_cursor is not None:
            p2x, p2y = self.preview_cursor
        else:
            return

        v1x, v1y = p1x - ax, p1y - ay
        v2x, v2y = p2x - ax, p2y - ay
        d1 = math.hypot(v1x, v1y)
        d2 = math.hypot(v2x, v2y)
        if d1 == 0 or d2 == 0:
            return

        a1 = math.atan2(v1y, v1x)
        a2 = math.atan2(v2y, v2x)
        diff = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        self.angle = abs(math.degrees(diff))

        r = max(18 * self.visual_scale, min(52 * self.visual_scale, min(d1, d2) * 0.42))
        steps = 28
        points = [ax, ay]
        for i in range(steps + 1):
            t = a1 + diff * (i / steps)
            points.extend([ax + r * math.cos(t), ay + r * math.sin(t)])
        points.extend([ax, ay])

        self.canvas.create_polygon(
            points,
            fill="#A8D5BA",
            outline="",
            tags=(self.tag, "angle_arc"),
        )

        arc_pts = []
        for i in range(steps + 1):
            t = a1 + diff * (i / steps)
            arc_pts.extend([ax + r * math.cos(t), ay + r * math.sin(t)])
        self.canvas.create_line(
            arc_pts,
            fill="#228B22",
            width=2,
            smooth=True,
            tags=(self.tag, "angle_arc"),
        )

        mid_t = a1 + diff / 2
        tx = ax + (r * 0.67) * math.cos(mid_t)
        ty = ay + (r * 0.67) * math.sin(mid_t)
        greek = {
            "a": "α",
            "b": "β",
            "c": "γ",
            "d": "δ",
            "e": "ε",
            "f": "ζ",
            "g": "η",
            "h": "θ",
            "i": "ι",
            "j": "κ",
            "k": "λ",
            "l": "μ",
            "m": "ν",
            "n": "ξ",
            "o": "ο",
            "p": "π",
            "q": "ρ",
            "r": "σ",
            "s": "τ",
            "t": "υ",
            "u": "φ",
            "v": "χ",
            "w": "ψ",
            "x": "ω",
        }
        greek_label = "".join(greek.get(ch, ch) for ch in (self.label or "a"))
        self.canvas.create_text(
            tx,
            ty,
            text=f"{greek_label} = {round(self.angle, 2)}°",
            font=("Arial", int(11 * self.visual_scale)),
            fill="#006400",
            tags=(self.tag, "angle_text"),
        )

        self.canvas.tag_lower("angle_arc")


    def update(self, e=None):
        self.canvas.delete(self.tag)
        self.canvas.delete(self.highlight_tag)
        self.preview_cursor = None

        if self.anchor is None or self.point_1 is None:
            return

        if e is not None:
            self.preview_cursor = (e.x, e.y)

        self.x, self.y = world_to_screen(self.anchor.pos_x, self.anchor.pos_y)
        self.visual_scale = min(max(1, self.scale**0.5), 1.9)
        self.r = 6.0 * self.visual_scale

        if self.is_drawable:
            if self.selected:
                self.draw_outline()
            self.draw_angle()
