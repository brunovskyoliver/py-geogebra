from .. import state


def dragging(canvas, objects):
    def left_click_drag(e):
        if state.selected_tool == "arrow":
            dx = e.x - state.start_pos["x"]
            dy = e.y - state.start_pos["y"]

            objects.offset_x += dx
            objects.offset_y += dy
            objects.refresh()

            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y

    canvas.bind("<B1-Motion>", left_click_drag)
