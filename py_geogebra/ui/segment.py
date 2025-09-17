import tkinter as tk
from ..tools.utils import center, world_to_screen, distance, snap_to_line
from .. import state
import math


class Segment:
    def __init__(
        self,
        root: tk.Tk,
        canvas: tk.Canvas,
        unit_size: int = 40,
        point_1=None,
        objects=None,
        lower_label: str = "",
    ):
        self.root = root
        self.canvas = canvas
        self.objects = objects

        self.pos_x = 0.0
        self.pos_y = 0.0
        self.prev_x = 0.0
        self.prev_y = 0.0

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0  # zoom factor
        self.unit_size = unit_size
        self.length = 0.0

        self.cx = 0
        self.cy = 0

        self.tag = f"segment_{id(self)}"
        self.point_1 = point_1
        self.point_2 = None
        self.lower_label = lower_label
        
        self.points = [self.point_1]

    def update(self, e=None):
        self.canvas.delete(self.tag)

        visual_scale = min(max(1, self.scale**0.5), 1.9)
    
        if (state.drag_target is self):
            
            x_dif, y_dif = self.prev_x - self.pos_x, self.prev_y - self.pos_y
            x1, y1 = self.point_1.pos_x, self.point_1.pos_y
            x2, y2 = self.point_2.pos_x, self.point_2.pos_y
            
            for obj in self.points:
                if (obj is self.point_1) or (obj is self.point_2):
                    obj.pos_x -= x_dif
                    obj.pos_y -= y_dif
                    x1 -= x_dif
                    y1 -= y_dif
                    x2 -= x_dif
                    y2 -= y_dif
                    continue

            
        else:       

            x1, y1 = self.point_1.pos_x, self.point_1.pos_y

            if self.point_2 is None and e is None:
                return

            if self.point_2 is None:
                cx, cy = state.center
                x2 = (e.x - cx) / (self.unit_size * self.scale)
                y2 = (cy - e.y) / (self.unit_size * self.scale)
            else:
                x2, y2 = self.point_2.pos_x, self.point_2.pos_y
                self.length = distance(x1, y1, x2, y2, 2)
                middle_x = self.point_1.x - (self.point_1.x - self.point_2.x) / 2
                middle_y = self.point_1.y - (self.point_1.y - self.point_2.y) / 2
                self.canvas.create_text(
                    middle_x + 1 * visual_scale,
                    middle_y - 15 * visual_scale,
                    text=self.lower_label,
                    font=("Arial", int(12 * visual_scale)),
                    fill="blue",
                    tags=self.tag,
                )
                
        for obj in self.points:
            if (obj is self.point_1) or (obj is self.point_2):
                continue
            snap_to_line(obj, self)
            obj.update()


        x1, y1 = world_to_screen(self.objects, x1, y1)
        x2, y2 = world_to_screen(self.objects, x2, y2)

        self.canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            fill="black",
            width=2 * visual_scale,
            tags=self.tag,
        )
        self.canvas.tag_raise(self.point_1.tag)
        if self.point_2 is not None:
            self.canvas.tag_raise(self.point_2.tag)
            if self.point_2 not in self.points:
                self.points.append(self.point_2)
                
        self.prev_x, self.prev_y = self.pos_x, self.pos_y
