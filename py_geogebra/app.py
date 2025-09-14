import tkinter as tk
from tkinter import ttk
from .tools.language import set_language
from .tools.language import change_lang
from .tools.widgets import Widgets
from .ui.menu_bar import menu


def run_app():
    global widgets
    set_language("sk")
    widgets = Widgets()

    root = tk.Tk()
    root.geometry("1280x720")  # TODO: make it dynamic ?
    widgets.register(lambda: root.title(_("Geogebra ale lepsia")))

    menu_bar = menu(root, widgets)

    root.config(menu=menu_bar)
    root.mainloop()
