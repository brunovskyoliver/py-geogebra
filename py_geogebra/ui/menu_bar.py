import tkinter as tk
import time
from tkinter import ttk, messagebox
from ..tools.language import change_lang
from ..tools.check_version import handle_version
from .dialogs import ask_for_update
from .. import globals


def run_fps_test(root):
    start = time.time()
    frames = 0

    def draw():
        nonlocal frames
        frames += 1
        # force a redraw (something light, just to trigger repaints)
        globals.objects.refresh()
        globals.canvas.update_idletasks()
        globals.canvas.update()

        if time.time() - start < 2:  # run for 2 seconds
            root.after(0, draw)
        else:
            fps = frames / 2
            print(f"Average FPS over 2s: {fps:.1f}")
            tk.messagebox.showinfo("FPS Test", f"Average FPS: {fps:.1f}")

    draw()


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
    more_cascade_index = menu_bar.index("end")
    widgets.register(lambda: menu_bar.entryconfig(more_cascade_index, label=_("Viac")))
    more_selection.add_command(
        label=_("Over verziu"),
        command=lambda: handle_version(root, widgets, ask_for_update),
    )
    check_version_index = more_selection.index("end")
    widgets.register(
        lambda: more_selection.entryconfig(check_version_index, label=_("Over verziu"))
    )

    more_selection.add_command(label=_("Test FPS"), command=lambda: run_fps_test(root))
    return menu_bar
