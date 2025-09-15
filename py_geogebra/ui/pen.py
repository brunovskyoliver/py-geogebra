import tkinter as tk


class Pen:
    def __init__(self, root: tk.Tk, canvas: tk.Canvas, unit_size: int = 40):
        self.root = root
        self.canvas = canvas

        self.pos_x = 0.0
        self.pos_y = 0.0

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0  # zoom factor
        self.unit_size = unit_size

        self.canvas.bind("<Configure>", lambda e: self.update())

    def update(self):
        self.canvas.delete("pen")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        cx = width // 2 + self.offset_x
        cy = height // 2 + self.offset_y

        x = cx + self.pos_x * self.unit_size * self.scale
        y = cy - self.pos_y * self.unit_size * self.scale

        visual_scale = min(max(1, self.scale**0.5), 1.9)

        r = 6.0 * visual_scale

        self.canvas.create_oval(
            x - r, y - r, x + r, y + r, fill="black", width=2, tags="pen"
        )
