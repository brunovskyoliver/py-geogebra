from .. import state
from ..ui.point import Point
from ..tools.utils import number_to_ascii, center
import math


def pressing(root, canvas, objects, axes):
    def left_click_pressed(e):
        if state.selected_tool == "arrow":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            items = canvas.find_overlapping(e.x, e.y, e.x + 1, e.y + 1)
            state.selected_point = None
            for obj in objects._objects:
                if hasattr(obj, "tag") and any(
                    obj.tag in canvas.gettags(i) for i in items
                ):
                    state.selected_point = obj
                    break

        elif state.selected_tool == "point":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y

            cx, cy = center(canvas, objects)
            world_x = (e.x - cx) / (objects.unit_size * objects.scale)
            world_y = (cy - e.y) / (objects.unit_size * objects.scale)
            step = axes.nice_step()
            world_x = math.floor(world_x / step + 0.5) * step
            world_y = math.floor(world_y / step + 0.5) * step

            label = number_to_ascii(state.point_counter)
            state.point_counter += 1

            p = Point(root, canvas, label=label, unit_size=axes.unit_size)
            p.pos_x = world_x
            p.pos_y = world_y
            objects.register(p)

    canvas.bind("<Button-1>", left_click_pressed)
