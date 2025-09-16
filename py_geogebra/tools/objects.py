from typing import List, Protocol
import tkinter as tk
from .utils import center
from .. import state


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
        state.center = center(self.canvas, self)
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
