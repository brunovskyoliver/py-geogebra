from .. import state


def scrolling(root, canvas, objects):
    zoom = Zoom(canvas, objects)
    def scroll(e):
        scale_before = state.scale
        if e.delta > 0:  # zoom in
            state.scale *= 1.1
        else:  # zoom out
            state.scale /= 1.1
        zoom.smooth_zoom(scale_before, state.scale)


    canvas.bind("<MouseWheel>", scroll)
    
    
class Zoom:
    def __init__(self, canvas, objects):
        self.canvas = canvas
        self.objects = objects
        self.animation_id = None
        self.target_scale = None
        self.steps = 10
        self.delay = 10

    def smooth_zoom(self, start, end):
        if self.animation_id is not None:
            self.canvas.after_cancel(self.animation_id)
            self.animation_id = None

        self.target_scale = end
        diff = (end - start) / self.steps

        def step(i=0, current = start):
            if i > self.steps:
                self.objects.scale = self.target_scale
                self.objects.refresh()
                return


            self.objects.scale = current
            self.objects.refresh()

            self.animation_id = self.canvas.after(self.delay, step, i+1, current + diff)

        step()
