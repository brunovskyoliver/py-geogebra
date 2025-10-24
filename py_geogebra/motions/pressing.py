from .. import state
from ..ui.point import Point
from ..ui.blank_point import Blank_point
from ..ui.intersect import Create_Intersect
from ..ui.midpoint_or_center import Midpoint_or_center
from ..ui.pen import Pen
from ..ui.line import Line
from ..ui.perpendicular_line import Perpendicular_line
from ..ui.ray import Ray
from ..ui.segment import Segment
from ..ui.vector import Vector
from ..ui.vector_from_point import Vector_from_point
from ..ui.free_hand import FreeHand
from ..ui.segment_with_lenght import Segment_with_length
from ..ui.polyline import Polyline
from ..tools.utils import (
    delete_object,
    get_lower_label,
    center,
    set_cursor,
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
    detach_point,
    attach_point,
)
from tkinter import simpledialog
from .. import globals


def pressing(root):
    def left_click_pressed(e):
        if state.selected_tool == "arrow":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            state.drag_target = None

            point_obj = find_point_at_position(e)
            if point_obj:
                point_obj.update()
                if state.selected_point and state.selected_point != point_obj:
                    state.selected_point.deselect()
                point_obj.select()
                state.selected_point = point_obj
                state.drag_target = point_obj
            else:
                deselect_all()

            if not point_obj:
                line_obj = find_line_at_position(e)
                if line_obj:
                    line_obj.pos_x, line_obj.pos_y = screen_to_world(e)
                    line_obj.update()
                    if hasattr(line_obj, "select"):
                        line_obj.select()
                        state.selected_point = line_obj
                    state.drag_target = line_obj
                else:
                    polyline_obj = find_polyline_at_position(e)
                    if polyline_obj:
                        polyline_obj.pos_x, polyline_obj.pos_y = screen_to_world(e)
                        polyline_obj.update()
                        state.selected_point = polyline_obj
                        polyline_obj.select()
                        state.drag_target = polyline_obj

        elif state.selected_tool == "point":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y

            world_x, world_y = screen_to_world(e)

            l = find_line_at_position(e, r=2)
            polyline = find_polyline_at_position(e, r=2)

            label = get_label(state)
            p = Point(
                root,
                e,
                label=label,
                unit_size=globals.axes.unit_size,
                pos_x=world_x,
                pos_y=world_y,
            )
            

            if l is not None:
                p.is_detachable = True
                p.is_atachable = False
                p.parent_line = l
                find_translation(p, l)
                l.points.append(p)
                snap_to_line(p, l)
                p.color = "#349AFF"
                l.update()
            elif polyline is not None:
                p.is_detachable = True
                p.is_atachable = False
                p.parent_line = polyline
                find_translation_polyline(p, polyline)
                polyline.points.append(p)
                snap_to_polyline(p, polyline)
                p.color = "#349AFF"
                polyline.update()


            globals.objects.register(p)

        elif state.selected_tool == "attach_detach_point":
            point_obj = find_point_at_position(e)
            
            if point_obj and point_obj.is_detachable and point_obj.parent_line:
                detach_point(point_obj, point_obj.parent_line)
                point_obj.parent_line.points.remove(point_obj)
                point_obj.parent_line = None
                point_obj.is_detachable = False
                point_obj .is_atachable = True
            elif not point_obj and not state.line_to_attach:
                l = find_line_at_position(e, r=2)
                if l is None:
                    l = find_polyline_at_position(e, r=2)
                    if l is None:
                        return
                l.select()
                state.line_to_attach = l
                
            elif not state.point_to_attach and point_obj:
                state.point_to_attach = point_obj
                point_obj.select()
            
            else:
                if state.point_to_attach:
                    state.point_to_attach.deselect()
                if state.line_to_attach:
                    state.line_to_attach.deselect()
                state.point_to_attach = None
                state.line_to_attach = None

                
            
            
            if state.line_to_attach and state.point_to_attach:
                attach_point(state.point_to_attach, state.line_to_attach)
                state.point_to_attach.is_atachable = False
                state.point_to_attach.is_detachable = True
                state.point_to_attach.deselect()
                state.line_to_attach.deselect()
                state.line_to_attach.points.append(state.point_to_attach)
                state.point_to_attach.parent_line = state.line_to_attach
                state.point_to_attach = None
                state.line_to_attach = None
                

                
                
        
        elif state.selected_tool == "intersect":
            l = find_line_at_position(e, r=2)
            if l is None:
                l = find_polyline_at_position(e, r=2)
            if l is None and state.selected_intersect_line_1:
                state.selected_intersect_line_1.deselect()
                state.selected_intersect_line_1 = None
                return
            elif l is None:
                return
            else:
                if state.selected_intersect_line_1:
                    if state.selected_intersect_line_1 == l:
                        return
                    else:
                        i = Create_Intersect(
                        state.selected_intersect_line_1,
                        l,
                        root,
                        unit_size=globals.axes.unit_size,
                        )
                        state.selected_intersect_line_1 = None
                else:
                    world_x, world_y = screen_to_world(e)
                    
                    state.selected_intersect_line_1 = l
                    l.select()

        elif state.selected_tool == "pen":
            cx, cy = state.center
            world_x = (e.x - cx) / (globals.objects.unit_size * globals.objects.scale)
            world_y = (cy - e.y) / (globals.objects.unit_size * globals.objects.scale)

            state.current_pen = Pen(root, globals.objects.unit_size)
            state.current_pen.add_point(world_x, world_y)
            globals.objects.register(state.current_pen)

        elif state.selected_tool == "freehand":
            cx, cy = state.center
            world_x = (e.x - cx) / (globals.objects.unit_size * globals.objects.scale)
            world_y = (cy - e.y) / (globals.objects.unit_size * globals.objects.scale)

            state.current_pen = FreeHand(root, globals.objects.unit_size)
            state.current_pen.add_point(world_x, world_y)
            globals.objects.register(state.current_pen)

        elif state.selected_tool == "line":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(e)
            p = find_point_at_position(e)
            if p == None:
                label = get_label(state)
                p = Point(
                    root,
                    e,
                    label=label,
                    unit_size=globals.axes.unit_size,
                    pos_x=world_x,
                    pos_y=world_y,
                )
                globals.objects.register(p)
            if len(state.points_for_obj) < 2:
                line = Line(
                    root,
                    unit_size=globals.axes.unit_size,
                    point_1=p,
                )
                lower_label = get_lower_label(state)
                line.lower_label = lower_label
                globals.objects.register(line)
                state.points_for_obj.append(p)
                state.points_for_obj.append(line)

            else:
                state.points_for_obj[1].point_2 = p
                state.points_for_obj[1].update()
                globals.sidebar.items.append(state.points_for_obj[1])
                globals.sidebar.update()
                state.points_for_obj = []

        elif state.selected_tool == "segment":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(e)
            p = find_point_at_position(e)
            if p == None:
                label = get_label(state)
                p = Point(
                    root,
                    e,
                    label=label,
                    unit_size=globals.axes.unit_size,
                    pos_x=world_x,
                    pos_y=world_y,
                )
                globals.objects.register(p)
            if len(state.points_for_obj) < 2:
                lower_label = get_lower_label(state)
                segment = Segment(
                    root,
                    unit_size=globals.axes.unit_size,
                    point_1=p,
                    lower_label=lower_label,
                )
                globals.objects.register(segment)
                segment.lower_label = lower_label
                state.points_for_obj.append(p)
                state.points_for_obj.append(segment)

            else:
                state.points_for_obj[1].point_2 = p
                state.points_for_obj[1].update()
                globals.sidebar.items.append(state.points_for_obj[1])
                globals.sidebar.update()
                state.points_for_obj = []

        elif state.selected_tool == "ray":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(e)
            p = find_point_at_position(e)
            if p == None:
                label = get_label(state)
                p = Point(
                    root,
                    e,
                    label=label,
                    unit_size=globals.axes.unit_size,
                    pos_x=world_x,
                    pos_y=world_y,
                )
                globals.objects.register(p)
            if len(state.points_for_obj) < 2:
                ray = Ray(
                    root,
                    unit_size=globals.axes.unit_size,
                    point_1=p,
                )
                lower_label = get_lower_label(state)
                ray.lower_label = lower_label
                globals.objects.register(ray)
                state.points_for_obj.append(p)
                state.points_for_obj.append(ray)

            else:
                state.points_for_obj[1].point_2 = p
                state.points_for_obj[1].update()
                globals.sidebar.items.append(state.points_for_obj[1])
                globals.sidebar.update()

                state.points_for_obj = []

        elif state.selected_tool == "polyline":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(e)
            if state.current_polyline is None:
                polyline = Polyline(root, globals.axes.unit_size)
                state.current_polyline = polyline
                globals.objects.register(polyline)
            p = find_point_at_position(e)
            if p == None:
                label = get_label(state)
                p = Point(
                    root,
                    e,
                    label=label,
                    unit_size=globals.axes.unit_size,
                    pos_x=world_x,
                    pos_y=world_y,
                )

                state.current_polyline.line_points.append(p)
                globals.objects.register(p)
            elif (
                len(state.current_polyline.line_points) > 2
                and state.current_polyline.line_points[0] == p
            ):
                state.current_polyline.last_not_set = False
                state.current_polyline.lower_label = get_lower_label(state)
                state.current_polyline.update(e)
                globals.sidebar.items.append(state.current_polyline)
                globals.sidebar.update()
                state.current_polyline = None
            else:
                if p in state.current_polyline.line_points:
                    state.current_polyline.line_points.remove(p)
                else:
                    state.current_polyline.line_points.append(p)
                state.current_polyline.update(e)

        elif state.selected_tool == "segment_with_length":
            world_x, world_y = screen_to_world(e)
            p = find_point_at_position(e)
            if p == None:
                label = get_label(state)
                p = Point(
                    root,
                    e,
                    label=label,
                    unit_size=globals.axes.unit_size,
                    pos_x=world_x,
                    pos_y=world_y,
                )
                globals.objects.register(p)
            length = simpledialog.askfloat(
                "Dĺžka úsečky",
                "Zadajte dĺžku úsečky (kladné číslo):",
                minvalue=0,
            )
            if length is None:
                delete_object(p, state)
                globals.sidebar.items.remove(p)
                globals.sidebar.update()
                return

            length *= globals.objects.unit_size
            new_x = e.x + length
            cx, cy = center()
            world_x = (new_x - cx) / (globals.objects.unit_size * globals.objects.scale)

            label = get_label(state)
            p2 = Point(
                root,
                e=None,
                label=label,
                unit_size=globals.axes.unit_size,
                pos_x=world_x,
                pos_y=world_y,
            )
            globals.objects.register(p2)

            swl = Segment_with_length(
                root,
                unit_size=globals.axes.unit_size,
                point_1=p,
                point_2=p2,
                length=length,
                angle=0,
            )
            lower_label = get_lower_label(state)
            swl.lower_label = lower_label

            globals.objects.register(swl)
            globals.objects.refresh()

        elif state.selected_tool == "midpoint_or_center":
            world_x, world_y = screen_to_world(e)
            p = find_point_at_position(e)
            if p == None:
                label = get_label(state)
                p = Point(
                    root,
                    e,
                    label=label,
                    unit_size=globals.axes.unit_size,
                    pos_x=world_x,
                    pos_y=world_y,
                )
                globals.objects.register(p)
            p.select()
            state.points_for_obj.append(p)
            if len(state.points_for_obj) == 2:
                label = get_label(state)
                midpoint = Midpoint_or_center(
                    root,
                    label=label,
                    unit_size=globals.axes.unit_size,
                    point_1=state.points_for_obj[0],
                    point_2=state.points_for_obj[1],
                )

                globals.objects.register(midpoint)
                state.points_for_obj = []

        elif state.selected_tool == "vector":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(e)
            p = find_point_at_position(e)
            if p == None:
                label = get_label(state)
                p = Point(
                    root,
                    e,
                    label=label,
                    unit_size=globals.axes.unit_size,
                    pos_x=world_x,
                    pos_y=world_y,
                )
                globals.objects.register(p)
            if len(state.points_for_obj) < 2:
                lower_label = get_lower_label(state)
                vector = Vector(
                    root,
                    unit_size=globals.axes.unit_size,
                    point_1=p,
                    lower_label=lower_label,
                )
                globals.objects.register(vector)
                state.points_for_obj.append(p)
                state.points_for_obj.append(vector)

            else:
                state.points_for_obj[1].point_2 = p
                state.points_for_obj[1].update()
                globals.sidebar.items.append(state.points_for_obj[1])
                globals.sidebar.update()
                state.points_for_obj = []
        
        elif state.selected_tool == "vector_from_point":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(e)
            p = find_point_at_position(e)
            if p == None:
                l = find_line_at_position(e)
                if isinstance(l, Vector):
                    state.selected_vector = l
                    l.select()
            else:
                state.selected_vector_point = p
                p.select()
                
            if state.selected_vector_point and state.selected_vector:
                lower_label = get_lower_label(state)
                label = get_label(state)
                p = Point(
                    root,
                    e,
                    label=label,
                    unit_size=globals.axes.unit_size,
                    pos_x=state.selected_vector_point.pos_x + (state.selected_vector.point_2.pos_x - state.selected_vector.point_1.pos_x),
                    pos_y=state.selected_vector_point.pos_y + (state.selected_vector.point_2.pos_y - state.selected_vector.point_1.pos_y),
                )
                vector = Vector_from_point(
                    root,
                    unit_size=globals.axes.unit_size,
                    point_1=state.selected_vector_point,
                    lower_label=lower_label,
                )
                vector.parent_vector = state.selected_vector
                vector.point_2 = p
                globals.objects.register(vector)
                globals.objects.register(p)
                state.selected_vector.child_vectors_labels.append(lower_label)
                state.selected_vector.loaded_children = False
                state.selected_vector.deselect()
                state.selected_vector_point.deselect()
                state.selected_vector_point = None
                state.selected_vector = None
                   

        
        elif state.selected_tool == "perpendicular_line":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(e)
            p = find_point_at_position(e)
            if p is None:
                l = find_line_at_position(e)
                if l:
                    state.selected_perpendicular_line = l
                    l.select()
                else:
                    label = get_label(state)
                    p = Point(
                        root,
                        e,
                        label=label,
                        unit_size=globals.axes.unit_size,
                        pos_x=world_x,
                        pos_y=world_y,
                    )
                    p.select()
                    state.selected_perpendicular_point = p
                    globals.objects.register(p)
            else:
                state.selected_perpendicular_point = p
                p.select()
                globals.objects.register(p)
                
                
            if state.selected_perpendicular_line and state.selected_perpendicular_point:
                l = Perpendicular_line(
                    root,
                )
                lower_label = get_lower_label(state)
                l.lower_label = lower_label
                l.parent_vector = state.selected_perpendicular_line.vector
                l.point_1 = state.selected_perpendicular_point
                    
                globals.objects.register(l)
                state.selected_perpendicular_line.child_lines.append(l)
                state.selected_perpendicular_line.deselect()
                state.selected_perpendicular_point.deselect()
                state.selected_perpendicular_line = None
                state.selected_perpendicular_point = None
                
            
            


    def middle_click_pressed(e):
        state.start_pos["x"] = e.x
        state.start_pos["y"] = e.y

    def right_click_released(e):
        if state.selected_tool == "pen":
            set_cursor(globals.canvas, "crosshair")

    def left_click_released(e):
        if state.selected_tool == "freehand":
            globals.objects.unregister(state.current_pen)
            globals.canvas.delete(state.current_pen.tag)
        elif state.selected_tool == "arrow":
            state.drag_target = None

        globals.objects.refresh()

    def left_click_pressed_sidebar(e):
        if abs(e.x - globals.sidebar.frame.winfo_width()) <= 20:
            state.sidebar_resizing = True
            state.start_pos["x"] = e.x
            set_cursor(globals.sidebar.frame, "sb_h_double_arrow")

    def left_click_released_sidebar(e):
        state.sidebar_resizing = False
        set_cursor(globals.sidebar.frame, "")

    globals.canvas.bind("<Button-1>", left_click_pressed)
    globals.canvas.bind("<Button-3>", middle_click_pressed)
    globals.canvas.bind("<ButtonRelease-2>", right_click_released)
    globals.canvas.bind("<ButtonRelease-1>", left_click_released)
    globals.sidebar.frame.bind("<Button-1>", left_click_pressed_sidebar)
    globals.sidebar.frame.bind("<ButtonRelease-1>", left_click_released_sidebar)
