import tkinter as tk
from ..tools.utils import center, world_to_screen, snap_to_line
from .. import state
import math


class Segment_with_length:
    def __init__(
        self,
        root: tk.Tk,
        canvas: tk.Canvas,
        unit_size: int = 40,
        point_1=None,
        point_2=None,
        length: float = 1.0,
        angle: float = 0.0,
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

        self.length = length
        self.angle = angle

        self.tag = f"line_{id(self)}"
        self.point_1 = point_1
        self.point_2 = point_2
        
        self.points = [self.point_1]
        
        self.selected = False

        self.canvas.bind("<Configure>", lambda e: self.update())
        
    def select(self):
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def update(self, e=None):
        self.canvas.delete(self.tag)

        visual_scale = min(max(1, self.scale**0.5), 1.9)
        if state.drag_target is self.point_2:
            self.angle = math.atan2(
                self.point_2.pos_y - self.point_1.pos_y,
                self.point_2.pos_x - self.point_1.pos_x,
            )
            
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
            self.point_2.pos_x = x1 + self.length * math.cos(self.angle) / (self.unit_size)
            self.point_2.pos_y = y1 + self.length * math.sin(self.angle) / (self.unit_size)
            x2, y2 = self.point_2.pos_x, self.point_2.pos_y
            self.point_2.update()
            
        for obj in self.points:
            if (obj is not self.point_1) and (obj is not self.point_2):
                if (obj.translation > 1):
                    obj.translation = 1
                elif (obj.translation < 0):
                    obj.translation = 0
                snap_to_line(obj, self)
                obj.update()

        x1, y1 = world_to_screen(self.objects, x1, y1)
        x2, y2 = world_to_screen(self.objects, x2, y2)
        
        if self.selected:
            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill="lightgrey",
                width=2 * 3 * visual_scale,
                tags=self.tag,
            )

        self.canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            fill="black",
            width=2 * visual_scale,
            tags=self.tag,
        )
        
        if self.point_2 not in self.points:
                self.points.append(self.point_2)
        
        self.prev_x = self.pos_x
        self.prev_y = self.pos_y
