from .. import state
from ..ui.point import Point
from ..ui.intersect import Intersect
from ..ui.midpoint_or_center import Midpoint_or_center
from ..ui.pen import Pen
from ..ui.line import Line
from ..ui.ray import Ray
from ..ui.segment import Segment
from ..ui.free_hand import FreeHand
from ..ui.segment_with_lenght import Segment_with_length
from ..ui.polyline import Polyline
from ..tools.utils import (
    get_lower_label,
    number_to_ascii,
    center,
    set_cursor,
    snap,
    get_label,
    screen_to_world,
    deselect_all,
    find_point_at_position,
    find_line_at_position,
    find_translation,
    snap_to_line,
    find_polyline_at_position,
    find_translation_polyline,
    snap_to_polyline,
)
from tkinter import CURRENT, simpledialog

from py_geogebra.ui import polyline


def pressing(root, canvas, sidebar, objects, axes):
    def left_click_pressed(e):
        if state.selected_tool == "arrow":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            state.drag_target = None

            point_obj = find_point_at_position(objects, e, canvas)
            if point_obj:
                point_obj.update()
                if state.selected_point and state.selected_point != point_obj:
                    state.selected_point.deselect()
                point_obj.select()
                state.selected_point = point_obj
                state.drag_target = point_obj
            else:
                deselect_all(objects)

            if not point_obj:
                line_obj = find_line_at_position(objects, e, canvas)
                if line_obj:
                    line_obj.pos_x, line_obj.pos_y = screen_to_world(canvas, objects, e)
                    line_obj.update()
                    if hasattr(line_obj, "select"):
                        line_obj.select()
                        state.selected_point = line_obj
                    state.drag_target = line_obj
                else:
                    polyline_obj = find_polyline_at_position(objects, e, canvas)
                    if polyline_obj:
                        polyline_obj.pos_x, polyline_obj.pos_y = screen_to_world(
                            canvas, objects, e
                        )
                        polyline_obj.update()
                        state.selected_point = polyline_obj
                        polyline_obj.select()
                        state.drag_target = polyline_obj

        elif state.selected_tool == "point":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y

            world_x, world_y = screen_to_world(canvas, objects, e)

            l = find_line_at_position(objects, e, canvas, r=2)

            label = get_label(state)
            p = Point(
                root,
                canvas,
                label=label,
                unit_size=axes.unit_size,
                pos_x=world_x,
                pos_y=world_y,
            )

            if l is not None:
                find_translation(p, l)
                l.points.append(p)
                snap_to_line(p, l)
                p.color = "#349AFF"
                l.update()

            polyline = find_polyline_at_position(objects, e, canvas, r=2)
            if polyline is not None:
                find_translation_polyline(p, polyline)
                polyline.points.append(p)
                snap_to_polyline(p, polyline)
                p.color = "#349AFF"
                polyline.update()

            objects.register(p)
            sidebar.items.append(p)
            sidebar.update()

        elif state.selected_tool == "intersect":
            l = find_line_at_position(objects, e, canvas, r=2)
            if l is None:
                state.selected_intersect.line_1.deselect()
                state.selected_intersect = None
                return
            else:
                if state.selected_intersect:
                    if state.selected_intersect.line_1 == l:
                        return
                    if not state.selected_intersect.line_2:
                        state.selected_intersect.line_2 = l
                        state.selected_intersect.line_1.deselect()
                        state.selected_intersect.update()
                        state.selected_intersect = None
                else:
                    label = get_label(state)
                    world_x, world_y = screen_to_world(canvas, objects, e)
                    i = Intersect(
                        root,
                        canvas,
                        label=label,
                        unit_size=axes.unit_size,
                        objects=objects,
                    )
                    i.line_1 = l
                    i.line_1.select()
                    objects.register(i)
                    i.update()
                    state.selected_intersect = i

        elif state.selected_tool == "pen":
            cx, cy = state.center
            world_x = (e.x - cx) / (objects.unit_size * objects.scale)
            world_y = (cy - e.y) / (objects.unit_size * objects.scale)

            state.current_pen = Pen(root, canvas, objects.unit_size)
            state.current_pen.add_point(world_x, world_y)
            objects.register(state.current_pen)

        elif state.selected_tool == "freehand":
            cx, cy = state.center
            world_x = (e.x - cx) / (objects.unit_size * objects.scale)
            world_y = (cy - e.y) / (objects.unit_size * objects.scale)

            state.current_pen = FreeHand(root, canvas, objects.unit_size)
            state.current_pen.add_point(world_x, world_y)
            objects.register(state.current_pen)

        elif state.selected_tool == "line":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(canvas, objects, e)
            p = find_point_at_position(objects, e, canvas)
            if p == None:
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
            if len(state.points_for_obj) < 2:
                line = Line(
                    root, canvas, unit_size=axes.unit_size, point_1=p, objects=objects
                )
                lower_label = get_lower_label(state)
                line.lower_label = lower_label
                objects.register(line)
                state.points_for_obj.append(p)
                state.points_for_obj.append(line)

            else:
                state.points_for_obj[1].point_2 = p
                state.points_for_obj[1].update()
                state.points_for_obj = []

        elif state.selected_tool == "segment":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(canvas, objects, e)
            p = find_point_at_position(objects, e, canvas)
            if p == None:
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
            if len(state.points_for_obj) < 2:
                lower_label = get_lower_label(state)
                segment = Segment(
                    root,
                    canvas,
                    unit_size=axes.unit_size,
                    point_1=p,
                    objects=objects,
                    lower_label=lower_label,
                )
                objects.register(segment)
                state.points_for_obj.append(p)
                state.points_for_obj.append(segment)

            else:
                state.points_for_obj[1].point_2 = p
                state.points_for_obj[1].update()
                sidebar.items.append(state.points_for_obj[1])
                sidebar.update()
                state.points_for_obj = []

        elif state.selected_tool == "ray":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(canvas, objects, e)
            p = find_point_at_position(objects, e, canvas)
            if p == None:
                label = get_label(state)
                p = Point(
                    root,
                    canvas,
                    label=label,
                    unit_size=axes.unit_size,
                    pos_x=world_x,
                    pos_y=world_y,
                )
                sidebar.items.append(p)
                sidebar.update()
                objects.register(p)
            if len(state.points_for_obj) < 2:
                ray = Ray(
                    root, canvas, unit_size=axes.unit_size, point_1=p, objects=objects
                )
                lower_label = get_lower_label(state)
                ray.lower_label = lower_label
                objects.register(ray)
                state.points_for_obj.append(p)
                state.points_for_obj.append(ray)

            else:
                state.points_for_obj[1].point_2 = p
                state.points_for_obj[1].update()
                state.points_for_obj = []

        elif state.selected_tool == "polyline":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(canvas, objects, e)
            if state.current_polyline is None:
                polyline = Polyline(root, canvas, axes.unit_size, objects)
                state.current_polyline = polyline
                objects.register(polyline)
            p = find_point_at_position(objects, e, canvas)
            if p == None:
                label = get_label(state)
                p = Point(
                    root,
                    canvas,
                    label=label,
                    unit_size=axes.unit_size,
                    pos_x=world_x,
                    pos_y=world_y,
                )

                state.current_polyline.line_points.append(p)
                objects.register(p)
            elif (
                len(state.current_polyline.line_points) > 2
                and state.current_polyline.line_points[0] == p
            ):
                state.current_polyline.last_not_set = False
                state.current_polyline.lower_label = get_lower_label(state)
                state.current_polyline.update(e)
                sidebar.items.append(state.current_polyline)
                sidebar.update()
                state.current_polyline = None
            else:
                if p in state.current_polyline.line_points:
                    state.current_polyline.line_points.remove(p)
                else:
                    state.current_polyline.line_points.append(p)
                state.current_polyline.update(e)

        elif state.selected_tool == "segment_with_length":
            world_x, world_y = screen_to_world(canvas, objects, e)
            p = find_point_at_position(objects, e, canvas)
            if p == None:
                label = get_label(state)
                p = Point(
                    root,
                    canvas,
                    label=label,
                    unit_size=axes.unit_size,
                    pos_x=world_x,
                    pos_y=world_y,
                )
                sidebar.items.append(p)
                objects.register(p)

            length = (
                simpledialog.askfloat(
                    "Dĺžka úsečky",
                    "Zadajte dĺžku úsečky (kladné číslo):",
                    minvalue=0,
                )
            ) * objects.unit_size
            new_x = e.x + length
            cx, cy = center(canvas, objects)
            world_x = (new_x - cx) / (objects.unit_size * objects.scale)

            label = get_label(state)
            p2 = Point(
                root,
                canvas,
                label=label,
                unit_size=axes.unit_size,
                pos_x=world_x,
                pos_y=world_y,
            )
            sidebar.items.append(p2)
            sidebar.update()
            objects.register(p2)

            swl = Segment_with_length(
                root,
                canvas,
                unit_size=axes.unit_size,
                point_1=p,
                point_2=p2,
                length=length,
                angle=0,
                objects=objects,
            )
            objects.register(swl)
            objects.refresh()

        elif state.selected_tool == "midpoint_or_center":
            world_x, world_y = screen_to_world(canvas, objects, e)
            p = find_point_at_position(objects, e, canvas)
            if p == None:
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
            p.select()
            state.points_for_obj.append(p)
            if len(state.points_for_obj) == 2:
                label = get_label(state)
                midpoint = Midpoint_or_center(
                    root,
                    canvas,
                    label=label,
                    unit_size=axes.unit_size,
                    point_1=state.points_for_obj[0],
                    point_2=state.points_for_obj[1],
                    objects=objects,
                )

                objects.register(midpoint)
                state.points_for_obj = []

    def middle_click_pressed(e):
        state.start_pos["x"] = e.x
        state.start_pos["y"] = e.y

    def right_click_released(e):
        if state.selected_tool == "pen":
            set_cursor(canvas, "crosshair")

    def left_click_released(e):
        if state.selected_tool == "freehand":
            objects.unregister(state.current_pen)
            canvas.delete(state.current_pen.tag)
        elif state.selected_tool == "arrow":
            state.drag_target = None

        objects.refresh()

    def left_click_pressed_sidebar(e):
        if abs(e.x - sidebar.frame.winfo_width()) <= 20:
            state.sidebar_resizing = True
            state.start_pos["x"] = e.x
            set_cursor(sidebar.frame, "sb_h_double_arrow")

    def left_click_released_sidebar(e):
        state.sidebar_resizing = False
        set_cursor(sidebar.frame, "")

    canvas.bind("<Button-1>", left_click_pressed)
    canvas.bind("<Button-3>", middle_click_pressed)
    canvas.bind("<ButtonRelease-2>", right_click_released)
    canvas.bind("<ButtonRelease-1>", left_click_released)
    sidebar.frame.bind("<Button-1>", left_click_pressed_sidebar)
    sidebar.frame.bind("<ButtonRelease-1>", left_click_released_sidebar)
