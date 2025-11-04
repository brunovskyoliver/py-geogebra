from os.path import isjunction
import tkinter as tk
import math
from tkinter import image_names, messagebox
from typing import List


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
    step = g().axes.current_step
    world_x = round(world_x / step) * step
    world_y = round(world_y / step) * step
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
    from ..ui.polygon import Polygon
    from ..ui.perpendicular_bisector import Perpendicular_bisector
    from ..tools.utils import reconfigure_label_order

    if state.points_for_obj:
        for obj in state.points_for_obj:
            g().objects.unregister(obj)
            g().canvas.delete(obj.tag)
            if hasattr(obj, "highlight_tag"):
                g().canvas.delete(obj.highlight_tag)
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
                or isinstance(obj,Perpendicular_bisector)
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
                or isinstance(obj, Polygon)
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
            if isinstance(obj, Polygon) and object_to_delete in obj.points:
                g().objects.unregister(obj)
                g().canvas.delete(obj.tag)

        state.selected_point = None
        reconfigure_label_order(object_to_delete.label, state)
    if isinstance(object_to_delete, Polyline):
        for obj in object_to_delete.points:
            g().objects.unregister(obj)
            g().canvas.delete(obj.tag)
            reconfigure_label_order(obj.label, state)
    if isinstance(object_to_delete, Polygon):
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


def find_point_at_position(e, r=2):
    from ..ui.point import Point
    from ..ui.midpoint_or_center import Midpoint_or_center
    from ..ui.intersect import Intersect
    items = g().canvas.find_overlapping(e.x - r, e.y - r, e.x + r, e.y + r)
    p = None
    for obj in g().objects._objects:
        if hasattr(obj, "tag") and any(obj.tag in g().canvas.gettags(i) for i in items) and (isinstance(obj, Point) or isinstance(obj, Intersect) or isinstance(obj, Midpoint_or_center)):
            if "point" in obj.tag or "intersect" in obj.tag:
                p = obj
                break
    return p


def find_line_at_position(e, r=2, num_lines: int = 1):
    items = g().canvas.find_overlapping(e.x - r, e.y - r, e.x + r, e.y + r)
    lines = []
    line_count = 0
    for obj in g().objects._objects:
        if hasattr(obj, "tag") and any(obj.tag in g().canvas.gettags(i) for i in items):
            if (
                ("line" in obj.tag and "polyline" not in obj.tag)
                or "ray" in obj.tag
                or "segment" in obj.tag
                or "segment_with_length" in obj.tag
                or "vector" in obj.tag
                or "angle_bisector" in obj.tag
                or "perpendicular_bisector" in obj.tag
            ):
                lines.append(obj)
                line_count += 1
                if line_count == num_lines:
                    break
    if num_lines == 1:
        return lines[0]
    else:
        return lines


def find_polyline_at_position(e, r=2):
    from ..ui.polyline import Polyline
    from ..ui.polygon import Polygon
    from ..ui.regular_polygon import Regular_polygon
    items = g().canvas.find_overlapping(e.x - r, e.y - r, e.x + r, e.y + r)
    line = None
    for obj in g().objects._objects:
        if hasattr(obj, "tag") and any(obj.tag in g().canvas.gettags(i) for i in items) and (isinstance(obj, Polyline) or isinstance(obj, Polygon) or isinstance(obj, Regular_polygon)):
            if "polyline" in obj.tag or "polygon" in obj.tag:
                line = obj
                break
    return line

def find_circle_at_position(e, r=2):
    from ..ui.circle_center_point import Circle_center_point
    from ..ui.circle_center_radius import Circle_center_radius
    from ..ui.compass import Compass

    items = g().canvas.find_overlapping(e.x - r, e.y - r, e.x + r, e.y + r)
    line = None
    for obj in g().objects._objects:
        if hasattr(obj, "tag") and any(obj.tag in g().canvas.gettags(i) for i in items) and (isinstance(obj, Circle_center_radius) or isinstance(obj, Circle_center_point) or isinstance(obj, Compass)):
            if "circle" in obj.tag:
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


