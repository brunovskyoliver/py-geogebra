import math
from tkinter import simpledialog
from tkinter import Tk

from py_geogebra.ui.compass import Compass
from py_geogebra.ui.semicircle import Semicircle
from py_geogebra.ui.tangents import Tangents

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
    create_or_find_point_at_position,
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

def arrow(e, root):
    state.start_pos["x"] = e.x
    state.start_pos["y"] = e.y
    state.drag_target = None

    point_obj = find_point_at_position(e)
    if point_obj:
        if state.selected_point and state.selected_point != point_obj:
            state.selected_point.deselect()
        else:
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

def point(e, root):
    state.start_pos["x"] = e.x
    state.start_pos["y"] = e.y

    create_or_find_point_at_position(e, root)

def attach_detach_point(e, root):
    state.start_pos["x"] = e.x
    state.start_pos["y"] = e.y
    state.drag_target = None

    point_obj = find_point_at_position(e)
    if point_obj:
        if state.selected_point and state.selected_point != point_obj:
            state.selected_point.deselect()
        else:
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

def intersect(e, root):
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

def pen(e, root):
    cx, cy = state.center
    world_x = (e.x - cx) / (globals.objects.unit_size * globals.objects.scale)
    world_y = (cy - e.y) / (globals.objects.unit_size * globals.objects.scale)

    state.current_pen = Pen(root, globals.objects.unit_size)
    state.current_pen.add_point(world_x, world_y)
    globals.objects.register(state.current_pen)

def freehand(e, root):
    cx, cy = state.center
    world_x = (e.x - cx) / (globals.objects.unit_size * globals.objects.scale)
    world_y = (cy - e.y) / (globals.objects.unit_size * globals.objects.scale)

    state.current_freehand = FreeHand(root, globals.objects.unit_size)
    state.current_freehand.add_point(world_x, world_y)
    globals.objects.register(state.current_freehand)

def line(e, root):
    state.start_pos["x"] = e.x
    state.start_pos["y"] = e.y
    world_x, world_y = screen_to_world(e)

    l = None
    if len(state.points_for_obj) == 2:
        l = state.points_for_obj[1]
    p = create_or_find_point_at_position(e, root, exception=l)

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

def segment(e, root):
    state.start_pos["x"] = e.x
    state.start_pos["y"] = e.y
    world_x, world_y = screen_to_world(e)

    l = None
    if len(state.points_for_obj) == 2:
        l = state.points_for_obj[1]
    p = create_or_find_point_at_position(e, root, exception=l)

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

def ray(e, root):
    state.start_pos["x"] = e.x
    state.start_pos["y"] = e.y
    world_x, world_y = screen_to_world(e)

    l = None
    if len(state.points_for_obj) == 2:
        l = state.points_for_obj[1]
    p = create_or_find_point_at_position(e, root, exception=l)

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

def polyline(e, root):
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

def segmnet_with_lenght(e, root):
    world_x, world_y = screen_to_world(e)

    p = create_or_find_point_at_position(e, root)

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

def midpoint_or_center(e, root):
    world_x, world_y = screen_to_world(e)

    p = create_or_find_point_at_position(e, root)

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

def vector(e, root):
    state.start_pos["x"] = e.x
    state.start_pos["y"] = e.y
    world_x, world_y = screen_to_world(e)

    l = None
    if len(state.points_for_obj) == 2:
        l = state.points_for_obj[1]
    p = create_or_find_point_at_position(e, root, exception=l)

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

def vector_from_point(e, root):
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

def perpendicular_line(e, root):
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
            p = create_or_find_point_at_position(e, root)
            state.selected_perpendicular_point = p
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

def parallel_line(e, root):
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
            p = create_or_find_point_at_position(e, root)
            state.selected_perpendicular_point = p
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

def perpendicular_bisector(e, root):
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

def angle_bisector(e, root):
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

def best_fit_line(e, root):
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

def c_polygon(e, root):
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

def regular_polygon(e, root):
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

def circle_center_point(e, root):
    state.start_pos["x"] = e.x
    state.start_pos["y"] = e.y
    world_x, world_y = screen_to_world(e)

    l = None
    if len(state.points_for_obj) == 2:
        l = state.points_for_obj[1]
    p = create_or_find_point_at_position(e, root, exception=l)

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

def circle_center_radius(e, root):
    state.start_pos["x"] = e.x
    state.start_pos["y"] = e.y
    world_x, world_y = screen_to_world(e)

    p = create_or_find_point_at_position(e, root)

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

