import builtins
import tkinter as tk
import unittest
from unittest.mock import patch

from py_geogebra import state
from py_geogebra.tools.widgets import Widgets
from py_geogebra.ui.menu_bar import HELP_URL, menu, open_help


def _(text):
    return text


builtins._ = _


class TestMenuBar(unittest.TestCase):
    def setUp(self):
        state.shift_pressed = False
        self.root = tk.Tk()
        self.root.withdraw()
        self.widgets = Widgets()

    def tearDown(self):
        self.root.destroy()

    def test_help_menu_item_opens_manual(self):
        menu_bar = menu(self.root, self.widgets)
        more_menu = self.root.nametowidget(menu_bar.entrycget(2, "menu"))
        help_index = more_menu.index("end")

        self.assertEqual(more_menu.entrycget(help_index, "label"), "Help")

        with patch("py_geogebra.ui.menu_bar.webbrowser.open") as mock_open:
            more_menu.invoke(help_index)

        mock_open.assert_called_once_with(HELP_URL)

    def test_open_help_uses_manual_url(self):
        with patch("py_geogebra.ui.menu_bar.webbrowser.open") as mock_open:
            open_help()

        mock_open.assert_called_once_with(HELP_URL)


if __name__ == "__main__":
    unittest.main()
