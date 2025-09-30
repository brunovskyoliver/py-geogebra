import json
from .. import state
from ..tools.utils import delete_object
from .. import globals
from ..ui.dialogs import save_file, open_from_file


def keybinds(root):
    def keypressed(e):
        is_command = (e.state & 8) != 0

        if e.keysym == "BackSpace":
            if state.selected_point is not None and state.selected_tool == "arrow":
                delete_object(state.selected_point, state)

        elif e.keysym == "Shift_L":
            state.shift_pressed = True

        elif e.keysym.lower() == "s" and is_command:
            save_file(root)
        elif e.keysym.lower() == "o" and is_command:
            open_from_file(root)

    def keyreleased(e):
        if e.keysym == "Shift_L":
            state.shift_pressed = False

    root.bind("<KeyPress>", keypressed)
    root.bind("<KeyRelease>", keyreleased)
