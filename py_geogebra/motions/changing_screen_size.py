from .. import state
from .. import globals


def changing_screen_size(root):
    def refrershing_canvas(e):
        cx = e.width // 2 + globals.objects.offset_x
        cy = e.height // 2 + globals.objects.offset_y
        state.center = (cx, cy)
        globals.objects.refresh()
        globals.axes.update()

    def refrershing_sidebar(e):
        state.sidebar_width = e.width

    globals.canvas.bind("<Configure>", refrershing_canvas)
    globals.sidebar.frame.bind("<Configure>", refrershing_canvas)
