import tkinter as tk
from tkinter import messagebox


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
