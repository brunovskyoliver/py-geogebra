from .. import state
from ..tools.utils import center, set_cursor
from .. import globals


def motion(root):
    def handle_mouse(e):
        if state.selected_tool == "line" and 0 < len(state.points_for_obj) < 3:
            state.points_for_obj[1].update(e)

        if state.selected_tool == "segment" and 0 < len(state.points_for_obj) < 3:
            state.points_for_obj[1].update(e)

        if state.selected_tool == "ray" and 0 < len(state.points_for_obj) < 3:
            state.points_for_obj[1].update(e)

        if (
            state.selected_tool == "polyline"
            and state.current_polyline is not None
            and state.current_polyline.last_not_set
        ):
            state.current_polyline.update(e)

        if (
            state.selected_tool == "polygon"
            and state.current_polygon is not None
            and state.current_polygon.last_not_set
        ):
            state.current_polygon.update(e)


        if state.selected_tool == "vector" and 0 < len(state.points_for_obj) < 3:
            state.points_for_obj[1].update(e)

        if state.selected_tool == "perpendicular_bisector" and 1 <= len(state.points_for_obj) <3:
            state.points_for_obj[1].update(e)

        if state.selected_tool == "circle_center_point" and 0 < len(state.points_for_obj) < 3:
            state.points_for_obj[1].update(e)

        if state.selected_tool == "compass" and 2 < len(state.points_for_obj) < 4:
                state.points_for_obj[2].update(e)

    globals.canvas.bind("<Motion>", handle_mouse)
