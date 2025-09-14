import tkinter as tk


class Axes:
    def __init__(self, root: tk.Tk, canvas: tk.Canvas):
        self.root = root
        self.canvas = canvas

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0      
        self.unit_size = 40    
        self.val_increase = 1.0
        self.scale_decrease = 0.0

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
        self.canvas.create_line(cx +100 * self.scale, 0, cx +100 * self.scale, height, fill="black", width=2, tags="axes")



        step = max(1, int(self.unit_size * (self.scale - self.scale_decrease)))
        width_int = int(width)
       
        
        if step > 80:
            step = 40
            self.val_increase /= 2
            self.scale_decrease = self.scale - 1
        elif step < 20:
            step = 40
            self.val_increase *= 2
            self.scale_decrease = -(1 - self.scale)
            
        print (step, self.val_increase, self.scale_decrease, self.scale)
            
            

        # X axis
        val = 0.0
        for x in range(cx, width_int, step):
            val += self.val_increase
            self.canvas.create_text(x, cy + 10, text=round(val, 4), font=("Arial", 10), tags="axes", fill="black")
        val = 0.0
        for x in range(cx, -1, -step):
            val -= self.val_increase
            self.canvas.create_text(x, cy + 10, text=round(val, 4), font=("Arial", 10), tags="axes", fill="black")

        # Y axis
        val = 0.0
        cy_int = int(cy)
        height_int = int(height)
        for y in range(cy, height_int, step):
            val += self.val_increase
            self.canvas.create_text(cx + 15, y, text=round(val, 4), font=("Arial", 10), tags="axes", fill="black")
        val = 0.0
        for y in range(cy, -1, -step):
            val -= self.val_increase
            self.canvas.create_text(cx + 15, y, text=round(val, 4), font=("Arial", 10), tags="axes", fill="black")

