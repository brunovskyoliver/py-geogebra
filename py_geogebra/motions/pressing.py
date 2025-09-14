from .. import state
from ..ui.point import Point


def pressing(root, canvas, objects):
    def left_click_pressed(e):
        if state.selected_tool == "arrow":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y

        elif state.selected_tool == "point":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y

            width = canvas.winfo_width()
            height = canvas.winfo_height()
            cx = width // 2 + objects.offset_x
            cy = height // 2 + objects.offset_y

            world_x = (e.x - cx) / (objects.unit_size * objects.scale)
            world_y = (cy - e.y) / (objects.unit_size * objects.scale)

            p = Point(root, canvas)
            p.pos_x = world_x
            p.pos_y = world_y
            objects.register(p)

    canvas.bind("<Button-1>", left_click_pressed)