def compass(e, root):
    state.start_pos["x"] = e.x
    state.start_pos["y"] = e.y
    world_x, world_y = screen_to_world(e)

    l = None
    if len(state.points_for_obj) == 3:
        l = state.points_for_obj[2]
    p = create_or_find_point_at_position(e, root, exception=l)

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

def circle_3_points(e, root):
    world_x, world_y = screen_to_world(e)

    l = None
    if len(state.points_for_obj) == 2:
        l = state.points_for_obj[1]
    p = create_or_find_point_at_position(e, root, exception=l)

    p.select()

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

def semi_circle(e, root):
    world_x, world_y = screen_to_world(e)

    l = None
    if len(state.points_for_obj) == 2:
        l = state.points_for_obj[1]
    p = create_or_find_point_at_position(e, root, exception=l)


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

def tangents(e, root):
    state.start_pos["x"] = e.x
    state.start_pos["y"] = e.y

    p = find_point_at_position(e)
    if p:
        state.tangents_point = p
        p.select()

    c = find_circle_at_position(e)
    if c:
        state.tangents_circle = c
        c.select()

    if state.tangents_circle and state.tangents_point:
        t = Tangents(root, point_1=state.tangents_point)
        t.circle = state.tangents_circle
        globals.objects.register(t)
        t.update()

        globals.objects.register(t.line_1)
        globals.objects.register(t.line_2)

        state.tangents_circle.deselect()
        state.tangents_point.deselect()
        state.tangents_circle = None
        state.tangents_point = None



def pressing(root:Tk) -> None:
    def left_click_pressed(e):


        if state.selected_tool == "arrow":
            arrow(e, root)
        elif state.selected_tool == "freehand":
            freehand(e, root)
        elif state.selected_tool == "pen":
            pen(e, root)


        elif state.selected_tool == "point":
            point(e, root)
        elif state.selected_tool == "point_on_object":
            pass
        elif state.selected_tool == "attach_detach_point":
            attach_detach_point(e, root)
        elif state.selected_tool == "intersect":
            intersect(e, root)
        elif state.selected_tool == "midpoint_or_center":
            midpoint_or_center(e, root)
        elif state.selected_tool == "complex_number":
            pass
        elif state.selected_tool == "extremum":
            pass
        elif state.selected_tool == "roots":
            pass


        elif state.selected_tool == "line":
            line(e, root)
        elif state.selected_tool == "segment":
            segment(e, root)
        elif state.selected_tool == "segment_with_length":
            segmnet_with_lenght(e, root)
        elif state.selected_tool == "ray":
            ray(e, root)
        elif state.selected_tool == "polyline":
            polyline(e, root)
        elif state.selected_tool == "vector":
            vector(e, root)
        elif state.selected_tool == "vector_from_point":
            vector_from_point(e, root)


        elif state.selected_tool == "perpendicular_line":
            perpendicular_line(e, root)
        elif state.selected_tool == "parallel_line":
            parallel_line(e, root)
        elif state.selected_tool == "perpendicular_bisector":
            perpendicular_bisector(e, root)
        elif state.selected_tool == "angle_bisector":
            angle_bisector(e, root)
        elif state.selected_tool == "tangents":
            tangents(e, root)
        elif state.selected_tool == "polar_or_diameter_line":
            pass
        elif state.selected_tool == "best_fit_line":
            best_fit_line(e, root)
        elif state.selected_tool == "locus":
            pass


        elif state.selected_tool == "polygon":
            c_polygon(e, root)
        elif state.selected_tool == "regular_polygon":
            regular_polygon(e, root)
        elif state.selected_tool == "rigid_polygon":
            pass
        elif state.selected_tool == "vector_polygon":
            pass


        elif state.selected_tool == "circle_center_point":
            circle_center_point(e, root)
        elif state.selected_tool == "circle_center_radius":
            circle_center_radius(e, root)
        elif state.selected_tool == "compass":
            compass(e, root)
        elif state.selected_tool == "circle_3_points":
            circle_3_points(e, root)
        elif state.selected_tool == "semi_circle":
            semi_circle(e, root)
        elif state.selected_tool == "circular_arc":
            pass
        elif state.selected_tool == "circumcircular_arc":
            pass
        elif state.selected_tool == "circular_sector":
            pass
        elif state.selected_tool == "circumcircular_sector":
            pass





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
