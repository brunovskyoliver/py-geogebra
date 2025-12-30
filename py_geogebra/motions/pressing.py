import math
from tkinter import simpledialog
from tkinter import Tk

from py_geogebra.ui.compass import Compass
from py_geogebra.ui.semicircle import Semicircle

from .. import globals, state
from ..tools.utils import (
    attach_point,
    center,
    delete_object,
    deselect_all,
    detach_point,
    find_circle_at_position,
    find_line_at_position,
    find_point_at_position,
    find_polyline_at_position,
    find_translation,
    find_translation_circle,
    find_translation_polyline,
    get_label,
    get_lower_label,
    screen_to_world,
    set_cursor,
    snap_to_circle,
    snap_to_line,
    snap_to_polyline,
)
from ..ui.angle_bisector import Angle_bisector
from ..ui.best_fit_line import Best_fit_line
from ..ui.circle_center_point import Circle_center_point
from ..ui.circle_center_radius import Circle_center_radius
from ..ui.free_hand import FreeHand
from ..ui.intersect import Create_Intersect
from ..ui.line import Line
from ..ui.midpoint_or_center import Midpoint_or_center
from ..ui.parallel_line import Parallel_line
from ..ui.pen import Pen
from ..ui.perpendicular_bisector import Perpendicular_bisector
from ..ui.perpendicular_line import Perpendicular_line
from ..ui.point import Point
from ..ui.polygon import Polygon
from ..ui.polyline import Polyline
from ..ui.ray import Ray
from ..ui.regular_polygon import Regular_polygon
from ..ui.segment import Segment
from ..ui.segment_with_lenght import Segment_with_length
from ..ui.vector import Vector
from ..ui.vector_from_point import Vector_from_point
from ..ui.circle_3_points import Circle_3_points


