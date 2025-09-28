import tkinter as tk
import math

from .. import state

import importlib

_globals = None


def g():
    global _globals
    if _globals is None:
        _globals = importlib.import_module("py_geogebra.globals")
    return _globals


def number_to_ascii(n: int):
    s = ""
    n += 1
    while n:
        n -= 1
        r = n % 26
        s = chr(65 + r) + s
        n //= 26

    return s


def ascii_to_number(s: str):
    n = 0
    for ch in s:
        n = n * 26 + (ord(ch) - 65 + 1)
    return n - 1


def center():
    width = g().canvas.winfo_width()
    height = g().canvas.winfo_height()
    cx = width // 2 + g().objects.offset_x
    cy = height // 2 + g().objects.offset_y
    return cx, cy


def center_screen():
    width = g().canvas.winfo_width()
    height = g().canvas.winfo_height()
    return width // 2, height // 2


def screen_to_world(e):
    cx, cy = state.center
    world_x = (e.x - cx) / (g().objects.unit_size * g().objects.scale)
    world_y = (cy - e.y) / (g().objects.unit_size * g().objects.scale)
    return world_x, world_y


def snap(e):
    world_x, world_y = screen_to_world(e)
    step = g().axes.nice_step()
    world_x = math.floor(world_x / step + 0.5) * step
    world_y = math.floor(world_y / step + 0.5) * step
    return world_x, world_y


def get_label(state):
    if state.label_unused:
        label = state.label_unused.pop(0)
    else:
        label = number_to_ascii(state.label_counter)
        state.label_counter += 1
    return label


def get_lower_label(state):
    if state.lower_label_unused:
        label = state.lower_label_unused.pop(0)
    else:
        label = number_to_ascii(state.lower_label_counter)
        state.lower_label_counter += 1
    return label.lower()


def set_cursor(canvas: tk.Canvas, cursor: str):
    canvas.configure(cursor=cursor)
    canvas.update()
    canvas.focus_set()


def reconfigure_label_order(label: str, state):
    state.label_unused.append(label)


def reconfigure_lower_label_order(lower_label: str, state):
    state.lower_label_unused.append(lower_label)


def delete_object(object_to_delete, state):
    from ..ui.point import Point
    from ..ui.midpoint_or_center import Midpoint_or_center
    from ..ui.line import Line
    from ..ui.ray import Ray
    from ..ui.segment import Segment
    from ..ui.segment_with_lenght import Segment_with_length
    from ..ui.polyline import Polyline
    from ..tools.utils import reconfigure_label_order

    if state.points_for_obj:
        for obj in state.points_for_obj:
            g().objects.unregister(obj)
            g().canvas.delete(obj.tag)
            if hasattr(obj, "highlight_tag"):
                g().canvas.delete(obj.highlight_tag)
            if isinstance(obj, Point):
                g().sidebar.items.remove(obj)
                reconfigure_label_order(obj.label, state)
        state.points_for_obj.clear()

    if isinstance(object_to_delete, Point):
        if state.selected_point in g().sidebar.items:
            g().sidebar.items.remove(state.selected_point)
            g().sidebar.update()
        for obj in list(g().objects._objects):
            if (
                isinstance(obj, Line)
                or isinstance(obj, Segment)
                or isinstance(obj, Ray)
                or isinstance(obj, Segment_with_length)
                or isinstance(obj, Midpoint_or_center)
            ) and (obj.point_1 is object_to_delete or obj.point_2 is object_to_delete):
                g().objects.unregister(obj)
                g().canvas.delete(obj.tag)
                if hasattr(obj, "lower_label"):
                    g().objects.unregister(obj.lower_label_obj)

            if (
                isinstance(obj, Line)
                or isinstance(obj, Ray)
                or isinstance(obj, Segment)
                or isinstance(obj, Polyline)
            ):
                reconfigure_lower_label_order(obj.lower_label, state)
                g().sidebar.items.remove(obj)
                g().sidebar.update()

            if isinstance(obj, Midpoint_or_center):
                g().sidebar.items.remove(obj)
                g().sidebar.update()
            if isinstance(obj, Polyline) and object_to_delete in obj.points:
                g().objects.unregister(obj)
                g().canvas.delete(obj.tag)

        state.selected_point = None
        reconfigure_label_order(object_to_delete.label, state)
    if isinstance(object_to_delete, Polyline):
        for obj in object_to_delete.points:
            g().objects.unregister(obj)
            g().canvas.delete(obj.tag)
            reconfigure_label_order(obj.label, state)

    g().objects.unregister(object_to_delete)
    g().canvas.delete(object_to_delete.tag)
    if hasattr(object_to_delete, "highlight_tag"):
        g().canvas.delete(object_to_delete.highlight_tag)


def world_to_screen(wx, wy):
    cx, cy = state.center
    sx = cx + wx * g().objects.unit_size * g().objects.scale
    sy = cy - wy * g().objects.unit_size * g().objects.scale
    return sx, sy


def distance(x1, y1, x2, y2, r: int = 0):
    d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    if r != 0:
        return round(d, r)
    return d


def deselect_all():
    for obj in g().objects._objects:
        if hasattr(obj, "deselect"):
            obj.deselect()


def find_point_at_position(e, r=1):
    items = g().canvas.find_overlapping(e.x - r, e.y - r, e.x + r, e.y + r)
    p = None
    for obj in g().objects._objects:
        if hasattr(obj, "tag") and any(obj.tag in g().canvas.gettags(i) for i in items):
            if "point" in obj.tag or "intersect" in obj.tag:
                p = obj
                break
    return p


