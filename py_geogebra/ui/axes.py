import tkinter as tk


class Axes:
    def __init__(self, root: tk.Tk, canvas: tk.Canvas):
        self.root = root
        self.canvas = canvas

        self.offset_x = 0.0
        self.offset_y = 0.0


        self.canvas.bind("<Configure>", lambda e: self.update())

    def update(self):
        self.canvas.delete("axes")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # center with offset
        cx = width // 2 + self.offset_x
        cy = height // 2 + self.offset_y

        # draw axes (scaled)
        self.canvas.create_line(0, cy, width, cy, fill="black", width=2, tags="axes")
        self.canvas.create_line(cx, 0, cx, height, fill="black", width=2, tags="axes")

