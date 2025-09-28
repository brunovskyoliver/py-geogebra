from .. import state
from ..tools.utils import delete_object


def keybinds(root, canvas, sidebar, objects, axex):
    def keypressed(e):
        if e.keysym == "BackSpace":
            if state.selected_point != None and state.selected_tool == "arrow":
                delete_object(canvas, objects, state.selected_point, state, sidebar)
        elif e.keysym == "Shift_L":
            state.shift_pressed = True

    def keyreleased(e):
        if e.keysym == "Shift_L":
            state.shift_pressed = False

    canvas.bind("<KeyPress>", keypressed)
    canvas.bind("<KeyRelease>", keyreleased)
