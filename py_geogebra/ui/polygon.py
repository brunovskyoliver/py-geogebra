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
        self.is_drawable = True

        self.line_points = []
        self.points = []
        self.segments = []
        self.last_not_set = True
        self.lower_label = ""
        self.lower_label_obj = Lower_label(self.root, obj=self)
        self.objects.register(self.lower_label_obj)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

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
            "is_drawable": self.is_drawable,
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
        polygon.is_drawable = data.get("is_drawable", True)
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

    def _on_canvas_configure(self, e=None):
        if e and e.width > 0 and e.height > 0:
            self.update()

    def handle_segments(self):
        from .segment import Segment

        if len(self.line_points) < 2:
            self.segments.clear()
            return

        pairs = []
        for i in range(len(self.line_points) - 1):
            pairs.append((self.line_points[i], self.line_points[i + 1]))

        if not self.last_not_set and len(self.line_points) > 2:
            pairs.append((self.line_points[-1], self.line_points[0]))

        def segment_points(segment):
            return segment.point_1, segment.point_2

        segments = []
        for segment in self.segments:
            if not segment or not segment.point_1 or not segment.point_2:
                continue
            p1, p2 = segment_points(segment)
            if (p1, p2) in pairs or (p2, p1) in pairs:
                segments.append(segment)
        self.segments = segments

        for p1, p2 in pairs:
            exists = any(
                (segment.point_1 == p1 and segment.point_2 == p2)
                or (segment.point_1 == p2 and segment.point_2 == p1)
                for segment in self.segments
            )
            if not exists:
                segment = Segment(self.root, point_1=p1)
                segment.point_2 = p2
                segment.parent = self
                segment.color = "#FF0000"
                segment.update()
                self.objects.register(segment)
                self.segments.append(segment)

        for segment in self.segments:
            segment.update()


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

        if len(self.line_points)>=2:
            if not self.line_points[0].is_drawable or not self.line_points[1].is_drawable:
                self.is_drawable = False
            else:
                self.is_drawable = True

        for p in self.line_points:
            coords.extend([p.x, p.y])
            p.is_drawable = self.is_drawable


        if self.last_not_set and e is not None:
            coords.extend([e.x, e.y])

        for obj in self.points:
            if obj.translation > 1:
                obj.translation = 1
            elif obj.translation < 0:
                obj.translation = 0
            snap_to_polyline(obj, self)
            obj.update()


        if self.is_drawable:
            if len(coords) < 4:
                return
            if not self.last_not_set:
                coords.extend([self.line_points[0].x,self.line_points[0].y])
            if self.selected:
                self.canvas.create_line(
                    *coords,
                    fill="lightgrey",
                    width=2 * 3 * visual_scale,
                    tags=(self.tag, "under_line"),
                )
            self.canvas.tag_lower("under_line")

            items = self.canvas.find_all()

            polygon_fill = self.canvas.create_polygon(
                *coords,
                fill="#D9AEA0",
                outline="",
                tags=(self.tag, "polygon_fill"),
            )


            if items:
                self.canvas.tag_lower(polygon_fill, items[0])

        # self.canvas.create_line(
        #     *coords,
        #     fill="#FF0000",
        #     width=5 * visual_scale,
        #     tags=(self.tag, "polygon_alpha"),
        # )


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

        for p in self.points:
            self.canvas.tag_raise(p.tag)
        for p in self.line_points:
            self.canvas.tag_raise(p.tag)


        self.prev_x, self.prev_y = self.pos_x, self.pos_y
