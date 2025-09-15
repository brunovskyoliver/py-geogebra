import tkinter as tk
import time


class FPSCounter:
    def __init__(self, canvas: tk.Canvas, x=10, y=10):
        self.canvas = canvas
        self.text_id = canvas.create_text(
            x, y,
            text="FPS: 0",
            anchor="nw",  # north-west (top-left)
            font=("Arial", 12),
            fill="black"
        )

        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0

        self.update_fps()

    def tick(self):
        """Call this inside your refresh() or animation steps."""
        self.frame_count += 1

    def update_fps(self):
        now = time.time()
        elapsed = now - self.last_time
        if elapsed >= 1.0:  # update once per second
            self.fps = self.frame_count / elapsed
            self.canvas.itemconfig(self.text_id, text=f"FPS: {self.fps:.1f}")
            self.frame_count = 0
            self.last_time = now

        self.canvas.after(100, self.update_fps)  # update check every 100ms