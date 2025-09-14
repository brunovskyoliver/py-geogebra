import tkinter as tk


class Axes:
    def __init__(self, root: tk.Tk, canvas: tk.Canvas):
        self.root = root
        self.canvas = canvas

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0       # zoom factor
        self.unit_size = 20    # pixels per unit at scale=1

        self.canvas.bind("<Configure>", lambda e: self.update())

    def update(self):
        self.canvas.delete("axes")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        cx = width // 2 + self.offset_x
        cy = height // 2 + self.offset_y

        # draw axes
        self.canvas.create_line(0, cy, width, cy, fill="black", width=2, tags="axes")
        self.canvas.create_line(cx, 0, cx, height, fill="black", width=2, tags="axes")

        # scaled step size
        step = max(1, int(self.unit_size * self.scale))  # ensure at least 1 pixel
        cx_mod = int(cx) % step
        width_int = int(width)

        # X axis
        for x in range(cx_mod, width_int, step):
            val = (x - cx) / (self.unit_size * self.scale)
            self.canvas.create_text(x, cy + 10, text=f"{val:.0f}", font=("Arial", 10), tags="axes", fill="black")
        for x in range(cx_mod, -1, -step):
            val = (x - cx) / (self.unit_size * self.scale)
            self.canvas.create_text(x, cy + 10, text=f"{val:.0f}", font=("Arial", 10), tags="axes", fill="black")

        # Y axis
        cy_int = int(cy)
        height_int = int(height)
        for y in range(cy_int % step, height_int, step):
            val = (cy - y) / (self.unit_size * self.scale)
            self.canvas.create_text(cx + 15, y, text=f"{val:.0f}", font=("Arial", 10), tags="axes", fill="black")
        for y in range(cy_int % step, -1, -step):
            val = (cy - y) / (self.unit_size * self.scale)
            self.canvas.create_text(cx + 15, y, text=f"{val:.0f}", font=("Arial", 10), tags="axes", fill="black")

