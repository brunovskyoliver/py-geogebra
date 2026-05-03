from typing import List, Protocol

from py_geogebra.ui.compass import Compass
from py_geogebra.ui.lower_label import Lower_label
from py_geogebra.ui.semicircle import Semicircle
from py_geogebra.ui.tangents import Tangents
from .utils import center, ensure_object_color, get_default_object_color
from .. import state
import json
from ..ui.point import Point
from ..ui.intersect import Intersect
from ..ui.axes import Axes
from ..ui.line import Line
from ..ui.perpendicular_line import Perpendicular_line
from ..ui.perpendicular_bisector import Perpendicular_bisector
from ..ui.parallel_line import Parallel_line
from ..ui.ray import Ray
from ..ui.segment import Segment
from ..ui.vector import Vector
from ..ui.vector_from_point import Vector_from_point
from ..ui.segment_with_lenght import Segment_with_length
from ..ui.polyline import Polyline
from ..ui.lower_label import Lower_label
from ..ui.angle_bisector import Angle_bisector
from ..ui.area import Area
from ..ui.best_fit_line import Best_fit_line
from ..ui.polygon import Polygon
from ..ui.regular_polygon import Regular_polygon
from ..ui.circle_center_point import Circle_center_point
from ..ui.circle_center_radius import Circle_center_radius
from ..ui.circle_3_points import Circle_3_points
from ..ui.length import Length
from ..ui.slope import Slope
from ..ui.point_on_object import Point_on_object
from py_geogebra.ui.circular_arc import Circular_arc
from py_geogebra.ui.circumcircular_arc import Circumcircular_arc
from py_geogebra.ui.circular_sector import Circular_sector
from py_geogebra.ui.circumcircular_sector import Circumcircular_sector
from .. import globals
import requests
import subprocess


class Drawable(Protocol):
    scale: float

    def update(self) -> None: ...


