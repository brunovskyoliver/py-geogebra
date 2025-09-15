import tkinter as tk
from ..tools.utils import center


class Pen:
    def __init__(self, root: tk.Tk, canvas: tk.Canvas, unit_size: int = 40):
        self.root = root
        self.canvas = canvas
        self.unit_size = unit_size
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.tag = f"pen_{id(self)}"
        self.cx = 0
        self.cy = 0

        self.points = []

        self.canvas.bind("<Configure>", lambda e: self.update())

    def add_point(self, world_x, world_y):
        self.points.append((world_x, world_y))
        self.update()

    def delete_point(self, x, y, r):
        points = []
        for p in self.points:
            if p is None:
                points.append(None)
            else:
                xx, yy = p
                dx = x - xx
                dy = y - yy
                if dx**2 + dy**2 > r**2:
                    points.append(p)
                else:
                    if len(points) >= 1 and points[-1] is not None:
                        points.append(None)
        self.points = points
        self.update()

    def update(self):
        self.canvas.delete(self.tag)
        if len(self.points) < 2:
            return

        visual_scale = min(max(1, self.scale**0.5), 1.9)

        segment = []
        for p in self.points + [None]:
            if p is None:
                if len(segment) >= 2:

                    coords = []
                    for xx, yy in segment:
                        x = self.cx + xx * self.unit_size * self.scale
                        y = self.cy - yy * self.unit_size * self.scale
                        coords.extend((x, y))
                    self.canvas.create_line(
                        *coords,
                        fill="black",
                        width=2 * visual_scale,
                        smooth=True,
                        tags=self.tag,
                    )
                segment = []
            else:
                segment.append(p)
