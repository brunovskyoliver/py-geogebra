from .. import state
from ..tools.utils import delete_object
from .. import globals


def keybinds(root):
    def keypressed(e):
        if e.keysym == "BackSpace":
            if state.selected_point != None and state.selected_tool == "arrow":
                delete_object(
                    state.selected_point,
                    state,
                )
        elif e.keysym == "Shift_L":
            state.shift_pressed = True

    def keyreleased(e):
        if e.keysym == "Shift_L":
            state.shift_pressed = False

    globals.canvas.bind("<KeyPress>", keypressed)
    globals.canvas.bind("<KeyRelease>", keyreleased)
