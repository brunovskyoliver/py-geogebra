import tkinter as tk
from ..tools.utils import distance, snap_to_polyline
from .. import state
from .. import globals
from .lower_label import Lower_label


class Polygon:
    def __init__(
        self,
        root: tk.Tk,
        unit_size: int = 40,
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

        self.tag = f"polygon_{id(self)}"

        self.selected = False

        self.line_points = []
        self.points = []
        self.last_not_set = True
        self.lower_label = ""
        self.lower_label_obj = Lower_label(self.root, obj=self)
        self.objects.register(self.lower_label_obj)
        self.canvas.bind("<Configure>", lambda e: self.update())

    def to_dict(self) -> dict:
        return {
            "type": "Polygon",
            "lower_label": self.lower_label,
            "pos_x": self.pos_x,
            "pos_y": self.pos_y,
            "unit_size": self.unit_size,
            "scale": self.scale,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "tag": self.tag,
            "points": [p.label for p in self.points],
            "line_points": [p.label for p in self.line_points],
            "last_not_set": self.last_not_set,
        }

    @classmethod
    def from_dict(cls, root, data: dict):
        def find_point(label):
            for obj in globals.objects._objects:
                if getattr(obj, "label", None) == label:
                    return obj
            return None

        polygon = cls(root=root, unit_size=data.get("unit_size", 40))
        polygon.scale = data.get("scale", 1.0)
        polygon.offset_x = data.get("offset_x", 0)
        polygon.offset_y = data.get("offset_y", 0)
        polygon.lower_label = data.get("lower_label", "")
        polygon.tag = data.get("tag", "")
        polygon.pos_x = data.get("pos_x", 0)
        polygon.pos_y = data.get("pos_y", 0)
        polygon.last_not_set = data.get("last_not_set", False)
        polygon.points = [find_point(lbl) for lbl in data.get("points", []) if lbl]
        polygon.line_points = [
            find_point(lbl) for lbl in data.get("line_points", []) if lbl
        ]
        cx, cy = state.center
        polygon.cx = cx
        polygon.cy = cy
        polygon.update()
        return polygon

    def select(self):
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def update(self, e=None):
        length = 0.0
        for p in self.line_points:
            p.offset_x = self.offset_x
            p.offset_y = self.offset_y
            p.scale = self.scale
            p.cx = self.cx
            p.cy = self.cy
            p.update()

        self.canvas.delete(self.tag)

        visual_scale = min(max(1, self.scale**0.5), 1.9)

        coords = []

        if state.drag_target is self:

            x_dif, y_dif = self.prev_x - self.pos_x, self.prev_y - self.pos_y

            for obj in self.line_points:
                obj.pos_x -= x_dif
                obj.pos_y -= y_dif

        for p in self.line_points:
            coords.extend([p.x, p.y])


        if self.last_not_set and e is not None:
            coords.extend([e.x, e.y])

        for obj in self.points:
            if obj.translation > 1:
                obj.translation = 1
            elif obj.translation < 0:
                obj.translation = 0
            snap_to_polyline(obj, self)
            obj.update()

        if len(coords) < 4:
            return
        if not self.last_not_set:
            coords.extend([self.line_points[0].x,self.line_points[0].y])
        if self.selected:
            self.canvas.create_line(
                *coords,
                fill="lightgrey",
                width=2 * 3 * visual_scale,
                tags=self.tag,
            )

        self.canvas.create_line(
            *coords,
            fill="black",
            width=2 * visual_scale,
            tags=(self.tag, "polygon_alpha"),
        )
        self.canvas.create_polygon(*coords,fill="orange",tags=self.tag)
        if not self.last_not_set and self.line_points:
            for i in range(0, len(self.line_points), 2):
                if i + 2 <= len(self.line_points):
                    line_points = self.line_points[i : i + 2]
                    length += distance(
                        line_points[0].pos_x,
                        line_points[0].pos_y,
                        line_points[1].pos_x,
                        line_points[1].pos_y,
                        2,
                    )
            self.lower_label_obj.update()
        self.length = length

        for p in self.line_points:
            self.canvas.tag_raise(p.tag)
        for p in self.points:
            self.canvas.tag_raise(p.tag)

        self.canvas.tag_lower("polygon_alpha")

        self.prev_x, self.prev_y = self.pos_x, self.pos_y
