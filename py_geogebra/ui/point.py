import tkinter as tk
from ..tools.utils import center


class Point:
    def __init__(
        self, root: tk.Tk, canvas: tk.Canvas, label: str = "", unit_size: int = 40
    ):
        self.root = root
        self.canvas = canvas

        self.pos_x = 0.0
        self.pos_y = 0.0
        self.label = label

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0  # zoom factor
        self.unit_size = unit_size

        self.cx = 0
        self.cy = 0

        self.tag = f"point_{id(self)}"

        self.canvas.bind("<Configure>", lambda e: self.update())

    def update(self):
        self.canvas.delete(self.tag)

        x = self.cx + self.pos_x * self.unit_size * self.scale
        y = self.cy - self.pos_y * self.unit_size * self.scale

        visual_scale = min(max(1, self.scale**0.5), 1.9)

        r = 6.0 * visual_scale

        self.canvas.create_oval(
            x - r, y - r, x + r, y + r, fill="blue", width=2, tags=(self.tag, "point")
        )

        if self.label:
            self.canvas.create_text(
                x + 5 * visual_scale,
                y - 10 * visual_scale,
                text=self.label,
                font=("Arial", int(12 * visual_scale)),
                fill="blue",
                tags=self.tag,
            )
