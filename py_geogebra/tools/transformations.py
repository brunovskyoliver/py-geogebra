import math

from .. import state
from .utils import (
    distance,
    g,
    get_label,
    get_lower_label,
    get_object_color,
)
from ..ui.circle_3_points import Circle_3_points
from ..ui.circle_center_point import Circle_center_point
from ..ui.circle_center_radius import Circle_center_radius
from ..ui.intersect import Intersect
from ..ui.line import Line
from ..ui.midpoint_or_center import Midpoint_or_center
from ..ui.point import Point
from ..ui.point_on_object import Point_on_object
from ..ui.polygon import Polygon
from ..ui.polyline import Polyline
from ..ui.ray import Ray
from ..ui.regular_polygon import Regular_polygon
from ..ui.segment import Segment
from ..ui.segment_with_lenght import Segment_with_length
from ..ui.vector import Vector
from ..ui.vector_from_point import Vector_from_point


def reflect_point_across_point(x: float, y: float, center_x: float, center_y: float) -> tuple[float, float]:
    return 2 * center_x - x, 2 * center_y - y


def translate_point_by_vector(x: float, y: float, dx: float, dy: float) -> tuple[float, float]:
    return x + dx, y + dy


def rotate_point_around_point(
    x: float, y: float, center_x: float, center_y: float, angle_degrees: float
) -> tuple[float, float]:
    radians = math.radians(angle_degrees)
    dx = x - center_x
    dy = y - center_y
    rotated_dx = dx * math.cos(radians) - dy * math.sin(radians)
    rotated_dy = dx * math.sin(radians) + dy * math.cos(radians)
    return center_x + rotated_dx, center_y + rotated_dy


def dilate_point_from_point(
    x: float, y: float, center_x: float, center_y: float, factor: float
) -> tuple[float, float]:
    return center_x + (x - center_x) * factor, center_y + (y - center_y) * factor


def reflect_point_across_line(
    x: float,
    y: float,
    line_x1: float,
    line_y1: float,
    line_x2: float,
    line_y2: float,
) -> tuple[float, float]:
    dx = line_x2 - line_x1
    dy = line_y2 - line_y1
    denom = dx * dx + dy * dy
    if denom == 0:
        return x, y

    t = ((x - line_x1) * dx + (y - line_y1) * dy) / denom
    proj_x = line_x1 + t * dx
    proj_y = line_y1 + t * dy
    return 2 * proj_x - x, 2 * proj_y - y


def clear_transform_state() -> None:
    state.transform_source = None
    state.transform_reference = None


def is_transform_tool(tool_name: str | None) -> bool:
    return tool_name in {
        "reflect_about_line",
        "reflect_about_point",
        "reflect_about_circle",
        "rotate_around_point",
        "translate_by_vector",
        "dilate_from_point",
    }


def get_transform_reference_kind(tool_name: str) -> str | None:
    return {
        "reflect_about_line": "line",
        "reflect_about_point": "point",
        "reflect_about_circle": "circle",
        "rotate_around_point": "point",
        "translate_by_vector": "vector",
        "dilate_from_point": "point",
    }.get(tool_name)


def is_transformable_source(obj) -> bool:
    return isinstance(
        obj,
        (
            Point,
            Intersect,
            Point_on_object,
            Midpoint_or_center,
            Line,
            Segment,
            Segment_with_length,
            Ray,
            Vector,
            Vector_from_point,
            Polyline,
            Polygon,
            Regular_polygon,
            Circle_center_point,
            Circle_center_radius,
            Circle_3_points,
        ),
    )


def is_valid_transform_reference(obj, tool_name: str) -> bool:
    kind = get_transform_reference_kind(tool_name)
    if kind == "point":
        return isinstance(obj, (Point, Intersect, Point_on_object, Midpoint_or_center))
    if kind == "line":
        return isinstance(obj, (Line, Segment, Segment_with_length, Ray))
    if kind == "vector":
        return isinstance(obj, (Vector, Vector_from_point))
    if kind == "circle":
        return isinstance(obj, (Circle_center_point, Circle_center_radius, Circle_3_points))
    return False


def transform_reference_prompt(tool_name: str) -> str:
    return {
        "reflect_about_line": "Select a line, segment, or ray to reflect about.",
        "reflect_about_point": "Select a point to reflect about.",
        "reflect_about_circle": "Select a circle. This tool is still a placeholder.",
        "rotate_around_point": "Select a point to rotate around.",
        "translate_by_vector": "Select a vector to translate by.",
        "dilate_from_point": "Select a point to dilate from.",
    }.get(tool_name, "Select a reference object.")


def transform_value_prompt(tool_name: str) -> tuple[str, str] | None:
    prompts = {
        "rotate_around_point": ("Rotation", "Angle in degrees"),
        "dilate_from_point": ("Dilation", "Scale factor"),
    }
    return prompts.get(tool_name)


def _new_point(x: float, y: float, color: str | None = None):
    root = g().root
    point = Point(
        root,
        None,
        label=get_label(state),
        unit_size=g().objects.unit_size,
        pos_x=x,
        pos_y=y,
        color=color or "#349aff",
    )
    g().objects.register(point)
    return point


def _append_sidebar_item(obj) -> None:
    sidebar = getattr(g(), "sidebar", None)
    if sidebar and obj not in sidebar.items:
        sidebar.items.append(obj)
        sidebar.update()


