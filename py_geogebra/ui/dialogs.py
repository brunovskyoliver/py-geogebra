import tkinter as tk
from tkinter import messagebox, filedialog
import sys, json, os
from .. import globals


def ask_for_update(widgets):
    ask = messagebox.askyesno(
        title=_("Dostupná aktualizácia"),
        message=_("Chcete nainštalovať najnovšiu verziu?"),
    )
    return ask


def no_need_to_update():
    messagebox.showinfo(
        title=_("Žiadna dostupná aktualizácia"), message=_("Si na najnovšej verzii")
    )


def ran_from_python(filepath):
    messagebox.showinfo(
        title=_("Nespustil si binary"), message=_(f"Binary nájdeš v {filepath}")
    )


def open_from_file(root):
    if getattr(
        sys, "frozen", False
    ):  # https://pyinstaller.org/en/stable/runtime-information.html
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    file = filedialog.askopenfile(defaultextension="json", initialdir=base_path)
    data = json.load(file)
    globals.objects.load_from_dict(root, data)


def save_file(root):
    if getattr(
        sys, "frozen", False
    ):  # https://pyinstaller.org/en/stable/runtime-information.html
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    file = filedialog.asksaveasfilename(defaultextension="json", initialdir=base_path)

    globals.objects.to_json(file)
