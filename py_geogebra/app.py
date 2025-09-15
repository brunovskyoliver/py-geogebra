import tkinter as tk
from tkinter import Canvas, ttk

from .tools.language import set_language
from .tools.language import change_lang
from .tools.widgets import Widgets
from .ui.menu_bar import menu
from .ui.sidebar import sidebar
from .config import __version__
from .tools.objects import Objects
from .ui.axes import Axes
from py_geogebra.motions import motions


def run_app():
    global widgets
    set_language("sk")
    widgets = Widgets()

    root = tk.Tk()
    root.geometry("1280x720")  # TODO: make it dynamic ?
    widgets.register(lambda: root.title(_("Geogebra ale lepsia") + f" v{__version__}"))

    menu_bar = menu(root, widgets)

    root.config(menu=menu_bar)

    canvas = Canvas(root, background="white")
    objects = Objects(canvas)
    side_bar = sidebar(root, canvas, widgets, objects)
    canvas.pack(fill="both", expand=True)
    axes = Axes(root, canvas, objects.unit_size)
    objects.register(axes)
    motions.bind_all(root, canvas, objects, axes)
    canvas.focus_set()

    root.mainloop()
