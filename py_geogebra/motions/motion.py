from .. import state
from ..tools.utils import center, set_cursor


def motion(root, canvas, objects, axes):
    def handle_mouse(e):
        if state.selected_tool == "line" and 0 < len(state.points_for_obj) < 3:
            state.points_for_obj[1].update(e)
            
        if state.selected_tool == "segment" and 0 < len(state.points_for_obj) < 3:
            state.points_for_obj[1].update(e)

    canvas.bind("<Motion>", handle_mouse)
