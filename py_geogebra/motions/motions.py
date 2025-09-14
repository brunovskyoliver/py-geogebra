from .pressing import pressing
from .dragging import dragging
from .mousewheel import scrolling


def bind_all(root, canvas, objects):
    pressing(root, canvas, objects)
    dragging(root, canvas, objects)
    scrolling(root, canvas, objects)
