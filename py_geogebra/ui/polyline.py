import tkinter as tk
from ..tools.utils import center, world_to_screen, distance
from .. import state
import math


class Polyline:
    def __init__(
        self,
        root: tk.Tk,
        canvas: tk.Canvas,
        unit_size: int = 40,
        objects=None,
    ):
        self.root = root
        self.canvas = canvas
        self.objects = objects

        self.pos_x = 0.0
        self.pos_y = 0.0

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0  # zoom factor
        self.unit_size = unit_size
        self.length = 0.0

        self.cx = 0
        self.cy = 0

        self.tag = f"polyline_{id(self)}"
        self.lower_label = ""

        self.points = []
        self.last_not_set = True
        self.canvas.bind("<Configure>", lambda e: self.update())

    def update(self, e=None):
        length = 0.0
        for p in self.points:
            p.offset_x = self.offset_x
            p.offset_y = self.offset_y
            p.scale = self.scale
            p.cx = self.cx
            p.cy = self.cy
            p.update()

        self.canvas.delete(self.tag)

        visual_scale = min(max(1, self.scale**0.5), 1.9)

        coords = []

        for p in self.points:
            coords.extend([p.x, p.y])

        if self.last_not_set and e is not None:
            coords.extend([e.x, e.y])

        if len(coords) < 4:
            return
        self.canvas.create_line(
            *coords,
            fill="black",
            width=2 * visual_scale,
            tags=self.tag,
        )

        if not self.last_not_set and self.points:
            for i in range(0, len(self.points), 2):
                if i + 2 <= len(self.points):
                    points = self.points[i : i + 2]
                    length += distance(
                        points[0].pos_x,
                        points[0].pos_y,
                        points[1].pos_x,
                        points[1].pos_y,
                        2,
                    )
            mid = self.points[len(self.points) // 2]
            self.canvas.create_text(
                mid.x - 3 * visual_scale,
                mid.y + 25 * visual_scale,
                text=self.lower_label,
                font=("Arial", int(12 * visual_scale)),
                fill="blue",
                tags=self.tag,
            )
        self.length = length

        for p in self.points:
            self.canvas.tag_raise(p.tag)
