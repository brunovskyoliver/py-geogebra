import tkinter as tk
import math


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


def center(canvas: tk.Canvas, objects):
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    cx = width // 2 + objects.offset_x
    cy = height // 2 + objects.offset_y
    return cx, cy


def snap(canvas, objects, e, axes):
    cx, cy = center(canvas, objects)
    world_x = (e.x - cx) / (objects.unit_size * objects.scale)
    world_y = (cy - e.y) / (objects.unit_size * objects.scale)
    step = axes.nice_step()
    world_x = math.floor(world_x / step + 0.5) * step
    world_y = math.floor(world_y / step + 0.5) * step
    return world_x, world_y


def get_label(state):
    label = number_to_ascii(state.label_counter)
    if state.label_counter_bck is None:
        state.label_counter += 1
    else:
        state.label_counter = state.label_counter_bck
        state.label_counter_bck = None
    state.label_list.append(label)
    return label


def set_cursor(canvas: tk.Canvas, cursor: str):
    canvas.configure(cursor=cursor)
    canvas.update()
    canvas.focus_set()


def reconfigure_label_order(label: str, state):
    state.label_list.remove(label)
    state.label_counter_bck = state.label_counter
    state.label_counter = ascii_to_number(label)


def delete_object(canvas, objects, object_to_delete, state):
    from ..ui.point import Point

    objects.unregister(object_to_delete)
    canvas.delete(object_to_delete.tag)
    if hasattr(object_to_delete, "highlight_tag"):
        canvas.delete(object_to_delete.highlight_tag)
    if isinstance(object_to_delete, Point):
        state.selected_point = None
        label = object_to_delete.label
        reconfigure_label_order(label, state)


def world_to_screen(canvas, objects, wx, wy):
    cx, cy = center(canvas, objects)
    sx = cx + wx * objects.unit_size * objects.scale
    sy = cy - wy * objects.unit_size * objects.scale
    return sx, sy
