from .. import state
from ..tools.utils import center


def dragging(root, canvas, objects):
    def left_click_drag(e):
        if state.selected_tool == "arrow":
            if state.selected_point is None:
                dx = e.x - state.start_pos["x"]
                dy = e.y - state.start_pos["y"]
                objects.offset_x += dx
                objects.offset_y += dy
                objects.refresh()
                state.start_pos["x"] = e.x
                state.start_pos["y"] = e.y
            else:
                cx, cy = center(canvas, objects)
                world_x = (e.x - cx) / (objects.unit_size * objects.scale)
                world_y = (cy - e.y) / (objects.unit_size * objects.scale)

                state.selected_point.pos_x = world_x
                state.selected_point.pos_y = world_y
                state.selected_point.update()

        elif state.selected_tool == "pen":
            pass

    canvas.bind("<B1-Motion>", left_click_drag)
