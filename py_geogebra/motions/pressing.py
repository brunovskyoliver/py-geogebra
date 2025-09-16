from .. import state
from ..ui.point import Point
from ..ui.midpoint_or_center import Midpoint_or_center
from ..ui.pen import Pen
from ..ui.line import Line
from ..ui.ray import Ray
from ..ui.segment import Segment
from ..ui.free_hand import FreeHand
from ..ui.segment_with_lenght import Segment_with_length
from ..tools.utils import (
    number_to_ascii,
    center,
    set_cursor,
    snap,
    get_label,
    screen_to_world,
)
from tkinter import simpledialog


def pressing(root, canvas, sidebar, objects, axes):
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
            sidebar.items.append(p)
            sidebar.update()

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
                line = Line(
                    root, canvas, unit_size=axes.unit_size, point_1=p, objects=objects
                )
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
                segment = Segment(
                    root, canvas, unit_size=axes.unit_size, point_1=p, objects=objects
                )
                objects.register(segment)
                state.points_for_obj.append(p)
                state.points_for_obj.append(segment)

            else:
                state.points_for_obj[1].point_2 = p
                state.points_for_obj[1].update()
                state.points_for_obj = []

        elif state.selected_tool == "ray":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(canvas, objects, e)
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
                objects.register(ray)
                state.points_for_obj.append(p)
                state.points_for_obj.append(ray)

            else:
                state.points_for_obj[1].point_2 = p
                state.points_for_obj[1].update()
                state.points_for_obj = []

        elif state.selected_tool == "segment_with_length":
            world_x, world_y = screen_to_world(canvas, objects, e)
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
            p.select()
            
            sidebar.update()
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
                    objects=objects
                    
                )

                objects.register(midpoint)
                sidebar.items.append(midpoint)
                sidebar.update()
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
