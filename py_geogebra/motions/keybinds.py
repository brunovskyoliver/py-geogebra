from .. import state
from ..tools.utils import delete_object


def keybinds(root, canvas, sidebar, objects, axex):
    def keypressed(e):
        if e.keysym == "BackSpace":
            if state.selected_point != None and state.selected_tool == "arrow":
                sidebar.items.remove(state.selected_point)
                sidebar.update()
                delete_object(canvas, objects, state.selected_point, state)

    canvas.bind("<KeyPress>", keypressed)
