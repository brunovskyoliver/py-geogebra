from .pressing import pressing
from .dragging import dragging
from .mousewheel import scrolling
from .keybinds import keybinds
from .changing_screen_size import changing_screen_size


def bind_all(root, canvas, objects, axes):
    pressing(root, canvas, objects, axes)
    dragging(root, canvas, objects, axes)
    scrolling(root, canvas, objects)
    keybinds(root, canvas, objects, axes)
    changing_screen_size(root, canvas, objects)
