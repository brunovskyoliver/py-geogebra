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
            p = Point(root, canvas)
            p.pos_x = e.x - objects.offset_x
            p.pos_y = e.y - objects.offset_y
            objects.register(p)

    canvas.bind("<Button-1>", left_click_pressed)
