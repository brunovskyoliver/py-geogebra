from .. import state
from ..ui.point import Point
from ..ui.pen import Pen
from ..ui.line import Line
from ..tools.utils import (
    number_to_ascii,
    center,
    set_cursor,
    snap,
    get_label,
    screen_to_world,
)
import math


def pressing(root, canvas, objects, axes):
    def left_click_pressed(e):
        if state.selected_tool == "arrow":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            items = canvas.find_overlapping(e.x, e.y, e.x + 1, e.y + 1)
            point_obj = None
            for obj in objects._objects:
                if hasattr(obj, "tag") and any(
                    obj.tag in canvas.gettags(i) for i in items
                ):
                    if "point" in obj.tag:
                        point_obj = obj
                        break
            if point_obj:
                if state.selected_point and state.selected_point != point_obj:
                    state.selected_point.deselect()
                point_obj.select()
                state.selected_point = point_obj
            state.drag_target = point_obj

        elif state.selected_tool == "point":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y

            world_x, world_y = snap(canvas, objects, e, axes)

            label = get_label(state)
            p = Point(
                root,
                canvas,
                label=label,
                unit_size=axes.unit_size,
                pos_x=world_x,
                pos_y=world_y,
            )
            objects.register(p)
        elif state.selected_tool == "pen":
            cx, cy = center(canvas, objects)
            world_x = (e.x - cx) / (objects.unit_size * objects.scale)
            world_y = (cy - e.y) / (objects.unit_size * objects.scale)

            state.current_pen = Pen(root, canvas, objects.unit_size)
            state.current_pen.add_point(world_x, world_y)
            objects.register(state.current_pen)

        elif state.selected_tool == "freehand":
            cx, cy = center(canvas, objects)
            world_x = (e.x - cx) / (objects.unit_size * objects.scale)
            world_y = (cy - e.y) / (objects.unit_size * objects.scale)
            state.freehand_last_pos["x"] = world_x
            state.freehand_last_pos["y"] = world_y
            
        elif state.selected_tool == "line":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(canvas, objects, e)
            label = get_label(state)
            items = canvas.find_overlapping(e.x, e.y, e.x + 1, e.y + 1)
            p = None
            for obj in objects._objects:
                if hasattr(obj, "tag") and any(
                    obj.tag in canvas.gettags(i) for i in items
                ):
                    if "point" in obj.tag:
                        p = obj
                        break
            if p == None:
                p = Point(
                    root,
                    canvas,
                    label=label,
                    unit_size=axes.unit_size,
                    pos_x=world_x,
                    pos_y=world_y,
                )
                objects.register(p)
            if len(state.points_for_obj) < 2:
                line = Line(
                    root, canvas, unit_size=axes.unit_size, point_1=p, objects=objects
                )
                objects.register(line)
                state.points_for_obj.append(p)
                state.points_for_obj.append(line)

            else:
                state.points_for_obj[1].point_2 = p
                state.points_for_obj = []

    def middle_click_pressed(e):
        state.start_pos["x"] = e.x
        state.start_pos["y"] = e.y

    def right_click_released(e):
        if state.selected_tool == "pen":
            set_cursor(canvas, "crosshair")

    def left_click_released(e):
        if state.selected_tool == "freehand":
            canvas.delete("freehand")
        elif state.selected_tool == "arrow":
            state.drag_target = None

    canvas.bind("<Button-1>", left_click_pressed)
    canvas.bind("<Button-3>", middle_click_pressed)
    canvas.bind("<ButtonRelease-2>", right_click_released)
    canvas.bind("<ButtonRelease-1>", left_click_released)
