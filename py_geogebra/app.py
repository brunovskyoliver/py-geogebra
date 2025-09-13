import tkinter as tk
from tkinter import ttk
from .language import set_language
from .widgets import Widgets


def change_lang(lang: str):
    global _
    assert _ != None
    _ = set_language(lang)
    widgets.refresh()


def run_app():
    global _, widgets
    _ = set_language(
        "sk"
    )  # musi to byt _ - dont ask questions you dont want answers to
    widgets = Widgets()

    root = tk.Tk()
    root.geometry("1280x720")  # TODO: make it dynamic ?
    widgets.register(lambda: root.title(_("Geogebra ale lepsia")))

    menu_bar = tk.Menu(root)
    language_selection = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label=_("Language"), menu=language_selection)
    language_selection.add_command(label="Slovenský", command=lambda: change_lang("sk"))
    language_selection.add_command(label="Anglický", command=lambda: change_lang("en"))

    root.config(menu=menu_bar)
    root.mainloop()
