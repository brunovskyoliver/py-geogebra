from .pressing import pressing
from .dragging import dragging
from .mousewheel import scrolling
from .keybinds import keybinds
from .motion import motion
from .changing_screen_size import changing_screen_size


def bind_all(root):
    pressing(root)
    dragging(root)
    scrolling(root)
    motion(root)
    keybinds(root)
    changing_screen_size(root)
