from .pressing import pressing
from .dragging import dragging


def bind_all(root, canvas, objects):
    pressing(root, canvas, objects)
    dragging(root, canvas, objects)
