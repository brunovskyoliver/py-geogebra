import tkinter as tk
from ..tools.utils import world_to_screen, find_2lines_intersection, find_translation
from .segment import Segment
from .segment_with_lenght import Segment_with_length
from .ray import Ray


class Intersect:
    def __init__(
        self,
        root: tk.Tk,
        canvas: tk.Canvas,
        label: str = "",
        unit_size: int = 40,
        color="grey",
        objects=None,
    ):

        self.root = root
        self.canvas = canvas
        self.color = color
        self.objects = objects

        self.pos_x = 0
        self.pos_y = 0
        self.label = label

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0  # zoom factor
        self.unit_size = unit_size

        self.x = 0
        self.y = 0

        self.line_1 = None
        self.line_2 = None
        self.translation = 0
        self.is_drawable = True

        self.tag = f"intersect_{id(self)}"
        self.selected = False
        self.highlight_tag = f"{self.tag}_highlight"

    def select(self):
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def update(self):
        self.canvas.delete(self.tag)
        self.canvas.delete(self.highlight_tag)

        self.is_drawable = True

        if self.line_2:
            self.pos_x, self.pos_y = find_2lines_intersection(self.line_1, self.line_2)
            if isinstance(self.line_1, Segment) or isinstance(
                self.line_1, Segment_with_length
            ):
                find_translation(self, self.line_1)
                if self.translation > 1 or self.translation < 0:
                    self.is_drawable = False
            if isinstance(self.line_2, Segment) or isinstance(
                self.line_2, Segment_with_length
            ):
                find_translation(self, self.line_2)
                if self.translation > 1 or self.translation < 0:
                    self.is_drawable = False
            if isinstance(self.line_1, Ray):
                find_translation(self, self.line_1)
                if self.translation < 0:
                    self.is_drawable = False
            if isinstance(self.line_2, Ray):
                find_translation(self, self.line_2)
                if self.translation < 0:
                    self.is_drawable = False

            if self.is_drawable:

                visual_scale = min(max(1, self.scale**0.5), 1.9)

                x, y = world_to_screen(self.pos_x, self.pos_y)
                self.x, self.y = x, y

                r = 6.0 * visual_scale

                self.canvas.create_oval(
                    x - r,
                    y - r,
                    x + r,
                    y + r,
                    fill=self.color,
                    outline="",
                    tags=(self.tag,),
                )

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

                if self.label:
                    self.canvas.create_text(
                        x + 10 * visual_scale,
                        y - 15 * visual_scale,
                        text=self.label,
                        font=("Arial", int(12 * visual_scale)),
                        fill="blue",
                        tags=self.tag,
                    )
