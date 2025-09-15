from .. import state
from ..tools.utils import center


def scrolling(root, canvas, objects):
    zoom = Zoom(canvas, objects)

    def scroll(e):
        scale_before = state.scale
        scale_factor = 1.1 if e.delta > 0 else 1/1.1
        scale_after = scale_before * scale_factor

        cx, cy = center(canvas, objects)

        state.scale = scale_after
        
        pos_x = (e.x - cx) / (objects.unit_size * objects.scale)
        pos_y = (cy - e.y) / (objects.unit_size * objects.scale)
        
        x = cx + pos_x * objects.unit_size * objects.scale
        y = cy - pos_y * objects.unit_size * objects.scale

        offset_x_after = ((cx - x)*scale_factor) - (cx - x)
        offset_y_after = ((cy - y)*scale_factor) - (cy - y)
        
        # objects.offset_x += offset_x_after
        # objects.offset_y += offset_y_after
        # objects.refresh()


        zoom.smooth_zoom(scale_before, scale_after, offset_x_after, offset_y_after)
        
    root.bind_all("<MouseWheel>", scroll)
        
    
    
class Zoom:
    def __init__(self, canvas, objects):
        self.canvas = canvas
        self.objects = objects
        self.animation_id = None
        self.target_scale = None
        self.steps = 10
        self.delay = 2

    def smooth_zoom(self, zoom_start, zoom_end, offset_x_end, offset_y_end):
        if self.animation_id is not None:
            self.canvas.after_cancel(self.animation_id)
            self.animation_id = None

        self.target_scale = zoom_end
        diff = (zoom_end - zoom_start) / self.steps
        x_diff = (offset_x_end) / self.steps
        y_diff = (offset_y_end) / self.steps


        def step(i=0, current = zoom_start):
            if i > self.steps:
                self.objects.scale = self.target_scale
                self.objects.refresh()
                return


            self.objects.scale = current
            self.objects.offset_x += x_diff
            self.objects.offset_y += y_diff

            self.objects.refresh()

            self.animation_id = self.canvas.after(self.delay, step, i+1, current + diff)

        step()
