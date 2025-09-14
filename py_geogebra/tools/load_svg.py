import os, sys
from PIL import Image, ImageTk


def get_base(*path):
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base, *path)


def load_icon(name: str, size=(48, 48)):
    path = get_base("resources", "icons", f"{name}.png")
    img = Image.open(path).resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)
