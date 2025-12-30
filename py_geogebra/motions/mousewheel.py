from threading import stack_size
from .. import state
from ..tools.utils import center, center_screen, screen_to_world, world_to_screen
from .. import globals


def scrolling(root):
    global _zoom
    zoom = Zoom()

    def on_scroll(e):
        zoom.on_scroll(e)

    root.bind_all("<MouseWheel>", on_scroll)


class Zoom:
    def __init__(self):
        self.canvas = globals.canvas
        self.objects = globals.objects

        self.target_scale = state.scale
        self.animating = False

        self.anchor_x = 0
        self.anchor_y = 0

        self.smoothness = 0.2
        self.delay = 10

        self.diff_x = 0
        self.diff_y = 0



    def on_scroll(self, e):
        cx,cy = center()
        factor = 1.1 if e.delta > 0 else (1 / 1.1)

        self.target_scale *= factor
        self.start_scale = state.scale

        start_x = e.x
        start_y = e.y
        diff_factor = 1 - ((self.start_scale - self.target_scale) / self.start_scale)
        target_x = ((start_x - cx) * diff_factor) + cx
        target_y = ((start_y - cy) * diff_factor) + cy
        self.diff_x = start_x - target_x
        self.diff_y = start_y - target_y


        if not self.animating:
            self.animating = True
            self.animate()





    def animate(self):
        current = state.scale
        target = self.target_scale

        new_scale = current + (target - current) * self.smoothness

        if abs(new_scale - target) < 1e-6:
            new_scale = target
            self.animating = False

        state.scale = new_scale
        self.objects.scale = new_scale


        self.objects.offset_x += self.diff_x * self.smoothness
        self.objects.offset_y += self.diff_y * self.smoothness

        self.diff_x -= self.diff_x * self.smoothness
        self.diff_y -= self.diff_y * self.smoothness

        self.objects.refresh()

        if self.animating:
            self.canvas.after(self.delay, self.animate)