class Objects:
    def __init__(self):
        self._objects: List[Drawable] = []
        self.canvas = globals.canvas

        self.offset_x = 0
        self.offset_y = 0
        self.scale = 1.0
        self.unit_size = 40

    def register(self, obj: Drawable):
        cx, cy = state.center
        if obj not in self._objects:
            self._objects.append(obj)
            if not isinstance(obj, (Axes, Lower_label)):
                ensure_object_color(obj)
            obj.offset_x = self.offset_x
            obj.offset_y = self.offset_y
            if hasattr(obj, "scale"):
                obj.scale = self.scale
            if hasattr(obj, "cx") and hasattr(obj, "cy"):
                obj.cx = cx
                obj.cy = cy
            obj.update()
            if hasattr(obj, "pos_x") and hasattr(obj, "pos_y"):
                globals.logger.info(f"Registered obj: {obj} x:{obj.pos_x} y:{obj.pos_y}")
            else:
                globals.logger.info(f"Registered obj: {obj}")

    def unregister(self, obj: Drawable):
        if obj in self._objects:
            self._objects.remove(obj)
            if hasattr(obj, "pos_x") and hasattr(obj, "pos_y"):
                globals.logger.info(f"UNREGISTER obj: {obj} x:{obj.pos_x} y:{obj.pos_y}")
            else:
                globals.logger.info(f"UNREGISTER obj: {obj}")

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
        def should_serialize(obj):
            if not hasattr(obj, "to_dict"):
                return False
            if isinstance(obj, Lower_label):
                return False
            if isinstance(obj, Line):
                p1_label = getattr(getattr(obj, "point_1", None), "label", None)
                p2_label = getattr(getattr(obj, "point_2", None), "label", None)
                lower_label = getattr(obj, "lower_label", None)
                if (
                    p1_label in (None, "")
                    and p2_label in (None, "")
                    and lower_label in (None, "")
                ):
                    return False
            return True

        serialized_objects = []
        for obj in sorted(
            self._objects,
            key=lambda o: 0 if getattr(o, "type", None) == "Point" else 1,
        ):
            if not should_serialize(obj):
                continue

            payload = obj.to_dict()
            if not isinstance(obj, (Axes, Lower_label)):
                payload.setdefault("color", getattr(obj, "color", get_default_object_color(obj)))
            serialized_objects.append(payload)

        return {
            "version": 1,
            "view": {
                "offset_x": self.offset_x,
                "offset_y": self.offset_y,
                "scale": self.scale,
                "unit_size": self.unit_size,
            },
            "objects": serialized_objects,
            "state": state.to_dict(),
            "sidebar": globals.sidebar.to_dict(),
        }

    def to_json(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    def load_scene_from_server(self,root,name):
        response = requests.get(f"http://127.0.0.1:5000/api/scene/{name}")
        response.raise_for_status()
        data = response.json()
        root.lift()
        cmd = ["osascript", "-e", 'tell application "Python" to activate']
        subprocess.run(cmd)

        self.load_from_dict(root, data)


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
        globals.sidebar.load_from_dict(data.get("sidebar", {}))
        globals.canvas.update_idletasks()
        state.center = center()
        state.current_polygon = None
        state.drag_target = None
        # naskor musime loadnut POINTS, lebo inak sa nam neincializuju ostatne objecty ktore na POINTS zalezia...
        for od in data.get("objects", []):
            if od["type"] == "Point":
                p = Point.from_dict(root, od)
                self.register(p)
            elif od["type"] == "Axes":
                axes = Axes.from_dict(root, od)
                self.register(axes)
                globals.axes = axes
        for od in data.get("objects", []):
            if od["type"] == "Line":
                if (
                    od.get("point_1") in (None, "")
                    and od.get("point_2") in (None, "")
                    and od.get("lower_label") in (None, "")
                ):
                    continue
                line = Line.from_dict(root, od)
                line.color = od.get("color", getattr(line, "color", get_default_object_color(line)))
                self.register(line)
            elif od["type"] == "Ray":
                ray = Ray.from_dict(root, od)
                ray.color = od.get("color", getattr(ray, "color", get_default_object_color(ray)))
                self.register(ray)
            elif od["type"] == "Segment":
                segment = Segment.from_dict(root, od)
                self.register(segment)
            elif od["type"] == "Segment With Length":
                swl = Segment_with_length.from_dict(root, od)
                swl.color = od.get("color", getattr(swl, "color", get_default_object_color(swl)))
                self.register(swl)
            elif od["type"] == "Polyline":
                polyline = Polyline.from_dict(root, od)
                polyline.color = od.get("color", getattr(polyline, "color", get_default_object_color(polyline)))
                self.register(polyline)
            elif od["type"] == "Polygon":
                polygon = Polygon.from_dict(root, od)
                polygon.color = od.get("color", getattr(polygon, "color", get_default_object_color(polygon)))
                self.register(polygon)
            elif od["type"] == "Regular_polygon":
                polygon = Regular_polygon.from_dict(root, od)
                polygon.color = od.get("color", getattr(polygon, "color", get_default_object_color(polygon)))
                self.register(polygon)
            elif od["type"] == "Vector":
                vector = Vector.from_dict(root, od)
                vector.color = od.get("color", getattr(vector, "color", get_default_object_color(vector)))
                self.register(vector)
            elif od["type"] == "Vector_from_point":
                vector = Vector_from_point.from_dict(root, od)
                vector.color = od.get("color", getattr(vector, "color", get_default_object_color(vector)))
                self.register(vector)
            elif od["type"] == "Perpendicular_line":
                vector = Perpendicular_line.from_dict(root, od)
                vector.color = od.get("color", getattr(vector, "color", get_default_object_color(vector)))
                self.register(vector)
            elif od["type"] == "Parallel_line":
                vector = Parallel_line.from_dict(root, od)
                vector.color = od.get("color", getattr(vector, "color", get_default_object_color(vector)))
                self.register(vector)
            elif od["type"] == "Perpendicular_bisector":
                vector = Perpendicular_bisector.from_dict(root, od)
                vector.color = od.get("color", getattr(vector, "color", get_default_object_color(vector)))
                self.register(vector)
            elif od["type"] == "Angle_bisector":
                vector = Angle_bisector.from_dict(root, od)
                vector.color = od.get("color", getattr(vector, "color", get_default_object_color(vector)))
                self.register(vector)
            elif od["type"] == "Best_fit_line":
                vector = Best_fit_line.from_dict(root, od)
                vector.color = od.get("color", getattr(vector, "color", get_default_object_color(vector)))
                self.register(vector)
            elif od["type"] == "Circle_center_point":
                c = Circle_center_point.from_dict(root, od)
                c.color = od.get("color", getattr(c, "color", get_default_object_color(c)))
                self.register(c)
            elif od["type"] == "Circle_3_points":
                c = Circle_3_points.from_dict(root, od)
                c.color = od.get("color", getattr(c, "color", get_default_object_color(c)))
                self.register(c)
            elif od["type"] == "Circle_center_radius":
                c = Circle_center_radius.from_dict(root, od)
                c.color = od.get("color", getattr(c, "color", get_default_object_color(c)))
                self.register(c)
            elif od["type"] == "Compass":
                c = Compass.from_dict(root, od)
                c.color = od.get("color", getattr(c, "color", get_default_object_color(c)))
                self.register(c)
            elif od["type"] == "Intersect":
                i = Intersect.from_dict(root, od)
                i.color = od.get("color", getattr(i, "color", get_default_object_color(i)))
                self.register(i)
            elif od["type"] == "Semicircle":
                c = Semicircle.from_dict(root, od)
                c.color = od.get("color", getattr(c, "color", get_default_object_color(c)))
                self.register(c)
            elif od["type"] in ("Tangnets", "Tangents"):
                c = Tangents.from_dict(root, od)
                self.register(c)
            elif od["type"] == "Circular_arc":
                c = Circular_arc.from_dict(root, od)
                c.color = od.get("color", getattr(c, "color", get_default_object_color(c)))
                self.register(c)
            elif od["type"] == "Circumcircular_arc":
                c = Circumcircular_arc.from_dict(root, od)
                c.color = od.get("color", getattr(c, "color", get_default_object_color(c)))
                self.register(c)
            elif od["type"] == "Circular_sector":
                c = Circular_sector.from_dict(root, od)
                c.color = od.get("color", getattr(c, "color", get_default_object_color(c)))
                self.register(c)
            elif od["type"] == "Circumcircular_sector":
                c = Circumcircular_sector.from_dict(root, od)
                c.color = od.get("color", getattr(c, "color", get_default_object_color(c)))
                self.register(c)
            elif od["type"] == "Length":
                c = Length.from_dict(root, od)
                c.color = od.get("color", getattr(c, "color", get_default_object_color(c)))
                self.register(c)
            elif od["type"] == "Slope":
                c = Slope.from_dict(root, od)
                c.color = od.get("color", getattr(c, "color", get_default_object_color(c)))
                self.register(c)

        for od in data.get("objects", []):
            if od["type"] in ("Lower_label", "Lower Label"):
                ll = Lower_label.from_dict(root, od)
                self.register(ll)

        for od in data.get("objects", []):
            if od["type"] == "Point_on_object":
                ll = Point_on_object.from_dict(root, od)
                ll.color = od.get("color", getattr(ll, "color", get_default_object_color(ll)))
                self.register(ll)

        for od in data.get("objects", []):
            if od["type"] == "Area":
                ll = Area.from_dict(root, od)
                ll.color = od.get("color", getattr(ll, "color", get_default_object_color(ll)))
                self.register(ll)

        if "sidebar" in data and "order" in data["sidebar"]:
            self.restore_sidebar_order(data["sidebar"]["order"])

        # XD SYNTAX - MILUJEM PYTHON
        for obj in self._objects:
            if isinstance(obj, Lower_label) and obj.obj:
                obj.obj.lower_label_obj = obj
                try:
                    obj.obj.update()
                except Exception as ex:
                    globals.logger.warning(
                        f"Skipping lower-label relink update for {obj.obj}: {ex}"
                    )
        globals.canvas.update_idletasks()
        state.center = center()
        self.refresh()

        return self
