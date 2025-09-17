import tkinter as tk
from ..tools.utils import center, world_to_screen, snap_to_line
from .. import state
import math


class Line:
    def __init__(
        self,
        root: tk.Tk,
        canvas: tk.Canvas,
        unit_size: int = 40,
        point_1=None,
        objects=None,
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

        self.cx = 0
        self.cy = 0

        self.tag = f"line_{id(self)}"
        self.point_1 = point_1
        self.point_2 = None
        
        
        self.points = [self.point_1]

        self.canvas.bind("<Configure>", lambda e: self.update())

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
                snap_to_line(obj, self)
                obj.update()
            
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
                
        for obj in self.points:
            if (obj is self.point_1) or (obj is self.point_2):
                continue
            snap_to_line(obj, self)
            obj.update()

        angle = math.atan2(y2 - y1, x2 - x1)
        span = (
            max(self.canvas.winfo_width(), self.canvas.winfo_height())
            * 10
            / (self.unit_size * self.scale)
        )
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        x1 -= span * cos_a
        y1 -= span * sin_a
        x2 += span * cos_a
        y2 += span * sin_a

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
