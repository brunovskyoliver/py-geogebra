from .. import state
from ..ui.point import Point
from ..tools.utils import number_to_ascii


def pressing(root, canvas, objects):
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

            width = canvas.winfo_width()
            height = canvas.winfo_height()
            cx = width // 2 + objects.offset_x
            cy = height // 2 + objects.offset_y

            world_x = (e.x - cx) / (objects.unit_size * objects.scale)
            world_y = (cy - e.y) / (objects.unit_size * objects.scale)

            label = number_to_ascii(state.point_counter)
            state.point_counter += 1

            p = Point(root, canvas, label=label)
            p.pos_x = world_x
            p.pos_y = world_y
            objects.register(p)

    canvas.bind("<Button-1>", left_click_pressed)
    canvas.bind("<ButtonRelease-1>", lambda e: setattr(state, "selected_point", None))