def snap_to_circle(point, circle):
    dx = point.pos_x - circle.point_1.pos_x
    dy = point.pos_y - circle.point_1.pos_y
    dist = math.hypot(dx, dy)
    k = point.translation / dist
    point.pos_x = circle.point_1.pos_x + dx * k
    point.pos_y = circle.point_1.pos_y + dy * k

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

def find_translation_circle(point, circle):

    point.translation = circle.radius

def find_translation_between_points(point, point_1, point_2):
    x1, y1 = point_1.pos_x, point_1.pos_y
    x2, y2 = point_2.pos_x, point_2.pos_y
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




def find_2lines_intersection(points):
    x1, y1 = (
        points[0].pos_x,
        points[0].pos_y,
    )
    x2, y2 = (
        points[1].pos_x,
        points[1].pos_y,
    )
    x3, y3 = (
        points[2].pos_x,
        points[2].pos_y,
    )
    x4, y4 = (
        points[3].pos_x,
        points[3].pos_y,
    )

    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / (
        (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    )
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / (
        (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    )

    return (px, py)

def find_circle_line_intersection(circle, p1, p2):
    x1,y1 = p1.pos_x, p1.pos_y
    x2,y2 = p2.pos_x, p2.pos_y
    c_pt = circle.point_1
    vector = (x2-x1, y2 - y1)
    a = vector[0]**2 + vector[1]**2
    b = 2*x1*vector[0] - 2*c_pt.pos_x*vector[0] + 2*y1*vector[1] - 2*c_pt.pos_y*vector[1]
    c = x1**2 - 2*c_pt.pos_x*x1 + c_pt.pos_x**2 + y1**2 - 2*c_pt.pos_y*y1 + c_pt.pos_y**2 - circle.radius**2
    k = []
    k.extend(solve_quadratic(a,b,c))
    intersections = []

    for i in range(len(k)):
        intersections.append((x1 + k[i]*vector[0], y1 + k[i]*vector[1]))


    return intersections

def find_circle_circle_intersection(circle1, circle2):
        x1, y1 = circle1.point_1.pos_x, circle1.point_1.pos_y
        r1 = circle1.radius
        x2, y2 = circle2.point_1.pos_x, circle2.point_1.pos_y
        r2 = circle2.radius

        dx, dy = x2 - x1, y2 - y1
        d = (dx**2 + dy**2) ** 0.5

        if d > r1 + r2 or d < abs(r1 - r2) or d == 0:
            return None  # no intersection or infinite

        a = (r1**2 - r2**2 + d**2) / (2 * d)
        h = (r1**2 - a**2) ** 0.5
        xm = x1 + a * dx / d
        ym = y1 + a * dy / d
        xs1 = xm + h * dy / d
        ys1 = ym - h * dx / d
        xs2 = xm - h * dy / d
        ys2 = ym + h * dx / d
        return [(xs1, ys1), (xs2, ys2)]






def get_linear_fuction_prescription(x1, y1, x2, y2):
    a = y2 - y1
    b = x1 - x2
    c = x2 * y1 - x1 * y2
    return round(a, 2), round(b, 2), round(-c, 2)

def detach_point(point, line):
    from ..ui.polyline import Polyline
    from ..ui.circle_center_point import Circle_center_point
    from ..ui.circle_center_radius import Circle_center_radius
    if not isinstance(line, Polyline) and not isinstance(line, Circle_center_point)and not isinstance(line, Circle_center_radius):
        dx = line.point_2.pos_x - line.point_1.pos_x
        dy = line.point_2.pos_y - line.point_1.pos_y

    if isinstance(line, Polyline):
        smallest_dist = float("inf")
        for i in range(len(line.line_points) - 1):
            dist = (
                distance(
                    point.pos_x,
                    point.pos_y,
                    line.line_points[i].pos_x,
                    line.line_points[i].pos_y,
                )
                + distance(
                    point.pos_x,
                    point.pos_y,
                    line.line_points[i + 1].pos_x,
                    line.line_points[i + 1].pos_y,
                )
                - distance(
                    line.line_points[i].pos_x,
                    line.line_points[i].pos_y,
                    line.line_points[i + 1].pos_x,
                    line.line_points[i + 1].pos_y,
                )
            )
            if dist < smallest_dist:
                smallest_dist = dist
                index_1 = i
                index_2 = i + 1

        x1, y1 = line.line_points[index_1].pos_x, line.line_points[index_1].pos_y
        x2, y2 = line.line_points[index_2].pos_x, line.line_points[index_2].pos_y

        dx = x2 - x1
        dy = y2 - y1
    elif isinstance(line, Circle_center_point) or isinstance(line, Circle_center_radius):
        x1, y1 = line.point_1.pos_x, line.point_1.pos_y
        dx = point.pos_x - x1
        dy = point.pos_y - y1
    else:
        dx = line.point_2.pos_x - line.point_1.pos_x
        dy = line.point_2.pos_y - line.point_1.pos_y

    length = math.hypot(dx, dy)
    if length == 0:
        return
    perp_x = -dy / length
    perp_y = dx / length


    point.pos_x += perp_x
    point.pos_y += perp_y

def attach_point(point, line):
    from ..ui.polyline import Polyline
    from ..ui.circle_center_point import Circle_center_point
    from ..ui.circle_center_radius import Circle_center_radius
    if isinstance(line, Polyline):
        find_translation_polyline(point, line)
        snap_to_polyline(point, line)
    elif isinstance(line, Circle_center_point) or isinstance(line, Circle_center_radius):
        find_translation_circle(point, line)
        snap_to_circle(point, line)
    else:
        find_translation(point, line)
        snap_to_line(point, line)

def calculate_vector(point_1, point_2):
    return (point_1.pos_x - point_2.pos_x, point_1.pos_y - point_2.pos_y)

def load_lines_from_labels(labels):
    lines = []
    for label in labels:
        for obj in g().objects._objects:
            if getattr(obj, "lower_label", None) == label:
                lines.append(obj)
    return lines

def handle_auth() -> dict | None:
    auth = g().auth
    user_info = auth.get_user_info()
    if not user_info:
        access_token = auth.authenticate()
        if not access_token:
            messagebox.showerror(_("Chyba"), _("Nepodarilo sa authentikovať"))
            return None
        user_info = auth.get_user_info()
        if not user_info:
            return None
    return user_info

def calculate_points_for_best_fit_line(points):
    # na toto som urcote dosiel sam
    xs = [p.pos_x for p in points]
    ys = [p.pos_y for p in points]
    n = len(points)

    mean_x = sum(xs) / n
    mean_y = sum(ys) / n


    numerator = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
    denominator = sum((xs[i] - mean_x) ** 2 for i in range(n))
    if denominator == 0:
        raise ValueError("Cannot compute line — all x values are identical")

    m = numerator / denominator
    b = mean_y - m * mean_x

    x1 = min(xs)
    x2 = max(xs)
    y1 = m * x1 + b
    y2 = m * x2 + b

    return x1, x2, y1, y2

def solve_quadratic(a, b, c):
    if a == 0:
        if b == 0:
            return []
        return [-c / b]

    discriminant = b**2 - 4*a*c
    if discriminant < 0:
        return []
    elif discriminant == 0:
        x = -b / (2*a)
        return [x]
    else:
        sqrt_disc = math.sqrt(discriminant)
        x1 = (-b + sqrt_disc) / (2*a)
        x2 = (-b - sqrt_disc) / (2*a)
        return [x1, x2]
