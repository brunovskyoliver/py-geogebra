import tkinter as tk
from tkinter import Canvas, ttk

from .tools.language import set_language
from .tools.language import change_lang
from .tools.widgets import Widgets
from .ui.menu_bar import menu
from .ui.toolbar import toolbar
from .config import __version__
from .tools.objects import Objects
from .ui.axes import Axes
from py_geogebra.motions import motions
from . import state
from .ui.sidebar import Sidebar


def run_app():
    global widgets
    set_language("sk")
    widgets = Widgets()

    root = tk.Tk()
    root.geometry("1280x720")
    widgets.register(lambda: root.title(_("Geogebra ale lepsia") + f" v{__version__}"))

    main_area = tk.Frame(root)
    sidebar = Sidebar(root, main_area, widgets)
    sidebar = sidebar.frame
    canvas = tk.Canvas(main_area, background="white")
    objects = Objects(canvas)
    tool_bar = toolbar(root, canvas, widgets, objects)
    tool_bar.pack(side="top", fill="x")
    main_area.pack(side="top", fill="both", expand=True)
    sidebar.pack(side="left", fill="y")
    canvas.pack(side="right", fill="both", expand=True)
    root.update_idletasks()
    state.center = (
        canvas.winfo_width() // 2 + objects.offset_x,
        canvas.winfo_height() // 2 + objects.offset_y,
    )
    state.sidebar_width = sidebar.winfo_width()

    axes = Axes(root, canvas, objects.unit_size)
    objects.register(axes)
    motions.bind_all(root, canvas, sidebar, objects, axes)
    canvas.focus_set()
    menu_bar = menu(root, widgets, canvas, objects)
    root.config(menu=menu_bar)

    root.mainloop()
