from tkinter import Canvas
from .tools.objects import Objects
from .ui.axes import Axes
from .ui.sidebar import Sidebar

objects: Objects | None = None
axes: Axes | None = None
sidebar: Sidebar | None = None
canvas: Canvas | None = None
