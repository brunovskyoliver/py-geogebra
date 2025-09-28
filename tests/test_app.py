import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch
from py_geogebra.app import run_app
import builtins
from py_geogebra import globals
from py_geogebra.tools.widgets import Widgets
from py_geogebra.tools.objects import Objects
from py_geogebra.ui.axes import Axes
from py_geogebra.ui.toolbar import tool_menu_init


def _(text):
    return text


builtins._ = _


class TestApp(unittest.TestCase):
    @patch("py_geogebra.ui.toolbar.tool_menu_init")
    @patch("tkinter.Tk")
    @patch("py_geogebra.app.set_language")
    def test_app_initialization(self, mock_set_language, mock_tk, mock_tool_menu):
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        mock_canvas = MagicMock()
        mock_canvas.winfo_width.return_value = 1280
        mock_canvas.winfo_height.return_value = 720

        with patch("tkinter.Canvas", return_value=mock_canvas):
            with patch("tkinter.Frame") as mock_frame:
                mock_root.mainloop = MagicMock()
                run_app()

                mock_set_language.assert_called_once_with("sk")
                mock_root.geometry.assert_called_once_with("1280x720")

                self.assertTrue(mock_root.config.called)

                self.assertEqual(mock_canvas.pack.call_count, 1)

                self.assertIsNotNone(globals.canvas)
                self.assertIsNotNone(globals.objects)
                self.assertIsNotNone(globals.sidebar)
                self.assertIsNotNone(globals.axes)

    def test_widgets_registration(self):
        widgets = Widgets()
        callback = MagicMock()
        widgets.register(callback)
        callback.assert_called_once()
        widgets.refresh()
        self.assertEqual(callback.call_count, 2)

    @patch("tkinter.Tk")
    def test_objects_initialization(self, mock_tk):
        objects = Objects()
        self.assertEqual(objects.offset_x, 0)
        self.assertEqual(objects.offset_y, 0)
        self.assertEqual(objects.unit_size, 40)
        self.assertEqual(len(objects._objects), 0)


if __name__ == "__main__":
    unittest.main()
