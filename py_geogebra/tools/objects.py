from types import FunctionType
from typing import List, Protocol
import tkinter as tk
from .utils import center
from .. import state
import json
import inspect
from ..ui.point import Point
from ..ui.axes import Axes
from .. import globals


class Drawable(Protocol):
    offset_x: float
    offset_y: float
    scale: float

    def update(self) -> None: ...


class Objects:
    def __init__(self, canvas: tk.Canvas):
        # List of all drawable objects
        self._objects: List[Drawable] = []
        self.canvas = canvas

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
                obj.to_dict() for obj in self._objects if hasattr(obj, "to_dict")
            ],
            "state": state.to_dict(),
        }

    def to_json(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    def load_from_dict(self, root, data: dict):
        view = data.get("view", {})
        self.offset_x = view.get("offset_x", 0)
        self.offset_y = view.get("offset_y", 0)
        self.scale = view.get("scale", 1.0)
        self.unit_size = view.get("unit_size", 40)
        self._objects.clear()
        state.load_from_dict(data.get("state", {}))
        state.selected_tool = "arrow"
        state.center = center()
        for od in data.get("objects", []):
            if od["type"] == "Point":
                p = Point.from_dict(root, self, od)
                self.register(p)
            elif od["type"] == "Axes":
                axes = Axes.from_dict(root, self, data)
                self.register(axes)
        self.refresh()
        return self