def find_line_at_position(e, r=1):
    items = g().canvas.find_overlapping(e.x - r, e.y - r, e.x + r, e.y + r)
    line = None
    for obj in g().objects._objects:
        if hasattr(obj, "tag") and any(obj.tag in g().canvas.gettags(i) for i in items):
            if (
                ("line" in obj.tag and "polyline" not in obj.tag)
                or "ray" in obj.tag
                or "segment" in obj.tag
                or "segment_with_length" in obj.tag
            ):
                line = obj
                break
    return line


def find_polyline_at_position(e, r=1):
    items = g().canvas.find_overlapping(e.x - r, e.y - r, e.x + r, e.y + r)
    line = None
    for obj in g().objects._objects:
        if hasattr(obj, "tag") and any(obj.tag in g().canvas.gettags(i) for i in items):
            if "polyline" in obj.tag:
                line = obj
                break
    return line


def snap_to_line(point, line):
    x1, y1 = line.point_1.pos_x, line.point_1.pos_y
    x2, y2 = line.point_2.pos_x, line.point_2.pos_y

    dx, dy = x2 - x1, y2 - y1

    t = point.translation

    proj_x = x1 + t * dx
    proj_y = y1 + t * dy

    point.pos_x = proj_x
    point.pos_y = proj_y


def snap_to_polyline(point, polyline):
    smallest_dist = float("inf")
    index_1 = 0
    index_2 = 0
    for i in range(len(polyline.line_points) - 1):
        dist = (
            distance(
                point.pos_x,
                point.pos_y,
                polyline.line_points[i].pos_x,
                polyline.line_points[i].pos_y,
            )
            + distance(
                point.pos_x,
                point.pos_y,
                polyline.line_points[i + 1].pos_x,
                polyline.line_points[i + 1].pos_y,
            )
            - distance(
                polyline.line_points[i].pos_x,
                polyline.line_points[i].pos_y,
                polyline.line_points[i + 1].pos_x,
                polyline.line_points[i + 1].pos_y,
            )
        )
        if dist < smallest_dist:
            smallest_dist = dist
            index_1 = i
            index_2 = i + 1

    x1, y1 = polyline.line_points[index_1].pos_x, polyline.line_points[index_1].pos_y
    x2, y2 = polyline.line_points[index_2].pos_x, polyline.line_points[index_2].pos_y

    dx, dy = x2 - x1, y2 - y1

    t = point.translation

    proj_x = x1 + t * dx
    proj_y = y1 + t * dy

    point.pos_x = proj_x
    point.pos_y = proj_y


def find_translation(point, line):
    x1, y1 = line.point_1.pos_x, line.point_1.pos_y
    x2, y2 = line.point_2.pos_x, line.point_2.pos_y
    px, py = point.pos_x, point.pos_y
    alpha = math.atan2(y2 - y1, x2 - x1)
    gama = math.atan2(px - x1, py - y1)
    beta = math.pi / 2 - alpha - gama
    dist = distance(x1, y1, x2, y2)
    p_dist = distance(x1, y1, px, py)

    point.translation = (p_dist * math.cos(beta)) / dist


def find_translation_polyline(point, polyline):
    smallest_dist = float("inf")
    index_1 = 0
    index_2 = 0
    for i in range(len(polyline.line_points) - 1):
        dist = (
            distance(
                point.pos_x,
                point.pos_y,
                polyline.line_points[i].pos_x,
                polyline.line_points[i].pos_y,
            )
            + distance(
                point.pos_x,
                point.pos_y,
                polyline.line_points[i + 1].pos_x,
                polyline.line_points[i + 1].pos_y,
            )
            - distance(
                polyline.line_points[i].pos_x,
                polyline.line_points[i].pos_y,
                polyline.line_points[i + 1].pos_x,
                polyline.line_points[i + 1].pos_y,
            )
        )
        if dist < smallest_dist:
            smallest_dist = dist
            index_1 = i
            index_2 = i + 1

    x1, y1 = polyline.line_points[index_1].pos_x, polyline.line_points[index_1].pos_y
    x2, y2 = polyline.line_points[index_2].pos_x, polyline.line_points[index_2].pos_y
    px, py = point.pos_x, point.pos_y
    alpha = math.atan2(y2 - y1, x2 - x1)
    gama = math.atan2(px - x1, py - y1)
    beta = math.pi / 2 - alpha - gama
    dist = distance(x1, y1, x2, y2)
    p_dist = distance(x1, y1, px, py)

    point.translation = (p_dist * math.cos(beta)) / dist


def find_2lines_intersection(line_1, line_2):
    x1, y1 = (
        line_1.point_1.pos_x,
        line_1.point_1.pos_y,
    )
    x2, y2 = (
        line_1.point_2.pos_x,
        line_1.point_2.pos_y,
    )
    x3, y3 = (
        line_2.point_1.pos_x,
        line_2.point_1.pos_y,
    )
    x4, y4 = (
        line_2.point_2.pos_x,
        line_2.point_2.pos_y,
    )

    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / (
        (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    )
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / (
        (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    )

    return px, py


def get_linear_fuction_prescription(x1, y1, x2, y2):
    a = y2 - y1
    b = x1 - x2
    c = x2 * y1 - x1 * y2
    return round(a, 2), round(b, 2), round(-c, 2)
