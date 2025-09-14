from .. import state


def pressing(canvas, axes):
    def left_click_pressed(e):
        if state.selected_tool == "arrow":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y

    canvas.bind("<Button-1>", left_click_pressed)
