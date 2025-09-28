import json
from .. import state
from ..tools.utils import delete_object
from .. import globals


def keybinds(root):
    def keypressed(e):
        is_command = (e.state & 8) != 0

        if e.keysym == "BackSpace":
            if state.selected_point is not None and state.selected_tool == "arrow":
                delete_object(state.selected_point, state)

        elif e.keysym == "Shift_L":
            state.shift_pressed = True

        elif e.keysym.lower() == "s" and is_command:
            globals.objects.to_json("scene_full.json")
            print("saved")
        elif e.keysym.lower() == "l" and is_command:
            with open("scene_full.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            globals.objects.load_from_dict(root, data)
            print("loaded")

    def keyreleased(e):
        if e.keysym == "Shift_L":
            state.shift_pressed = False

    root.bind("<KeyPress>", keypressed)
    root.bind("<KeyRelease>", keyreleased)
