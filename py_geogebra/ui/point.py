import tkinter as tk


class Point:
    def __init__(self, root: tk.Tk, canvas: tk.Canvas, label: str = ""):
        self.root = root
        self.canvas = canvas

        self.pos_x = 0.0
        self.pos_y = 0.0
        self.label = label

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0  # zoom factor
        self.unit_size = 20  # pixels per unit at scale=1

        self.tag = f"point_{id(self)}"

        self.canvas.bind("<Configure>", lambda e: self.update())

    def update(self):
        self.canvas.delete(self.tag)

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        cx = width // 2 + self.offset_x
        cy = height // 2 + self.offset_y

        x = cx + self.pos_x * self.unit_size * self.scale
        y = cy - self.pos_y * self.unit_size * self.scale

        r = 3. * self.scale
        self.canvas.create_oval(
            x - r, y - r, x + r, y + r, fill="blue", width=2, tags=(self.tag, "point")
        )
        if self.label:
            self.canvas.create_text(
                x + 5 * self.scale,
                y - 10 * self.scale,
                text=self.label,
                font=("Arial", int(12 * self.scale)),
                fill="blue",
                tags=self.tag,
            )
