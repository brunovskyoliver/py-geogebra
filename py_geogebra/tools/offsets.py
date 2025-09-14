import tkinter as tk
from .objects import Objects
from ..ui.axes import Axes


class Offsets:
    def __init__(self, root: tk.Tk, canvas: tk.Canvas):
        self.root = root
        self.canvas = canvas
        self.objects = Objects()
        self.axes = Axes(root, canvas)
        
        self.objects.register(self.axes)
        

        
        self.offset_x = 0
        self.offset_y = 0
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.scale = 1.0

        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.do_pan)
        
        self.canvas.bind("<MouseWheel>", self.zoom)          # Windows / MacOS
        self.canvas.bind("<Button-4>", self.zoom_linux)      # Linux scroll up
        self.canvas.bind("<Button-5>", self.zoom_linux)      # Linux scroll down
        


    def start_pan(self, event):
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def do_pan(self, event):
        dx = event.x - self.pan_start_x
        dy = event.y - self.pan_start_y
        self.offset_x += dx
        self.offset_y += dy
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        
        self.objects.offset_x = self.offset_x
        self.objects.offset_y = self.offset_y
        self.objects.refresh()
        
    def zoom(self, event):
        if event.delta > 0:   # zoom in
            self.scale *= 1.1
        else:                 # zoom out
            self.scale /= 1.1


    def zoom_linux(self, event):
        if event.num == 4:    # scroll up
            self.scale *= 1.1
        elif event.num == 5:  # scroll down
            self.scale /= 1.1
