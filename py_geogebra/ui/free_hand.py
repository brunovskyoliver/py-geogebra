import math
import tkinter as tk
from typing_extensions import Set

from py_geogebra import state
from py_geogebra.tools.utils import find_blank_point_at_position, get_lower_label
from py_geogebra.ui.blank_point import Blank_point
from py_geogebra.ui.circle_center_radius import Circle_center_radius
from py_geogebra.ui.segment import Segment
from .. import globals


class FreeHand:
    def __init__(self, root: tk.Tk, unit_size: int = 40):
        self.root = root
        self.canvas = globals.canvas
        self.unit_size = unit_size
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.tag = f"pen_{id(self)}"
        self.cx = 0
        self.cy = 0

        self.points = []

        self.line_buffer = 0.98
        self.circle_buffer =0.33

        self.detected = False

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

    def detect_line(self, start_index: int = 0, stop_index:int = -1) -> bool:
        if stop_index == -1:
            stop_index = len(self.points)
        real_lenght = 0
        estimated_lenght = math.hypot(self.points[stop_index-1][0] - self.points[start_index][0], self.points[stop_index-1][1] - self.points[start_index][1])

        for i in range(start_index,stop_index-1):
            x1, y1 = self.points[i][0], self.points[i][1]
            x2, y2 = self.points[i+1][0], self.points[i+1][1]
            lenght = math.hypot(x2-x1, y2-y1)
            real_lenght += lenght

        if estimated_lenght >= real_lenght * self.line_buffer:
            lower_label = get_lower_label(state)
            p = find_blank_point_at_position(self.points[start_index][0], self.points[start_index][1])
            if not p:
                p = Blank_point(root=self.root)
                p.pos_x, p.pos_y = self.points[start_index][0], self.points[start_index][1]
                state.blank_points.append(p)
            p2 = Blank_point(root=self.root)
            p2.pos_x, p2.pos_y = self.points[stop_index-1][0], self.points[stop_index-1][1]
            state.blank_points.append(p2)
            segment = Segment(
                self.root,
                unit_size=globals.axes.unit_size,
                point_1=p,
                lower_label=lower_label,
            )
            segment.point_2 = p2
            globals.objects.register(segment)
            segment.lower_label = lower_label
            return True

        return False

    def detect_circle(self) -> bool:
        if len(self.points) < 3:
            return False

        xs, ys = zip(*self.points)
        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)

        distances = [math.hypot(x - cx, y - cy) for x, y in self.points]
        avg_r = sum(distances) / len(distances)


        max_dev = max(abs(d - avg_r) for d in distances)

        end_points_dist = math.hypot(self.points[0][0] - self.points[-1][0], self.points[0][1] - self.points[-1][1])

        if (max_dev / avg_r) < self.circle_buffer and end_points_dist < 1:
            p = Blank_point(root=self.root)
            p.pos_x, p.pos_y = cx, cy
            c = Circle_center_radius(
                root=self.root,
                point_1=p
            )
            c.radius = avg_r
            lower_label = get_lower_label(state)
            c.lower_label = lower_label
            globals.objects.register(c)

            return True

        return False

    def detect_polyline(self) -> bool:
        first = 0
        while first < len(self.points)-1:
            for last in range(len(self.points), 0, -1):
                if (self.detect_line(first, last)):
                    first = last - 1
                    break

        state.blank_points = []
        return False


    def detect_shape(self) -> None:
        if self.detect_line():
            return
        elif self.detect_circle():
            return
        elif self.detect_polyline():
            return




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
