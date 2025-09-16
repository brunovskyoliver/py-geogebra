from .. import state


def changing_screen_size(root, canvas, sidebar, objects):
    def refrershing_canvas(e):
        cx = e.width // 2 + objects.offset_x
        cy = e.height // 2 + objects.offset_y
        state.center = (cx, cy)
        objects.refresh()

    def refrershing_sidebar(e):
        state.sidebar_width = e.width

    canvas.bind("<Configure>", refrershing_canvas)
    sidebar.frame.bind("<Configure>", refrershing_canvas)
