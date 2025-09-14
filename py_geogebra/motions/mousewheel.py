from .. import state


def scrolling(root, canvas, objects):
    def scroll(e):
        if e.delta > 0:  # zoom in
            state.scale *= 1.1
        else:  # zoom out
            state.scale /= 1.1

        objects.scale = state.scale
        objects.refresh()

    canvas.bind("<MouseWheel>", scroll)
