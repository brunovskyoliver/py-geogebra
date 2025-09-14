import tkinter as tk


class Point:
    def __init__(self, root: tk.Tk, canvas: tk.Canvas):
        self.root = root
        self.canvas = canvas

        self.pos_x = 0.0
        self.pos_y = 0.0

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0  # zoom factor
        self.unit_size = 20  # pixels per unit at scale=1

        self.tag = f"point_{id(self)}"

        self.canvas.bind("<Configure>", lambda e: self.update())

    def update(self):
        self.canvas.delete(self.tag)

        x = self.pos_x + self.offset_x
        y = self.pos_y + self.offset_y

        r = 3
        self.canvas.create_oval(
            x - r, y - r, x + r, y + r, fill="blue", width=2, tags=(self.tag, "point")
        )
