from typing import List, Protocol

from py_geogebra.ui.lower_label import Lower_label
from .utils import center
from .. import state
import json
from ..ui.point import Point
from ..ui.axes import Axes
from ..ui.line import Line
from ..ui.perpendicular_line import Perpendicular_line
from ..ui.ray import Ray
from ..ui.segment import Segment
from ..ui.vector import Vector
from ..ui.vector_from_point import Vector_from_point
from ..ui.segment_with_lenght import Segment_with_length
from ..ui.polyline import Polyline
from ..ui.lower_label import Lower_label
from .. import globals


class Drawable(Protocol):
    offset_x: float
    offset_y: float
    scale: float

    def update(self) -> None: ...


class Objects:
    def __init__(self):
        # List of all drawable objects
        self._objects: List[Drawable] = []
        self.canvas = globals.canvas

        # Global offsets and scale
        self.offset_x = 0
        self.offset_y = 0
        self.scale = 1.0
        self.unit_size = 40

    def register(self, obj: Drawable):
        cx, cy = state.center
        if obj not in self._objects:
            self._objects.append(obj)
            obj.offset_x = self.offset_x
            obj.offset_y = self.offset_y
            if hasattr(obj, "scale"):
                obj.scale = self.scale
            if hasattr(obj, "cx") and hasattr(obj, "cy"):
                obj.cx = cx
                obj.cy = cy
            obj.update()

    def unregister(self, obj: Drawable):
        if obj in self._objects:
            self._objects.remove(obj)

    def refresh(self):
        state.center = center()
        cx, cy = state.center
        for obj in self._objects:
            obj.offset_x = self.offset_x
            obj.offset_y = self.offset_y

            if hasattr(obj, "scale"):
                obj.scale = self.scale
            if hasattr(obj, "cx") and hasattr(obj, "cy"):
                obj.cx = cx
                obj.cy = cy
            obj.update()

    def restore_sidebar_order(self, order_tags):
        tags = {}
        for obj in globals.objects._objects:
            if hasattr(obj, "tag") and not isinstance(obj, Lower_label):
                tags[obj.tag] = obj

        globals.sidebar.items.clear()
        for tag in order_tags:
            obj = tags.get(tag)
            if obj:
                globals.sidebar.items.append(obj)

        globals.sidebar.update()

    def to_dict(self):
        return {
            "version": 1,
            "view": {
                "offset_x": self.offset_x,
                "offset_y": self.offset_y,
                "scale": self.scale,
                "unit_size": self.unit_size,
            },
            "objects": [
                obj.to_dict()
                for obj in sorted(
                    self._objects,
                    key=lambda o: 0 if getattr(o, "type", None) == "Point" else 1,
                )
                if hasattr(obj, "to_dict")
            ],
            "state": state.to_dict(),
            "sidebar": globals.sidebar.to_dict(),
        }

    def to_json(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    def load_from_dict(self, root, data: dict):
        globals.canvas.delete("all")
        view = data.get("view", {})
        self.offset_x = view.get("offset_x", 0)
        self.offset_y = view.get("offset_y", 0)
        self.scale = view.get("scale", 1.0)
        self.unit_size = view.get("unit_size", 40)
        self._objects.clear()
        state.load_from_dict(data.get("state", {}))
        state.selected_tool = "arrow"
        state.shift_pressed = False
        state.center = center()
        globals.sidebar.load_from_dict(data.get("sidebar", {}))
        # naskor musime loadnut POINTS, lebo inak sa nam neincializuju ostatne objecty ktore na POINTS zalezia...
        for od in data.get("objects", []):
            if od["type"] == "Point":
                p = Point.from_dict(root, od)
                self.register(p)
            elif od["type"] == "Axes":
                axes = Axes.from_dict(root, od)
                self.register(axes)
        for od in data.get("objects", []):
            if od["type"] == "Line":
                line = Line.from_dict(root, od)
                self.register(line)
            elif od["type"] == "Ray":
                ray = Ray.from_dict(root, od)
                self.register(ray)
            elif od["type"] == "Segment":
                segment = Segment.from_dict(root, od)
                self.register(segment)
            elif od["type"] == "Segment With Length":
                swl = Segment_with_length.from_dict(root, od)
                self.register(swl)
            elif od["type"] == "Polyline":
                polyline = Polyline.from_dict(root, od)
                self.register(polyline)
            elif od["type"] == "Vector":
                vector = Vector.from_dict(root, od)
                self.register(vector)
            elif od["type"] == "Vector_from_point":
                vector = Vector_from_point.from_dict(root, od)
                self.register(vector)
            elif od["type"] == "Perpendicular_line":
                vector = Perpendicular_line.from_dict(root, od)
                self.register(vector)

        for od in data.get("objects", []):
            if od["type"] == "Lower_label":
                ll = Lower_label.from_dict(root, od)
                self.register(ll)

        if "sidebar" in data and "order" in data["sidebar"]:
            self.restore_sidebar_order(data["sidebar"]["order"])

        # XD SYNTAX - MILUJEM PYTHON
        for obj in self._objects:
            if isinstance(obj, Lower_label) and obj.obj:
                obj.obj.lower_label_obj = obj
                obj.obj.update()
        self.refresh()

        return self
