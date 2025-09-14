import tkinter as tk
from tkinter import ttk
from ..tools.language import change_lang


def menu(root, widgets):
    menu_bar = tk.Menu(root)
    language_selection = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label=_("Language"), menu=language_selection)
    language_selection.add_command(
        label="Slovenský", command=lambda: change_lang("sk", widgets)
    )
    language_selection.add_command(
        label="Anglický", command=lambda: change_lang("en", widgets)
    )
    more_selection = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label=_("Viac"), menu=more_selection)
    more_selection.add_command(
        label=_("Over verziu"), command=lambda: print("checking version...")
    )
    return menu_bar
