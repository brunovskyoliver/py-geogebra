import tkinter as tk
import math
from .. import state
from .. import globals


class Axes:
    def __init__(self, root: tk.Tk, unit_size: int = 40):
        self.root = root
        self.canvas = globals.canvas

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0
        self.current_step = 1.0
        self.unit_size = unit_size

    def to_dict(self) -> dict:
        return {
            "type": "Axes",
            "unit_size": self.unit_size,
            "scale": self.scale,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "current_step": self.current_step,
        }

    @classmethod
    def from_dict(cls, root, data: dict):
        axes = cls(
            root=root,
        )
        axes.scale = data.get("scale", 1.0)
        axes.offset_x = data.get("offset_x", 0)
        axes.offset_y = data.get("offset_y", 0)
        axes.current_step = data.get("current_step", 1.0)
        axes.update()
        return axes

    def nice_step(self, min_px=50):
        raw_step = min_px / (self.unit_size * self.scale)
        power = math.floor(math.log10(raw_step))
        base = raw_step / (10**power)

        if base < 1.5:
            nice = 1
        elif base < 3.5:
            nice = 2
        else:
            nice = 5

        return nice * (10**power)

    def update(self):
        self.canvas.delete("axes")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        cx, cy = state.center

        # main axes
        self.canvas.create_line(0, cy, width, cy, fill="black", width=2, tags="axes")
        self.canvas.create_line(cx, 0, cx, height, fill="black", width=2, tags="axes")

        step_world = self.nice_step()
        self.current_step = step_world
        step_px = step_world * self.unit_size * self.scale

        # X
        start_val = -math.ceil(cx / step_px) * step_world
        end_val = math.ceil((width - cx) / step_px) * step_world
        val = start_val
        while val <= end_val:
            x = cx + val * self.unit_size * self.scale
            if 0 <= x <= width:
                self.canvas.create_line(
                    x, 0, x, height, fill="lightgray", width=1, tags="axes"
                )

                if abs(val) > 1e-9:
                    self.canvas.create_text(
                        x,
                        cy + 12,
                        text=f"{val:.3f}",
                        font=("Arial", 10),
                        tags="axes",
                        fill="black",
                    )
            val += step_world
        # Y
        start_val = -math.ceil(cy / step_px) * step_world
        end_val = math.ceil((height - cy) / step_px) * step_world
        val = start_val
        while val <= end_val:
            y = cy + val * self.unit_size * self.scale
            if 0 <= y <= height:

                self.canvas.create_line(
                    0, y, width, y, fill="lightgray", width=1, tags="axes"
                )

                if abs(val) > 1e-9:
                    self.canvas.create_text(
                        cx + 15,
                        y,
                        text=f"{(val*-1):.3f}",
                        font=("Arial", 10),
                        tags="axes",
                        fill="black",
                    )
            val += step_world
