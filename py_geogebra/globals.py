import tkinter
from typing import TYPE_CHECKING, Optional
from tkinter import Canvas, Frame

from py_geogebra.tools import widgets

if TYPE_CHECKING:
    from .tools.objects import Objects
    from .ui.axes import Axes
    from .ui.sidebar import Sidebar
    from .tools.widgets import Widgets

objects: Optional["Objects"] = None
axes: Optional["Axes"] = None
sidebar: Optional["Sidebar"] = None
canvas: Optional[Canvas] = None
main_area: Optional[Frame] = None
widgets: Optional["Widgets"] = None
