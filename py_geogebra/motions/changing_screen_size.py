from .. import state


def changing_screen_size(root, canvas, objects):
    def refrershing(e):
        objects.refresh()


    canvas.bind("<Configure>", refrershing)