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
import json
from . import globals


def run_app():
    global widgets
    set_language("sk")
    widgets = Widgets()
    globals.widgets = widgets

    root = tk.Tk()
    root.geometry("1280x720")
    widgets.register(lambda: root.title(_("Geogebra ale lepsia") + f" v{__version__}"))

    main_area = tk.Frame(root)
    sidebar = Sidebar(root, main_area)
    globals.sidebar = sidebar
    canvas = tk.Canvas(main_area, background="white")
    globals.canvas = canvas
    objects = Objects()
    globals.objects = objects
    tool_bar = toolbar(root)
    tool_bar.pack(side="top", fill="x")
    main_area.pack(side="top", fill="both", expand=True)
    sidebar.frame.pack(side="left", fill="y")
    canvas.pack(side="right", fill="both", expand=True)
    root.update_idletasks()
    state.center = (
        canvas.winfo_width() // 2 + objects.offset_x,
        canvas.winfo_height() // 2 + objects.offset_y,
    )

    axes = Axes(root, objects.unit_size)
    globals.axes = axes
    objects.register(axes)
    motions.bind_all(root)
    canvas.focus_set()
    menu_bar = menu(root, widgets)
    root.config(menu=menu_bar)
    state.shift_pressed = False

    root.mainloop()