def _two_point_data(obj):
    if isinstance(obj, (Line, Segment, Segment_with_length, Ray, Vector, Vector_from_point)):
        return obj.point_1, obj.point_2
    return None, None


def _transform_function(tool_name: str, reference, numeric_value: float | None):
    if tool_name == "reflect_about_line":
        p1, p2 = reference.point_1, reference.point_2
        return lambda x, y: reflect_point_across_line(x, y, p1.pos_x, p1.pos_y, p2.pos_x, p2.pos_y)
    if tool_name == "reflect_about_point":
        return lambda x, y: reflect_point_across_point(x, y, reference.pos_x, reference.pos_y)
    if tool_name == "rotate_around_point":
        return lambda x, y: rotate_point_around_point(
            x, y, reference.pos_x, reference.pos_y, numeric_value or 0.0
        )
    if tool_name == "translate_by_vector":
        dx = reference.point_2.pos_x - reference.point_1.pos_x
        dy = reference.point_2.pos_y - reference.point_1.pos_y
        return lambda x, y: translate_point_by_vector(x, y, dx, dy)
    if tool_name == "dilate_from_point":
        return lambda x, y: dilate_point_from_point(
            x, y, reference.pos_x, reference.pos_y, numeric_value or 1.0
        )
    return None


def create_transformed_copy(source, tool_name: str, reference, numeric_value: float | None = None):
    transform_point = _transform_function(tool_name, reference, numeric_value)
    if transform_point is None:
        return None

    source_color = get_object_color(source)
    root = g().root
    created_points = {}

    def mapped_point(original, *, point_color: str | None = None):
        key = id(original)
        if key not in created_points:
            x, y = transform_point(original.pos_x, original.pos_y)
            created_points[key] = _new_point(x, y, color=point_color)
        return created_points[key]

    if isinstance(source, (Point, Intersect, Point_on_object, Midpoint_or_center)):
        x, y = transform_point(source.pos_x, source.pos_y)
        return _new_point(x, y, color=source_color)

    p1, p2 = _two_point_data(source)
    if p1 is not None and p2 is not None:
        new_p1 = mapped_point(p1)
        new_p2 = mapped_point(p2)
        if isinstance(source, Line):
            obj = Line(root=root, point_1=new_p1, unit_size=g().objects.unit_size)
        elif isinstance(source, (Segment, Segment_with_length)):
            obj = Segment(root=root, point_1=new_p1, unit_size=g().objects.unit_size)
        elif isinstance(source, Ray):
            obj = Ray(root=root, point_1=new_p1, unit_size=g().objects.unit_size)
        else:
            obj = Vector(root=root, point_1=new_p1, unit_size=g().objects.unit_size)
        obj.point_2 = new_p2
        obj.lower_label = get_lower_label(state)
        obj.color = source_color
        g().objects.register(obj)
        obj.update()
        _append_sidebar_item(obj)
        return obj

    if isinstance(source, Polyline):
        obj = Polyline(root=root, unit_size=g().objects.unit_size)
        obj.line_points = [mapped_point(point) for point in source.line_points]
        obj.last_not_set = False
        obj.lower_label = get_lower_label(state)
        obj.color = source_color
        g().objects.register(obj)
        obj.update()
        _append_sidebar_item(obj)
        return obj

    if isinstance(source, (Polygon, Regular_polygon)):
        obj = Polygon(root=root, unit_size=g().objects.unit_size)
        obj.line_points = [mapped_point(point) for point in source.line_points]
        obj.last_not_set = False
        obj.lower_label = get_lower_label(state)
        obj.color = source_color
        g().objects.register(obj)
        obj.handle_segments()
        obj.update()
        _append_sidebar_item(obj)
        return obj

    if isinstance(source, Circle_center_point):
        new_center = mapped_point(source.center)
        new_p2 = mapped_point(source.point_2)
        obj = Circle_center_point(root=root, center=new_center, unit_size=g().objects.unit_size)
        obj.point_2 = new_p2
        obj.lower_label = get_lower_label(state)
        obj.color = source_color
        g().objects.register(obj)
        obj.update()
        _append_sidebar_item(obj)
        return obj

    if isinstance(source, Circle_center_radius):
        new_center = mapped_point(source.center)
        sample_x, sample_y = transform_point(source.center.pos_x + source.radius, source.center.pos_y)
        obj = Circle_center_radius(root=root, center=new_center, unit_size=g().objects.unit_size)
        obj.radius = distance(new_center.pos_x, new_center.pos_y, sample_x, sample_y)
        obj.lower_label = get_lower_label(state)
        obj.color = source_color
        g().objects.register(obj)
        obj.update()
        _append_sidebar_item(obj)
        return obj

    if isinstance(source, Circle_3_points):
        new_p1 = mapped_point(source.point_1)
        new_p2 = mapped_point(source.point_2)
        new_p3 = mapped_point(source.point_3)
        obj = Circle_3_points(root=root, point_1=new_p1, unit_size=g().objects.unit_size)
        obj.point_2 = new_p2
        obj.point_3 = new_p3
        obj.lower_label = get_lower_label(state)
        obj.color = source_color
        g().objects.register(obj)
        obj.update()
        _append_sidebar_item(obj)
        return obj

    return None
