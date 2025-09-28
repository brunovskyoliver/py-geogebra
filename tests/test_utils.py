import unittest
from unittest.mock import MagicMock, patch
import math
from py_geogebra.tools.utils import (
    number_to_ascii,
    ascii_to_number,
    screen_to_world,
    world_to_screen,
    distance,
    get_label,
    get_lower_label,
    get_linear_fuction_prescription,
)


class TestUtils(unittest.TestCase):
    def test_number_to_ascii(self):
        test_cases = [
            (0, "A"),
            (1, "B"),
            (25, "Z"),
            (26, "AA"),
            (27, "AB"),
            (51, "AZ"),
            (701, "ZZ"),
        ]
        for number, expected in test_cases:
            with self.subTest(number=number):
                self.assertEqual(number_to_ascii(number), expected)

    def test_ascii_to_number(self):
        test_cases = [
            ("A", 0),
            ("B", 1),
            ("Z", 25),
            ("AA", 26),
            ("AB", 27),
            ("AZ", 51),
            ("ZZ", 701),
        ]
        for ascii, expected in test_cases:
            with self.subTest(ascii=ascii):
                self.assertEqual(ascii_to_number(ascii), expected)

    def test_ascii_number_roundtrip(self):
        for i in range(1000):
            with self.subTest(i=i):
                ascii = number_to_ascii(i)
                number = ascii_to_number(ascii)
                self.assertEqual(i, number)

    @patch("py_geogebra.tools.utils.g")
    def test_screen_to_world(self, mock_g):
        mock_g.return_value.objects.unit_size = 50
        mock_g.return_value.objects.scale = 1

        mock_event = MagicMock()
        mock_event.x = 100
        mock_event.y = 100

        with patch("py_geogebra.tools.utils.state") as mock_state:
            mock_state.center = (50, 50)

            world_x, world_y = screen_to_world(mock_event)

            expected_x = (100 - 50) / 50
            expected_y = (50 - 100) / 50

            self.assertAlmostEqual(world_x, expected_x)
            self.assertAlmostEqual(world_y, expected_y)

    @patch("py_geogebra.tools.utils.g")
    def test_world_to_screen(self, mock_g):
        mock_g.return_value.objects.unit_size = 50
        mock_g.return_value.objects.scale = 1

        with patch("py_geogebra.tools.utils.state") as mock_state:
            mock_state.center = (50, 50)

            screen_x, screen_y = world_to_screen(1, 1)

            expected_x = 50 + 1 * 50 * 1
            expected_y = 50 - 1 * 50 * 1

            self.assertAlmostEqual(screen_x, expected_x)
            self.assertAlmostEqual(screen_y, expected_y)

    def test_distance(self):
        test_cases = [
            ((0, 0, 3, 4), 5),
            ((0, 0, 1, 1), math.sqrt(2)),
            ((1, 1, 1, 1), 0),
            ((-1, -1, 1, 1), 2 * math.sqrt(2)),
        ]
        for (x1, y1, x2, y2), expected in test_cases:
            with self.subTest(points=f"({x1},{y1})->({x2},{y2})"):
                self.assertAlmostEqual(distance(x1, y1, x2, y2), expected)

    def test_get_linear_function_prescription(self):
        test_cases = [
            ((0, 0, 1, 1), (1, -1, 0)),
            ((0, 0, 1, 2), (2, -1, 0)),
            ((1, 1, 3, 1), (0, -2, -2)),
            ((0, 1, 2, 1), (0, -2, -2)),
            ((-1, -1, 1, 1), (2, -2, 0)),
        ]
        for (x1, y1, x2, y2), expected in test_cases:
            with self.subTest(points=f"({x1},{y1})->({x2},{y2})"):
                result = get_linear_fuction_prescription(x1, y1, x2, y2)
                self.assertEqual(
                    result,
                    expected,
                    f"For line through ({x1},{y1})->({x2},{y2}), "
                    f"expected {expected} but got {result}",
                )

    @patch("py_geogebra.tools.utils.state")
    def test_get_label(self, mock_state):
        mock_state.label_unused = ["B", "C"]
        mock_state.label_counter = 0

        label = get_label(mock_state)
        self.assertEqual(label, "B")
        self.assertEqual(mock_state.label_unused, ["C"])

        mock_state.label_unused = []
        mock_state.label_counter = 0

        label = get_label(mock_state)
        self.assertEqual(label, "A")
        self.assertEqual(mock_state.label_counter, 1)

    @patch("py_geogebra.tools.utils.state")
    def test_get_lower_label(self, mock_state):
        mock_state.lower_label_unused = ["b", "c"]
        mock_state.lower_label_counter = 0

        label = get_lower_label(mock_state)
        self.assertEqual(label, "b")
        self.assertEqual(mock_state.lower_label_unused, ["c"])

        mock_state.lower_label_unused = []
        mock_state.lower_label_counter = 0

        label = get_lower_label(mock_state)
        self.assertEqual(label, "a")
        self.assertEqual(mock_state.lower_label_counter, 1)


if __name__ == "__main__":
    unittest.main()
