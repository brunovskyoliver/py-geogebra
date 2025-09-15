import tkinter as tk


def number_to_ascii(n: int):
    s = ""
    n += 1
    while n:
        n -= 1
        r = n % 26
        s = chr(65 + r) + s
        n //= 26

    return s


def center(canvas: tk.Canvas, objects):
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    cx = width // 2 + objects.offset_x
    cy = height // 2 + objects.offset_y
    return cx, cy


def set_cursor(canvas: tk.Canvas, cursor: str):
    canvas.configure(cursor=cursor)
    canvas.update()
    canvas.focus_set()


def delete_object(canvas, objects, object_to_delete, state):
    objects.unregister(object_to_delete)
    canvas.delete(object_to_delete.tag)
    if hasattr(object_to_delete, "highlight_tag"):
        canvas.delete(object_to_delete.highlight_tag)
        state.selected_point = None
