from typing import TYPE_CHECKING, Optional
from tkinter import Canvas, Frame

if TYPE_CHECKING:
    from .tools.objects import Objects
    from .ui.axes import Axes
    from .ui.sidebar import Sidebar
    from .tools.widgets import Widgets
    from .tools.auth0_handler import Auth0Handler

objects: Optional["Objects"] = None
axes: Optional["Axes"] = None
sidebar: Optional["Sidebar"] = None
canvas: Optional[Canvas] = None
main_area: Optional[Frame] = None
widgets: Optional["Widgets"] = None
auth: Optional["Auth0Handler"] = None
