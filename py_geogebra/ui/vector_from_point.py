import tkinter as tk
from ..tools.utils import (
    world_to_screen,
    distance,
    snap_to_line,
    calculate_vector,
    load_lines_from_labels,
)
from .. import state
from .lower_label import Lower_label
from .. import globals


class Vector_from_point:
    def __init__(
        self,
        root: tk.Tk,
        unit_size: int = 40,
        point_1=None,
        lower_label: str = "",
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
        self.length = 0.0

        self.cx = 0
        self.cy = 0
        
        self.parent_vector = None

        self.selected = False

        self.is_drawable = True

        self.tag = f"vector_{id(self)}"
        self.point_1 = point_1
        self.point_2 = None
        self.lower_label = lower_label
        self.lower_label_obj = Lower_label(self.root, obj=self)
        self.objects.register(self.lower_label_obj)
        self.vector = (0,0)
        self.child_lines = []
        self.child_lines_labels = []

        self.points = [self.point_1]
        self.canvas.bind("<Configure>", lambda e: self.update())

    def to_dict(self) -> dict:
        return {
            "type": "Vector_from_point",
            "lower_label": self.lower_label,
            "pos_x": self.pos_x,
            "pos_y": self.pos_y,
            "unit_size": self.unit_size,
            "scale": self.scale,
            "is_drawable": self.is_drawable,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "tag": self.tag,
            "points": [p.label for p in self.points],
            "point_1": self.point_1.label if self.point_1 else None,
            "point_2": self.point_2.label if self.point_2 else None,
            "parent_vector": self.parent_vector.lower_label,
            "vector": self.vector,
            "child_lines_labels": [l.lower_label for l in self.child_lines]
        }

    @classmethod
    def from_dict(cls, root, data: dict):
        def find_point(label):
            for obj in globals.objects._objects:
                if getattr(obj, "label", None) == label:
                    return obj
            return None
        def find_vector(label):
            for obj in globals.objects._objects:
                if getattr(obj, "lower_label", None) == label:
                    return obj
            return None

        p1 = find_point(data.get("point_1"))
        p2 = find_point(data.get("point_2"))
        vector = cls(root=root, point_1=p1, unit_size=data.get("unit_size", 40))
        vector.point_2 = p2
        vector.scale = data.get("scale", 1.0)
        vector.is_drawable = data.get("is_drawable", True)
        vector.offset_x = data.get("offset_x", 0)
        vector.offset_y = data.get("offset_y", 0)
        vector.lower_label = data.get("lower_label", "")
        vector.tag = data.get("tag", "")
        vector.lower_label_obj = Lower_label(root, obj=vector)
        globals.objects.register(vector.lower_label_obj)
        vector.pos_x = data.get("pos_x", 0)
        vector.pos_y = data.get("pos_y", 0)
        vector.points = [find_point(lbl) for lbl in data.get("points", []) if lbl]
        vector.parent_vector = find_vector(data.get("parent_vector", ""))
        vector.parent_vector.loaded_children = False
        vector.vector = data.get("vector")
        vector.child_lines_labels = [lbl for lbl in data.get("child_lines_labels", [])]
        cx, cy = state.center
        vector.cx = cx
        vector.cy = cy
        vector.update()
        return vector

    def select(self):
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def update(self, e=None):
        self.canvas.delete(self.tag)
        
        

        visual_scale = min(max(1, self.scale**0.5), 1.9)

        if state.drag_target is self:

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

        for obj in self.points:
            if (obj is self.point_1) or (obj is self.point_2):
                continue
            if obj.translation > 1:
                obj.translation = 1
            elif obj.translation < 0:
                obj.translation = 0
            snap_to_line(obj, self)
            obj.update()
            
            
        if self.point_2 is not None:          
            self.vector = calculate_vector(self.point_1, self.point_2)

        if not self.point_2:
            self.is_drawable = True
        elif self.point_1.is_drawable and self.point_2.is_drawable:
            self.is_drawable = True
        else:
            self.is_drawable = False
            
        self.lower_label_obj.is_drawable = self.is_drawable 

        if self.is_drawable:
            if self.point_2 is None:
                cx, cy = state.center
                x2 = (e.x - cx) / (self.unit_size * self.scale)
                y2 = (cy - e.y) / (self.unit_size * self.scale)
            else:
                self.point_2.pos_x=self.point_1.pos_x + (self.parent_vector.point_2.pos_x - self.parent_vector.point_1.pos_x)
                self.point_2.pos_y=self.point_1.pos_y + (self.parent_vector.point_2.pos_y - self.parent_vector.point_1.pos_y)
                x2, y2 = self.point_2.pos_x, self.point_2.pos_y
                self.length = distance(x1, y1, x2, y2, 2)
                self.lower_label_obj.update()

            x1, y1 = world_to_screen(x1, y1)
            x2, y2 = world_to_screen(x2, y2)

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
                arrow=tk.LAST,
                arrowshape=(12, 15, 4),
                width=2 * visual_scale,
                tags=self.tag,
            )
        self.canvas.tag_raise(self.point_1.tag)
        if self.point_2 is not None:
            self.canvas.tag_raise(self.point_2.tag)
            if self.point_2 not in self.points:
                self.points.append(self.point_2)
                
                
        if len(self.child_lines) == 0:
            self.child_lines = load_lines_from_labels(self.child_lines_labels)

        for p in self.points:
            self.canvas.tag_raise(p.tag)
            p.update()
        for l in self.child_lines:
            if l:
                l.parent_vector = self.vector
                l.update()

        self.prev_x, self.prev_y = self.pos_x, self.pos_y
