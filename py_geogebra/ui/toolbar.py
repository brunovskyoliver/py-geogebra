from os import confstr
import tkinter as tk
from typing import ChainMap
from ..tools.load_image import load_icon
from ..tools.utils import delete_object, set_cursor, deselect_all_points
from .. import state



def show_menu(e, menu):
    x = e.widget.winfo_rootx()
    y = e.widget.winfo_rooty() + e.widget.winfo_height()
    menu.tk_popup(x, y)


def update_labels(items, menu):
    def _init():
        for i in items:
            menu.entryconfig(i["index"], label=_(i["name"]))

    return _init


# https://stackoverflow.com/questions/61724685/python-tkinter-cursor-icon-change-size
def change_icon(canvas, img, btn, tool_name, objects):
    btn.configure(image=img)
    btn.image = img
    if state.selected_tool == "line" and state.selected_tool != tool_name:
        for obj in list(state.points_for_obj):
            delete_object(canvas, objects, obj, state)
        state.points_for_obj.clear()
    deselect_all_points(objects)
    state.selected_tool = tool_name

    if tool_name in ("pen", "freehand"):
        cursor = "crosshair"  # pencil nefunguje spravne na macu z nejakeho dovodu
    else:
        cursor = ""
    set_cursor(canvas, cursor)
    if state.selected_point:
        state.selected_point.deselect()


def tool_menu_init(root, canvas, bar, widgets, def_icon, buttons, objects):
    icons = {
        name: load_icon(name)
        for name in {def_icon, *[button["icon"] for button in buttons]}
    }  # https://www.geeksforgeeks.org/python/packing-and-unpacking-arguments-in-python/
    default_icon = icons[def_icon]
    button = tk.Button(
        bar,
        image=default_icon,
        text="",
        bg="white",
        activebackground="white",
        relief="flat",
        bd=0,
        highlightthickness=0,
    )
    button.image = default_icon
    button.pack(side="left", padx=4, pady=4)

    menu = tk.Menu(root, tearoff=0, bg="white", activebackground="white")
    items = []
    for b in buttons:
        icon = icons[b["icon"]]
        menu.add_command(
            label=_(b["name"]),
            image=icon,
            compound="left",
            command=lambda img=icon, tool_name=b["icon"]: change_icon(
                canvas, img, button, tool_name, objects
            ),
        )
        i = (
            menu.index("end") or 0
        )  # prvy je vzdy 0 a index hadze error pri prvom bez oru
        items.append({"name": b["name"], "icon": icon, "index": i})

    menu.entries = items

    button.bind("<Button-1>", lambda e, m=menu: show_menu(e, m))

    widgets.register(update_labels(items, menu))

    return button, menu


def toolbar(root, canvas, widgets, objects):
    root.configure(bg="white")
    bar = tk.Frame(root, height=40, bg="white", bd=0, highlightthickness=0)
    bar.pack(side="top", fill="x")

    tool_menu_init(
        root,
        canvas,
        bar,
        widgets,
        def_icon="arrow",
        buttons=[
            {"name": _("Pohyb"), "icon": "arrow"},
            {"name": _("Voľný tvar"), "icon": "freehand"},
            {"name": _("Nástroj pero"), "icon": "pen"},
        ],
        objects=objects,
    )
    tool_menu_init(
        root,
        canvas,
        bar,
        widgets,
        def_icon="point",
        buttons=[
            {"name": _("Bod"), "icon": "point"},
            {"name": _("Bod na objekte"), "icon": "point_on_object"},
            {"name": _("Pripojiť / Odpojiť bod"), "icon": "attach_detach_point"},
            {"name": _("Priesečník"), "icon": "intersect"},
            {"name": _("Stred"), "icon": "midpoint_or_center"},
            {"name": _("Komplexné číslo"), "icon": "complex_number"},
            {"name": _("Extremum"), "icon": "extremum"},
            {"name": _("Korene"), "icon": "roots"},
        ],
        objects=objects,
    )
    tool_menu_init(
        root,
        canvas,
        bar,
        widgets,
        def_icon="line",
        buttons=[
            {"name": _("Priamka"), "icon": "line"},
            {"name": _("Úsečka"), "icon": "segment"},
            {"name": _("Úsečka s danou dĺžkou"), "icon": "segment_with_length"},
            {"name": _("Polpriamka"), "icon": "ray"},
            {"name": _("Zalomená čiara"), "icon": "polyline"},
            {"name": _("Vektor"), "icon": "vector"},
            {"name": _("Vektor z bodu"), "icon": "vector_from_point"},
        ],
        objects=objects,
    )
    state.selected_tool = "arrow"

    return bar
