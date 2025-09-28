import unittest
import tkinter as tk
from py_geogebra.ui.toolbar import tool_menu_init, change_icon, show_menu
from py_geogebra.tools.load_image import load_icon
from py_geogebra import state, globals
from py_geogebra.tools.utils import g

import builtins


def _(text):
    return text


builtins._ = _


class MockObjects:
    def __init__(self):
        self._objects = []

    def unregister(self, obj):
        if obj in self._objects:
            self._objects.remove(obj)

    def register(self, obj):
        self._objects.append(obj)


class MockGlobals:
    def __init__(self):
        self.objects = MockObjects()
        self.canvas = None


def mock_g():
    return globals.mock_globals


class TestToolbar(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root)
        self.bar = tk.Frame(self.root)
        self.widgets = MockWidgetManager()
        self.mock_globals = MockGlobals()
        globals.mock_globals = self.mock_globals
        globals.canvas = self.canvas
        globals.widgets = self.widgets
        self.mock_globals.canvas = self.canvas
        import py_geogebra.tools.utils

        py_geogebra.tools.utils.g = mock_g
        state.selected_tool = None
        state.points_for_obj = set()
        state.current_polyline = None
        state.selected_point = None
        state.selected_intersect = None
        self.buttons = [
            {"name": "Point", "icon": "point"},
            {"name": "Line", "icon": "line"},
            {"name": "Segment", "icon": "segment"},
        ]

    def tearDown(self):
        self.root.destroy()

    def test_tool_menu_init(self):
        button, menu = tool_menu_init(self.root, self.bar, "point", self.buttons)
        self.assertIsInstance(button, tk.Button)
        self.assertTrue(hasattr(button, "image"))
        self.assertIsInstance(menu, tk.Menu)
        self.assertEqual(menu.index("end") + 1, len(self.buttons))

    def test_change_icon(self):
        btn = tk.Button(self.root)
        img = load_icon("point")
        change_icon(img, btn, "point")
        self.assertEqual(state.selected_tool, "point")
        self.assertEqual(btn.cget("image"), str(img))
        change_icon(img, btn, "pen")
        self.assertEqual(state.selected_tool, "pen")
        self.assertEqual(self.canvas.cget("cursor"), "crosshair")

    def test_change_icon_cleanup(self):
        mock_point = MockPoint()
        globals.mock_globals.objects.register(mock_point)
        state.points_for_obj = {mock_point}
        state.selected_tool = "line"
        change_icon(None, tk.Button(self.root), "point")
        self.assertEqual(len(state.points_for_obj), 0)
        self.assertEqual(state.selected_tool, "point")

    def test_show_menu(self):
        menu = tk.Menu(self.root)
        button = tk.Button(self.root)
        button.pack()
        self.root.update()

        event = type(
            "Event",
            (),
            {
                "widget": button,
            },
        )()

        show_menu(event, menu)


class MockWidgetManager:
    def register(self, callback):
        self.callback = callback


class MockPoint:
    def __init__(self):
        self.selected = False
        self.tag = "mock_point"

    def deselect(self):
        self.selected = False


if __name__ == "__main__":
    unittest.main()
