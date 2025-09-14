from .pressing import pressing
from .dragging import dragging


def bind_all(canvas, offsets):
    pressing(canvas, offsets)
    dragging(canvas, offsets)
