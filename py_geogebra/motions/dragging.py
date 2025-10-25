from .. import state
from ..tools.utils import (
    set_cursor,
    find_translation,
    find_translation_polyline,
)
from ..ui.line import Line
from ..ui.ray import Ray
from ..ui.segment_with_lenght import Segment_with_length
from ..ui.midpoint_or_center import Midpoint_or_center
from ..ui.segment import Segment
from ..ui.vector import Vector
from ..ui.polyline import Polyline
from ..ui.intersect import Intersect
from ..ui.perpendicular_bisector import Perpendicular_bisector
from .. import globals


def dragging(root):
    def left_click_drag(e):
        if state.selected_tool == "arrow":
            if state.drag_target is None:
                dx = e.x - state.start_pos["x"]
                dy = e.y - state.start_pos["y"]
                globals.objects.offset_x += dx
                globals.objects.offset_y += dy

                width = globals.canvas.winfo_width()
                height = globals.canvas.winfo_height()
                state.center = (
                    width // 2 + globals.objects.offset_x,
                    height // 2 + globals.objects.offset_y,
                )

                globals.objects.refresh()
                state.start_pos["x"] = e.x
                state.start_pos["y"] = e.y

            else:
                cx, cy = state.center
                world_x = (e.x - cx) / (
                    globals.objects.unit_size * globals.objects.scale
                )
                world_y = (cy - e.y) / (
                    globals.objects.unit_size * globals.objects.scale
                )

                if state.shift_pressed and not isinstance(state.drag_target, Intersect):
                    state.drag_target.snap_point(e)
                else:
                    state.drag_target.pos_x = world_x
                    state.drag_target.pos_y = world_y
                    state.drag_target.update()

                for obj in globals.objects._objects:
                    if (
                        isinstance(obj, Line)
                        or isinstance(obj, Segment)
                        or isinstance(obj, Ray)
                        or isinstance(obj, Segment_with_length)
                        or isinstance(obj, Midpoint_or_center)
                        or isinstance(obj, Vector)
                        or isinstance(obj, Perpendicular_bisector)
                    ):
                        if (
                            obj.point_1 is state.drag_target
                            or obj.point_2 is state.drag_target
                        ):
                            obj.update()
                        elif hasattr(obj, "points") and state.drag_target in obj.points:
                            state.drag_target.pos_x = world_x
                            state.drag_target.pos_y = world_y
                            state.drag_target.update()
                            find_translation(state.drag_target, obj)
                            obj.update()
                        elif (
                            state.drag_target is not obj.point_1
                            and state.drag_target is not obj.point_2
                        ):
                            globals.objects.refresh()
                    elif isinstance(obj, Polyline):
                        if state.drag_target in obj.line_points:
                            obj.update()
                        elif state.drag_target in obj.points:
                            state.drag_target.pos_x = world_x
                            state.drag_target.pos_y = world_y
                            state.drag_target.update()
                            find_translation_polyline(state.drag_target, obj)
                            obj.update()
                        else:
                            globals.objects.refresh()
                globals.sidebar.update()

        elif state.selected_tool == "pen" and state.current_pen is not None:
            cx, cy = state.center
            world_x = (e.x - cx) / (globals.objects.unit_size * globals.objects.scale)
            world_y = (cy - e.y) / (globals.objects.unit_size * globals.objects.scale)
            state.current_pen.add_point(world_x, world_y)

        elif state.selected_tool == "freehand":
            cx, cy = state.center
            world_x = (e.x - cx) / (globals.objects.unit_size * globals.objects.scale)
            world_y = (cy - e.y) / (globals.objects.unit_size * globals.objects.scale)
            state.current_pen.add_point(world_x, world_y)

    def right_click_drag(e):
        if state.selected_tool == "pen":
            set_cursor(globals.canvas, "circle")
            r = 8
            items = globals.canvas.find_overlapping(e.x - r, e.y - r, e.x + r, e.y + r)
            for obj in globals.objects._objects:
                if hasattr(obj, "tag") and any(
                    obj.tag in globals.canvas.gettags(i) for i in items
                ):
                    if "pen" in obj.tag:
                        cx, cy = state.center
                        world_x = (e.x - cx) / (
                            globals.objects.unit_size * globals.objects.scale
                        )
                        world_y = (cy - e.y) / (
                            globals.objects.unit_size * globals.objects.scale
                        )
                        obj.delete_point(world_x, world_y, r=0.2)
                        break

    def middle_click_drag(e):
        dx = e.x - state.start_pos["x"]
        dy = e.y - state.start_pos["y"]
        globals.objects.offset_x += dx
        globals.objects.offset_y += dy

        width = globals.canvas.winfo_width()
        height = globals.canvas.winfo_height()
        state.center = (
            width // 2 + globals.objects.offset_x,
            height // 2 + globals.objects.offset_y,
        )

        globals.objects.refresh()
        state.start_pos["x"] = e.x
        state.start_pos["y"] = e.y

    def left_click_drag_sidebar(e):
        if state.sidebar_resizing:
            new_width = max(50, e.x)
            globals.sidebar.resize(new_width)

    globals.canvas.bind("<B1-Motion>", left_click_drag)
    globals.canvas.bind("<B2-Motion>", right_click_drag)
    globals.canvas.bind("<B3-Motion>", middle_click_drag)

    globals.sidebar.frame.bind("<B1-Motion>", left_click_drag_sidebar)
