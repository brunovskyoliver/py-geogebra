import tkinter as tk

from py_geogebra.ui.blank_point import Blank_point
from py_geogebra.ui.line import Line
from ..tools.utils import (
    distance,
    world_to_screen,
    snap_to_line,
    get_linear_fuction_prescription,
    calculate_vector,
    load_lines_from_labels,
)
from .. import state
from .lower_label import Lower_label
import math
from .. import globals



class Tangents:
    def __init__(
        self,
        root: tk.Tk,
        unit_size: int = 40,
        point_1=None,
    ):
        self.root = root
        self.canvas = globals.canvas
        self.objects = globals.objects

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

        self.is_drawable = True
        self.deleted = False

        self.point_1 = point_1
        self.point_2_1 = Blank_point(root)
        self.point_2_2 = Blank_point(root) # preco ma kruznica dve dotycnice?

        self.line_1 = None
        self.line_2 = None

        self.circle = None

    def to_dict(self) -> dict:
        return {
            "type": "Tangents",
            "pos_x": self.pos_x,
            "pos_y": self.pos_y,
            "unit_size": self.unit_size,
            "scale": self.scale,
            "is_drawable": self.is_drawable,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "point_1": self.point_1.label if self.point_1 else None,
            "point_2_1": self.point_2_1.label if self.point_2_1 else None,
            "point_2_2": self.point_2_2.label if self.point_2_2 else None,
            "circle": self.circle.lower_label if self.circle else None,
            "line_1": self.line_1.lower_label if self.line_1 else None,
            "line_2": self.line_2.lower_label if self.line_2 else None,
        }

    @classmethod
    def from_dict(cls, root, data: dict):
        def find_point(label):
            for obj in globals.objects._objects:
                if getattr(obj, "label", None) == label:
                    return obj
            return None

        def find_line(label):
            for obj in globals.objects._objects:
                if getattr(obj, "lower_label", None) == label:
                    return obj
            return None

        p1 = find_point(data.get("point_1"))
        p2_1 = find_point(data.get("point_2_1"))
        p2_2 = find_point(data.get("point_2_2"))
        line = cls(root=root, point_1=p1, unit_size=data.get("unit_size", 40))
        line.point_2_1 = p2_1
        line.point_2_2 = p2_2
        line.circle = find_line(data.get("circle"))
        line.line_1 = find_line(data.get("line_1"))
        line.line_2 = find_line(data.get("line_2"))
        line.scale = data.get("scale", 1.0)
        line.is_drawable = data.get("is_drawable", True)
        line.offset_x = data.get("offset_x", 0)
        line.offset_y = data.get("offset_y", 0)
        line.pos_x = data.get("pos_x", 0)
        line.pos_y = data.get("pos_y", 0)
        cx, cy = state.center
        line.cx = cx
        line.cy = cy
        line.update()
        return line

    def select(self):
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def update(self, e=None):
        if not self.line_1:
            self.line_1 = Line(root=self.root, point_1=self.point_1)
            self.line_1.point_2 = self.point_2_1
        if not self.line_2:
            self.line_2 = Line(root=self.root, point_1=self.point_1)
            self.line_2.point_2 = self.point_2_2


        try:
            angle = math.asin(self.circle.radius / distance(self.circle.center.pos_x, self.circle.center.pos_y, self.point_1.pos_x, self.point_1.pos_y))
        except ValueError:
            angle = 0


        if angle == 0:
            self.point_2_1.is_drawable = False
            self.point_2_2.is_drawable = False
        else:
            self.point_2_1.is_drawable = True
            self.point_2_2.is_drawable = True


        vec = [self.circle.center.pos_x - self.point_1.pos_x, self.circle.center.pos_y - self.point_1.pos_y]
        rot_matrix_1 = [[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]]
        new_vec_1 = [rot_matrix_1[0][0] * vec[0] + rot_matrix_1[0][1] * vec[1], rot_matrix_1[1][0] * vec[0] + rot_matrix_1[1][1] * vec[1]]
        rot_matrix_2 = [[math.cos(-angle), -math.sin(-angle)], [math.sin(-angle), math.cos(-angle)]]
        new_vec_2 = [rot_matrix_2[0][0] * vec[0] + rot_matrix_2[0][1] * vec[1], rot_matrix_2[1][0] * vec[0] + rot_matrix_2[1][1] * vec[1]]

        self.point_2_1.pos_x = self.point_1.pos_x + new_vec_1[0]
        self.point_2_1.pos_y = self.point_1.pos_y + new_vec_1[1]
        self.point_2_2.pos_x = self.point_1.pos_x - new_vec_2[0]
        self.point_2_2.pos_y = self.point_1.pos_y - new_vec_2[1]

        self.line_1.update()
        self.line_2.update()
