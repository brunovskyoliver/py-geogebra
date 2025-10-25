import json, inspect


def to_dict() -> dict:
    g = globals()
    return {
        name: g[name]
        for name, val in g.items()
        if not name.startswith("_")
        and not inspect.isfunction(val)
        and not inspect.isclass(val)
        and not inspect.ismodule(val)
        and name not in ["points_for_obj", "selected_point"]
    }


def load_from_dict(data: dict) -> None:
    g = globals()
    for name, val in data.items():
        if name in g:
            g[name] = val


selected_tool = None
start_pos = {"x": 0, "y": 0}
scale = 1.0
selected_point = None
current_pen = None
current_polyline = None
label_counter = 0
lower_label_counter = 0
label_unused = []
lower_label_unused = []
points_for_obj = []
freehand_last_pos = {"x": 0, "y": 0}
drag_target = None
deleted_point_label = None
center = (0, 0)
sidebar_resizing = False
selected_intersect_line_1 = None
shift_pressed = False
line_to_attach = None
point_to_attach = None
selected_vector = None
selected_vector_point = None
selected_perpendicular_point = None
selected_perpendicular_line = None
selected_angle_bisector_points = []
