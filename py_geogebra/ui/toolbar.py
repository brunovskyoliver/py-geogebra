import tkinter as tk
from ..tools.load_image import load_icon
from ..tools.utils import delete_object, set_cursor, deselect_all
from .. import state
from .. import globals


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
def change_icon(img, btn, tool_name):
    btn.configure(image=img)
    btn.image = img
    if (
        state.selected_tool
        in (
            "line",
            "segment",
            "segment_with_length",
            "ray",
            "midpoint_or_center",
            "perpendicular_line",
            "perpendicular_bisector"
        )
        and state.selected_tool != tool_name
    ):
        for obj in list(state.points_for_obj):
            delete_object(obj, state)
        state.points_for_obj.clear()
    if state.selected_tool == "polyline" and state.current_polyline:
        delete_object(state.current_polyline, state)
        state.current_polyline = None
    if state.selected_tool == "polygon" and state.current_polygon:
        delete_object(state.current_polygon, state)
        state.current_polygon = None

    deselect_all()
    state.selected_tool = tool_name
    state.points_for_obj = []

    if tool_name in ("pen", "freehand"):
        cursor = "crosshair"  # pencil nefunguje spravne na macu z nejakeho dovodu
    else:
        cursor = ""
    set_cursor(globals.canvas, cursor)
    if state.selected_point:
        state.selected_point.deselect()
    if state.selected_intersect_line_1:
        state.selected_intersect_line_1 = None


def tool_menu_init(root, bar, def_icon, buttons):
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
                img, button, tool_name
            ),
        )
        i = (
            menu.index("end") or 0
        )  # prvy je vzdy 0 a index hadze error pri prvom bez oru
        items.append({"name": b["name"], "icon": icon, "index": i})

    menu.entries = items

    button.bind("<Button-1>", lambda e, m=menu: show_menu(e, m))

    globals.widgets.register(update_labels(items, menu))

    return button, menu


def toolbar(root):
    root.configure(bg="white")
    bar = tk.Frame(root, height=40, bg="white", bd=0, highlightthickness=0)
    bar.pack(side="top", fill="x")

    tool_menu_init(
        root,
        bar,
        def_icon="arrow",
        buttons=[
            {"name": _("Pohyb"), "icon": "arrow"},
            {"name": _("Voľný tvar"), "icon": "freehand"},
            {"name": _("Nástroj pero"), "icon": "pen"},
        ],
    )
    tool_menu_init(
        root,
        bar,
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
    )
    tool_menu_init(
        root,
        bar,
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
    )
    tool_menu_init(
        root,
        bar,
        def_icon="perpendicular_line",
        buttons=[
            {"name": _("Kolmica"), "icon": "perpendicular_line"},
            {"name": _("Rovnobežka"), "icon": "parallel_line"},
            {"name": _("Os úsečky"), "icon": "perpendicular_bisector"},
            {"name": _("Os uhla"), "icon": "angle_bisector"},
            {"name": _("Dotyčnice"), "icon": "tangents"},
            {"name": _("Polárna priamka alebo priemer"), "icon": "polar_or_diameter_line"},
            {"name": _("lineárna regresia"), "icon": "best_fit_line"},
            {"name": _("Množina bodov"), "icon": "locus"},
        ],
    )
    tool_menu_init(
        root,
        bar,
        def_icon="polygon",
        buttons=[
            {"name": _("Mnohouholník"), "icon": "polygon"},
            {"name": _("Pravidelný mnohouholník"), "icon": "regular_polygon"},
            {"name": _("Pevný mnohouholník"), "icon": "rigid_polygon"},
            {"name": _("Vektorový mnohouholník"), "icon": "vector_polygon"},
        ],
    )
    tool_menu_init(
        root,
        bar,
        def_icon="circle_center_point",
        buttons=[
            {"name": _("Kružnica daná stredom a bodom"), "icon": "circle_center_point"},
            {"name": _("Kružnica daná stredom a polomerom"), "icon": "circle_center_radius"},
            {"name": _("Kružnica daná polomerom a stredom"), "icon": "compass"},
            {"name": _("Kružnica daná 3 bodmi"), "icon": "circle_3_points"},
            {"name": _("Polkružnica s krajnými bodmi"), "icon": "semi_circle"},
            {"name": _("Kružnicový oblúk daný stredom a krajnými bodmi"), "icon": "circular_arc"},
            {"name": _("Kružnicový oblúk daný 3 bodmi"), "icon": "circumcircular_arc"},
            {"name": _("Kruhový výsek daný stredom a krajnými bodmi"), "icon": "circular_sector"},
            {"name": _("Kruhový výsek určený 3 bodmi"), "icon": "circumcircular_sector"},
        ],
    )
    state.selected_tool = "arrow"

    return bar