from .pressing import pressing
from .dragging import dragging
from .mousewheel import scrolling
from .keybinds import keybinds
from .motion import motion
from .changing_screen_size import changing_screen_size


def bind_all(root, canvas, sidebar, objects, axes):
    pressing(root, canvas, sidebar, objects, axes)
    dragging(root, canvas, sidebar, objects, axes)
    scrolling(root, canvas, objects)
    motion(root, canvas, objects, axes)
    keybinds(root, canvas, sidebar, objects, axes)

    changing_screen_size(root, canvas, sidebar, objects)
