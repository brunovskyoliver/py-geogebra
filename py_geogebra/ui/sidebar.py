import tkinter as tk
from ..tools.load_image import load_icon


def show_menu(e, menu):
    x = e.widget.winfo_rootx()
    y = e.widget.winfo_rooty() + e.widget.winfo_height()
    menu.tk_popup(x, y)


def update_labels(items, menu):
    def _init():
        for i in items:
            menu.entryconfig(i["index"], label=_(i["name"]))

    return _init


def change_icon(img, btn):
    btn.configure(image=img)
    btn.image = img


def tool_menu_init(root, bar, widgets, def_icon, buttons):
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
            command=lambda img=icon: change_icon(img, button),
        )
        i = (
            menu.index("end") or 0
        )  # prvy je vzdy 0 a index hadze error pri prvom bez oru
        items.append({"name": b["name"], "icon": icon, "index": i})

    menu.entries = items

    button.bind("<Button-1>", lambda e, m=menu: show_menu(e, m))

    widgets.register(update_labels(items, menu))

    return button, menu


def sidebar(root, widgets):
    root.configure(bg="white")
    bar = tk.Frame(root, height=40, bg="white", bd=0, highlightthickness=0)
    bar.pack(side="top", fill="x")

    tool_menu_init(
        root,
        bar,
        widgets,
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
        widgets,
        def_icon="point",
        buttons=[
            {"name": _(_("Bod")), "icon": "point"},
            {"name": _("Bod na objekte"), "icon": "point_on_object"},
            {"name": _("Pripojiť / Odpojiť bod"), "icon": "attach_detach_point"},
            {"name": _("Priesečník"), "icon": "intersect"},
            {"name": _("Stred"), "icon": "midpoint_or_center"},
            {"name": _("Komplexné číslo"), "icon": "complex_number"},
            {"name": _("Extremum"), "icon": "extremum"},
            {"name": _("Korene"), "icon": "roots"},
        ],
    )

    return bar