def pressing(root:Tk) -> None:
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
                globals.logger.info(f"Selected {point_obj.tag} at x:{point_obj.pos_x} y:{point_obj.pos_y}")
            else:
                deselect_all()

            if not point_obj:
                line_obj = find_line_at_position(e)
                polyline_obj = find_polyline_at_position(e)
                circle_obj = find_circle_at_position(e, r=2)
                if line_obj:
                    line_obj.pos_x, line_obj.pos_y = screen_to_world(e)
                    line_obj.update()
                    if hasattr(line_obj, "select"):
                        line_obj.select()
                        state.selected_point = line_obj
                        globals.logger.info(f"Selected {line_obj.tag} at x:{line_obj.pos_x} y:{line_obj.pos_y}")
                    state.drag_target = line_obj
                elif polyline_obj:
                    polyline_obj.pos_x, polyline_obj.pos_y = screen_to_world(e)
                    polyline_obj.update()
                    state.selected_point = polyline_obj
                    polyline_obj.select()
                    globals.logger.info(f"Selected {polyline_obj.tag} at x:{polyline_obj.pos_x} y:{polyline_obj.pos_y}")
                    state.drag_target = polyline_obj
                elif circle_obj:
                    circle_obj.pos_x, circle_obj.pos_y = screen_to_world(e)
                    circle_obj.update()
                    state.drag_target = circle_obj
                    circle_obj.select()
                    globals.logger.info(f"Selected {circle_obj.tag} at x:{circle_obj.pos_x} y:{circle_obj.pos_y}")

        elif state.selected_tool == "point":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y

            world_x, world_y = screen_to_world(e)

            pb = find_line_at_position(e, r=2)
            polyline = find_polyline_at_position(e, r=2)
            circle = find_circle_at_position(e, r=2)

            label = get_label(state)
            p = Point(
                root,
                e,
                label=label,
                unit_size=globals.axes.unit_size,
                pos_x=world_x,
                pos_y=world_y,
            )

            if pb is not None:
                p.is_detachable = True
                p.is_atachable = False
                p.parent_line = pb
                find_translation(p, pb)
                pb.points.append(p)
                snap_to_line(p, pb)
                p.color = "#349AFF"
                pb.update()
            elif polyline is not None:
                p.is_detachable = True
                p.is_atachable = False
                p.parent_line = polyline
                find_translation_polyline(p, polyline)
                polyline.points.append(p)
                snap_to_polyline(p, polyline)
                p.color = "#349AFF"
                polyline.update()
            elif circle is not None:
                p.is_detachable = True
                p.is_atachable = False
                p.parent_line = circle
                find_translation_circle(p,circle)
                circle.points.append(p)
                snap_to_circle(p, circle)
                p.color = "#349AFF"
                circle.update()




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
                pb = find_line_at_position(e, r=2)
                if pb is None:
                    pb = find_polyline_at_position(e, r=2)
                    if pb is None:
                        pb = find_circle_at_position(e, r=2)
                        if pb is None:
                            return
                pb.select()
                state.line_to_attach = pb

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
            pbs = find_line_at_position(e, r=2, num_lines=2)
            if not pbs:
                pb = find_polyline_at_position(e, r=2)
                if pb is None:
                    pb = find_circle_at_position(e, r=2)

            if len(pbs) > 0:
                for pb in pbs:
                    if pb is None and state.selected_intersect_line_1:
                        state.selected_intersect_line_1.deselect()
                        state.selected_intersect_line_1 = None
                        return
                    elif pb is None:
                        return
                    else:
                        if state.selected_intersect_line_1:
                            if state.selected_intersect_line_1 == pb:
                                return
                            else:
                                i = Create_Intersect(
                                state.selected_intersect_line_1,
                                pb,
                                root,
                                unit_size=globals.axes.unit_size,
                                )
                                state.selected_intersect_line_1 = None
                        else:
                            world_x, world_y = screen_to_world(e)

                            state.selected_intersect_line_1 = pb
                            pb.select()
            else:
                if pb is None and state.selected_intersect_line_1:
                    state.selected_intersect_line_1.deselect()
                    state.selected_intersect_line_1 = None
                    return
                elif pb is None:
                    return
                else:
                    if state.selected_intersect_line_1:
                        if state.selected_intersect_line_1 == pb:
                            return
                        else:
                            i = Create_Intersect(
                            state.selected_intersect_line_1,
                            pb,
                            root,
                            unit_size=globals.axes.unit_size,
                            )
                            state.selected_intersect_line_1 = None
                    else:
                        world_x, world_y = screen_to_world(e)

                        state.selected_intersect_line_1 = pb
                        pb.select()

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
                c = Line(
                    root,
                    unit_size=globals.axes.unit_size,
                    point_1=p,
                )
                lower_label = get_lower_label(state)
                c.lower_label = lower_label
                globals.objects.register(c)
                state.points_for_obj.append(p)
                state.points_for_obj.append(c)

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
                pb = find_line_at_position(e)
                if isinstance(pb, Vector):
                    state.selected_vector = pb
                    pb.select()
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
                pb = find_line_at_position(e)
                if pb:
                    state.selected_perpendicular_line = pb
                    pb.select()
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
                pb = Perpendicular_line(
                    root,
                    parent_line=state.selected_perpendicular_line
                )
                lower_label = get_lower_label(state)
                pb.lower_label = lower_label
                pb.parent_vector = state.selected_perpendicular_line.vector
                pb.point_1 = state.selected_perpendicular_point

                globals.objects.register(pb)
                globals.sidebar.items.append(pb)
                globals.sidebar.update()
                state.selected_perpendicular_line.child_lines.append(pb)
                state.selected_perpendicular_line.deselect()
                state.selected_perpendicular_point.deselect()
                state.selected_perpendicular_line = None
                state.selected_perpendicular_point = None

        elif state.selected_tool == "parallel_line":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(e)
            p = find_point_at_position(e)
            if p is None:
                pb = find_line_at_position(e)
                if pb:
                    state.selected_perpendicular_line = pb
                    pb.select()
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
                pb = Parallel_line(
                    root,
                    parent_line=state.selected_perpendicular_line
                )
                lower_label = get_lower_label(state)
                pb.lower_label = lower_label
                pb.parent_vector = state.selected_perpendicular_line.vector
                pb.point_1 = state.selected_perpendicular_point

                globals.objects.register(pb)
                globals.sidebar.items.append(pb)
                globals.sidebar.update()
                state.selected_perpendicular_line.child_lines.append(pb)
                state.selected_perpendicular_line.deselect()
                state.selected_perpendicular_point.deselect()
                state.selected_perpendicular_line = None
                state.selected_perpendicular_point = None

        elif state.selected_tool == "perpendicular_bisector":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(e)
            p = find_point_at_position(e)
            if p is None:
                return
            p.select()
            state.points_for_obj.append(p)

            if len(state.points_for_obj) < 2:
                pb = Perpendicular_bisector(
                    root,
                    perp_point_1=p
                )
                lower_label = get_lower_label(state)
                pb.lower_label = lower_label
                state.points_for_obj.append(pb)
                globals.objects.register(pb)
                pb.update()
            else:
                state.points_for_obj[1].perp_point_2 = p
                state.points_for_obj[1].update()
                deselect_all()
                globals.sidebar.items.append(state.points_for_obj[1])
                globals.sidebar.update()
                state.points_for_obj = []

        elif state.selected_tool == "angle_bisector":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(e)
            p = find_point_at_position(e)
            if p is None:
                return
            p.select()
            state.selected_angle_bisector_points.append(p)

            if len(state.selected_angle_bisector_points) == 3:
                ag = Angle_bisector(
                    root
                )
                lower_label = get_lower_label(state)
                ag.lower_label = lower_label
                ag.point_1 = state.selected_angle_bisector_points[1]
                ag.angle_point_1 = state.selected_angle_bisector_points[0]
                ag.angle_point_2 = state.selected_angle_bisector_points[2]
                globals.objects.register(ag)
                globals.sidebar.items.append(ag)
                globals.sidebar.update()
                for p in state.selected_angle_bisector_points:
                    p.deselect()

                state.selected_angle_bisector_points.clear()

        elif state.selected_tool == "best_fit_line":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(e)
            p = find_point_at_position(e)
            if not p:
                for obj in state.points_for_obj:
                    obj.deselect()
                state.points_for_obj = []
                state.best_fit_line = None
                return
            state.points_for_obj.append(p)
            p.select()
            if not state.best_fit_line and len(state.points_for_obj) >= 2:
                state.best_fit_line = Best_fit_line(
                    root,
                )
                lower_label = get_lower_label(state)
                state.best_fit_line.lower_label = lower_label
                globals.objects.register(state.best_fit_line)
            if state.best_fit_line:
                state.best_fit_line.fit_points = state.points_for_obj[:]

        elif state.selected_tool == "polygon":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(e)
            if state.current_polygon is None:
                polygon = Polygon(root, globals.axes.unit_size)
                state.current_polygon = polygon
                globals.objects.register(polygon)
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

                state.current_polygon.line_points.append(p)
                globals.objects.register(p)
                state.current_polygon.handle_segments()
            elif (
                len(state.current_polygon.line_points) > 2
                and state.current_polygon.line_points[0] == p
            ):
                state.current_polygon.last_not_set = False
                state.current_polygon.lower_label = get_lower_label(state)
                state.current_polygon.handle_segments()
                state.current_polygon.update(e)
                globals.sidebar.items.append(state.current_polygon)
                globals.sidebar.update()
                state.current_polygon = None
            else:
                state.current_polygon.line_points.append(p)
                state.current_polygon.handle_segments()
                state.current_polygon.update(e)

            p.select()

        elif state.selected_tool == "regular_polygon":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(e)

            if not state.current_polygon:
                polygon = Regular_polygon(root, globals.axes.unit_size)
                state.current_polygon = polygon
                globals.objects.register(polygon)


            p = find_point_at_position(e)
            if not p:
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
            state.current_polygon.line_points.append(p)

            if state.current_polygon and len(state.current_polygon.line_points) == 2:
                num_points = simpledialog.askinteger(
                "pocet stran",
                "pocet stran",
                minvalue=3,
                )
                state.current_polygon.num_points = num_points
                angle = (num_points*180 - 360) / num_points
                rad_angle = math.radians(angle)
                angle_matrix = [[math.cos(rad_angle), -math.sin(rad_angle)],
                                [math.sin(rad_angle), math.cos(rad_angle)]]
                state.current_polygon.matrix = angle_matrix
                for i in range(1, num_points-1):
                    dist_x = (state.current_polygon.line_points[i-1].pos_x - state.current_polygon.line_points[i].pos_x)
                    dist_y = (state.current_polygon.line_points[i-1].pos_y - state.current_polygon.line_points[i].pos_y)
                    pos_x = state.current_polygon.line_points[i].pos_x + (dist_x * angle_matrix[0][0] + dist_y * angle_matrix[1][0])
                    pos_y = state.current_polygon.line_points[i].pos_y + (dist_x * angle_matrix[0][1] + dist_y * angle_matrix[1][1])
                    label = get_label(state)
                    p = Point(
                        root,
                        e,
                        label=label,
                        unit_size=globals.axes.unit_size,
                        pos_x=pos_x,
                        pos_y=pos_y,
                        color="Gray"
                    )
                    globals.objects.register(p)
                    state.current_polygon.line_points.append(p)

                for p in state.current_polygon.line_points:
                    p.deselect()
                state.current_polygon.last_not_set = False
                state.current_polygon.lower_label = get_lower_label(state)
                state.current_polygon.handle_segments()
                state.current_polygon.update()
                globals.sidebar.items.append(state.current_polygon)
                globals.sidebar.update()
                state.current_polygon = None
                state.points_for_obj = []

        elif state.selected_tool == "circle_center_point":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(e)
            p = find_point_at_position(e)
            if p == None:
                label = get_label(state)
                p = Point(
                    root,
                    e=None,
                    label=label,
                    unit_size=globals.axes.unit_size,
                    pos_x=world_x,
                    pos_y=world_y,
                )
                globals.objects.register(p)
            if len(state.points_for_obj) < 2:
                c = Circle_center_point(
                    root,
                    unit_size=globals.axes.unit_size,
                    center=p,
                )
                lower_label = get_lower_label(state)
                c.lower_label = lower_label
                globals.objects.register(c)
                state.points_for_obj.append(p)
                state.points_for_obj.append(c)

            else:
                state.points_for_obj[1].point_2 = p
                state.points_for_obj[1].update()
                globals.sidebar.items.append(state.points_for_obj[1])
                globals.sidebar.update()
                state.points_for_obj = []

        elif state.selected_tool == "circle_center_radius":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(e)
            p = find_point_at_position(e)
            if p is None:
                label = get_label(state)
                p = Point(
                    root,
                    e=None,
                    label=label,
                    unit_size=globals.axes.unit_size,
                    pos_x=world_x,
                    pos_y=world_y,
                )
                globals.objects.register(p)
            radius = simpledialog.askfloat(
            "radius",
            "radius",
            minvalue=0,
            )
            c = Circle_center_radius(
                root,
                unit_size=globals.axes.unit_size,
                center=p,
            )
            lower_label = get_lower_label(state)
            c.lower_label = lower_label
            c.radius = radius
            globals.objects.register(c)

            globals.sidebar.items.append(c)
            globals.sidebar.update()

        elif state.selected_tool == "compass":
            state.start_pos["x"] = e.x
            state.start_pos["y"] = e.y
            world_x, world_y = screen_to_world(e)
            p = find_point_at_position(e)
            if p is None:
                label = get_label(state)
                p = Point(
                    root,
                    e=None,
                    label=label,
                    unit_size=globals.axes.unit_size,
                    pos_x=world_x,
                    pos_y=world_y,
                )
                globals.objects.register(p)
            state.points_for_obj.append(p)

            if len(state.points_for_obj) == 2:
                c = Compass(
                    root
                )
                c.r_point_1 = state.points_for_obj[0]
                c.r_point_2 = state.points_for_obj[1]
                lower_label = get_lower_label(state)
                c.lower_label = lower_label
                globals.objects.register(c)
                c.update(e)
                state.points_for_obj.append(c)


            elif len(state.points_for_obj) == 4:
                state.points_for_obj[2].center = p
                state.points_for_obj[2].update(e)

                globals.sidebar.items.append(state.points_for_obj[2])
                globals.sidebar.update()

                state.points_for_obj = []


        elif state.selected_tool == "circle_3_points":
            world_x, world_y = screen_to_world(e)
            p = find_point_at_position(e)

            if p is None:
                p = Point(
                    root,
                    e=None,
                    label=get_label(state),
                    unit_size=globals.axes.unit_size,
                    pos_x=world_x,
                    pos_y=world_y,
                )
                globals.objects.register(p)

            if len(state.points_for_obj) == 0:
                state.points_for_obj.append(p)

                c = Circle_3_points(
                    root,
                    unit_size=globals.axes.unit_size,
                    point_1=p,
                )
                c.lower_label = get_lower_label(state)
                globals.objects.register(c)

                state.points_for_obj.append(c)

            elif len(state.points_for_obj) == 2:
                state.points_for_obj.append(p)
                state.points_for_obj[1].point_2 = p
                state.points_for_obj[1].update()

            elif len(state.points_for_obj) == 3:
                state.points_for_obj.append(p)
                state.points_for_obj[1].point_3 = p
                state.points_for_obj[1].update()

                globals.sidebar.items.append(state.points_for_obj[1])
                globals.sidebar.update()

                state.points_for_obj = []

        elif state.selected_tool == "semi_circle":
            world_x, world_y = screen_to_world(e)
            p = find_point_at_position(e)

            if p is None:
                p = Point(
                    root,
                    e=None,
                    label=get_label(state),
                    unit_size=globals.axes.unit_size,
                    pos_x=world_x,
                    pos_y=world_y,
                )
                globals.objects.register(p)

            p.select()

            if len(state.points_for_obj) == 0:
                state.points_for_obj.append(p)

                c = Semicircle(
                    root,
                    point_1=p,
                )
                c.lower_label = get_lower_label(state)
                globals.objects.register(c)

                state.points_for_obj.append(c)



            elif len(state.points_for_obj) == 2:
                state.points_for_obj.append(p)
                state.points_for_obj[1].point_2 = p
                state.points_for_obj[1].update()

                globals.sidebar.items.append(state.points_for_obj[1])
                globals.sidebar.update()

                state.points_for_obj[0].deselect()
                state.points_for_obj[2].deselect()

                state.points_for_obj = []




    def middle_click_pressed(e):
        state.start_pos["x"] = e.x
        state.start_pos["y"] = e.y

    def right_click_released(e):
        if state.selected_tool == "pen":
            set_cursor(globals.canvas, "crosshair")

    def left_click_released(e):
        if state.selected_tool == "freehand":
            state.current_pen.detect_shape()
            globals.objects.unregister(state.current_pen)
            globals.canvas.delete(state.current_pen.tag)
        elif state.selected_tool == "arrow":
            state.drag_target = None

        globals.objects.refresh()

    def left_click_pressed_sidebar(e):
        if abs(e.x - globals.sidebar.canvas.winfo_width()) <= 20:
            state.sidebar_resizing = True
            state.start_pos["x"] = e.x
            set_cursor(globals.sidebar.canvas, "sb_h_double_arrow")
        else:
            objs = globals.sidebar.canvas.find_overlapping(20, e.y - 3, globals.sidebar.canvas.winfo_width() - 20, e.y+3)
            if objs:
                deselect_all()
                for obj in objs:
                    item = globals.sidebar.canvas_tags.get(obj)
                    if item and hasattr(item, "select"):
                        item.select()
                        state.selected_point = item
                        break



    def left_click_released_sidebar(e):
        state.sidebar_resizing = False
        set_cursor(globals.sidebar.canvas, "")

    globals.canvas.bind("<Button-1>", left_click_pressed)
    globals.canvas.bind("<Button-3>", middle_click_pressed)
    globals.canvas.bind("<ButtonRelease-2>", right_click_released)
    globals.canvas.bind("<ButtonRelease-1>", left_click_released)
    globals.sidebar.canvas.bind("<Button-1>", left_click_pressed_sidebar)
    globals.sidebar.canvas.bind("<ButtonRelease-1>", left_click_released_sidebar)
