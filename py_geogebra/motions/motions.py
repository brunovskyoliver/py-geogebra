from .pressing import pressing
from .dragging import dragging
from .mousewheel import scrolling
from .changing_screen_size import changing_screen_size


def bind_all(root, canvas, objects, axes):
    pressing(root, canvas, objects, axes)
    dragging(root, canvas, objects, axes)
    scrolling(root, canvas, objects)
    changing_screen_size(root, canvas, objects)
