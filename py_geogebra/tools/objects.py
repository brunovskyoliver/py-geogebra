from typing import List, Protocol


class Drawable(Protocol):
    offset_x: float
    offset_y: float
    scale: float

    def update(self) -> None: ...


class Objects:
    def __init__(self):
        # List of all drawable objects
        self._objects: List[Drawable] = []

        # Global offsets and scale
        self.offset_x = 0
        self.offset_y = 0
        self.scale = 1.0
        self.unit_size = 20

    def register(self, obj: Drawable):
        if obj not in self._objects:
            self._objects.append(obj)
            obj.offset_x = self.offset_x
            obj.offset_y = self.offset_y
            if hasattr(obj, "scale"):
                obj.scale = self.scale
            obj.update()  # draw immediately with correct offset

    def unregister(self, obj: Drawable):
        if obj in self._objects:
            self._objects.remove(obj)

    def refresh(self):
        for obj in self._objects:
            obj.offset_x = self.offset_x
            obj.offset_y = self.offset_y

            if hasattr(obj, "scale"):
                obj.scale = self.scale
            obj.update()
