import tkinter as tk


class FreeHand:
    def __init__(self, root: tk.Tk, canvas: tk.Canvas):
        self.root = root
        self.canvas = canvas

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0
        self.unit_size = 40
        self.pos_x1 = 0
        self.pos_y1 = 0
        self.pos_x2 = 0
        self.pos_y2 = 0
        self.cx = 0
        self.cy = 0


        self.tag = f"freehand_{id(self)}"


    def update(self):
        self.canvas.delete(self.tag)

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        
        x1 = self.cx + self.pos_x1 * self.unit_size * self.scale
        y1 = self.cy - self.pos_y1 * self.unit_size * self.scale
        x2 = self.cx + self.pos_x2 * self.unit_size * self.scale
        y2 = self.cy - self.pos_y2 * self.unit_size * self.scale
        
        self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2, tags=self.tag)