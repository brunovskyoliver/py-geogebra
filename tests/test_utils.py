import unittest
from unittest.mock import MagicMock, patch
import math
from types import SimpleNamespace
from py_geogebra.tools.utils import (
    delete_object,
    find_circle_at_position,
    number_to_ascii,
    ascii_to_number,
    format_angle_value,
    format_length_value,
    find_measurement_at_position,
    find_selectable_shape_at_position,
    rename_object,
    screen_vector_to_world,
    screen_to_world,
    world_vector_to_screen,
    world_to_screen,
    distance,
    get_label,
    get_lower_label,
    get_linear_fuction_prescription,
)
from py_geogebra.ui.length import Length
from py_geogebra.ui.angle import Angle
from py_geogebra.ui.point import Point
from py_geogebra.ui.regular_polygon import Regular_polygon
from py_geogebra.ui.segment import Segment
from py_geogebra.ui.sidebar import Sidebar


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

    @patch("py_geogebra.tools.utils.g")
    def test_screen_world_vector_conversion(self, mock_g):
        mock_g.return_value.objects.unit_size = 40
        mock_g.return_value.objects.scale = 2

        screen_dx, screen_dy = world_vector_to_screen(1.5, -0.5)
        self.assertAlmostEqual(screen_dx, 120)
        self.assertAlmostEqual(screen_dy, 40)

        world_dx, world_dy = screen_vector_to_world(screen_dx, screen_dy)
        self.assertAlmostEqual(world_dx, 1.5)
        self.assertAlmostEqual(world_dy, -0.5)

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

    @patch("py_geogebra.tools.utils.state")
    def test_format_helpers_respect_decimal_precision(self, mock_state):
        mock_state.length_decimal_places = 0
        mock_state.angle_decimal_places = 6

        self.assertEqual(format_length_value(12.75), "13")
        self.assertEqual(format_angle_value(45.1234567), "45.123457")

    @patch("py_geogebra.tools.utils.g")
    def test_rename_object_updates_label_and_reclaims_old_name(self, mock_g):
        point_a = Point.__new__(Point)
        point_a.label = "A"
        point_a.update = MagicMock()

        point_b = Point.__new__(Point)
        point_b.label = "B"

        mock_g.return_value.objects._objects = [point_a, point_b]
        mock_g.return_value.sidebar.update = MagicMock()

        fake_state = SimpleNamespace(
            label_unused=[],
            lower_label_unused=[],
            angle_label_unused=[],
        )

        success, error = rename_object(point_a, "c", fake_state)

        self.assertTrue(success)
        self.assertEqual(error, "")
        self.assertEqual(point_a.label, "C")
        self.assertEqual(fake_state.label_unused, ["A"])
        point_a.update.assert_called()
        mock_g.return_value.sidebar.update.assert_called()

    @patch("py_geogebra.tools.utils.g")
    def test_rename_object_rejects_invalid_and_duplicate_names(self, mock_g):
        point_a = Point.__new__(Point)
        point_a.label = "A"
        point_a.update = MagicMock()

        point_b = Point.__new__(Point)
        point_b.label = "B"

        mock_g.return_value.objects._objects = [point_a, point_b]
        mock_g.return_value.sidebar.update = MagicMock()

        fake_state = SimpleNamespace(
            label_unused=[],
            lower_label_unused=[],
            angle_label_unused=[],
        )

        success, error = rename_object(point_a, "b", fake_state)
        self.assertFalse(success)
        self.assertIn("already in use", error)
        self.assertEqual(point_a.label, "A")

        success, error = rename_object(point_a, "a1", fake_state)
        self.assertFalse(success)
        self.assertEqual(error, "Use letters only.")
        self.assertEqual(point_a.label, "A")

    @patch("py_geogebra.tools.utils.g")
    def test_rename_lower_label_updates_linked_measurements(self, mock_g):
        point_1 = SimpleNamespace(label="A")
        point_2 = SimpleNamespace(label="B")

        owner = SimpleNamespace(
            lower_label="a",
            owns_label=True,
            point_1=point_1,
            point_2=point_2,
            update=MagicMock(),
            lower_label_obj=SimpleNamespace(update=MagicMock()),
        )
        linked_length = Length.__new__(Length)
        linked_length.point_1 = point_1
        linked_length.point_2 = point_2
        linked_length.owns_label = False
        linked_length.lower_label = "a"
        linked_length.update = MagicMock()

        mock_g.return_value.objects._objects = [owner, linked_length]
        mock_g.return_value.sidebar.update = MagicMock()

        fake_state = SimpleNamespace(
            label_unused=[],
            lower_label_unused=[],
            angle_label_unused=[],
        )

        success, error = rename_object(owner, "b", fake_state)

        self.assertTrue(success)
        self.assertEqual(error, "")
        self.assertEqual(owner.lower_label, "b")
        self.assertEqual(linked_length.lower_label, "b")
        linked_length.update.assert_called()
        owner.lower_label_obj.update.assert_called()

    @patch("py_geogebra.tools.utils.g")
    def test_find_measurement_at_position_prefers_measurement_tags(self, mock_g):
        class FakeLength:
            def __init__(self, tag):
                self.tag = tag

        class FakeLine:
            def __init__(self, tag):
                self.tag = tag

        event = MagicMock()
        event.x = 10
        event.y = 20

        measurement = FakeLength("length_123")
        non_measurement = FakeLine("line_123")

        mock_canvas = MagicMock()
        mock_canvas.find_overlapping.return_value = [1]
        mock_canvas.gettags.return_value = ("length_123",)

        mock_g.return_value.canvas = mock_canvas
        mock_g.return_value.objects._objects = [non_measurement, measurement]

        with patch("py_geogebra.ui.length.Length", FakeLength):
            with patch("py_geogebra.ui.area.Area", type("FakeArea", (), {})):
                with patch("py_geogebra.ui.slope.Slope", type("FakeSlope", (), {})):
                    result = find_measurement_at_position(event)

        self.assertIs(result, measurement)

    @patch("py_geogebra.tools.utils.g")
    def test_find_selectable_shape_at_position_matches_lower_label(self, mock_g):
        event = MagicMock()
        event.x = 25
        event.y = 30

        shape = MagicMock()
        shape.tag = "shape_1"
        shape.lower_label_obj = MagicMock(tag="shape_1_label")
        shape.select = MagicMock()

        mock_canvas = MagicMock()
        mock_canvas.find_overlapping.return_value = [1]
        mock_canvas.gettags.return_value = ("shape_1_label",)

        mock_g.return_value.canvas = mock_canvas
        mock_g.return_value.objects._objects = [shape]

        result = find_selectable_shape_at_position(event)

        self.assertIs(result, shape)

    @patch("py_geogebra.tools.utils.g")
    def test_find_circle_at_position_supports_circular_sector(self, mock_g):
        event = MagicMock()
        event.x = 12
        event.y = 16

        sector = MagicMock()
        sector.tag = "circular_sector_1"

        mock_canvas = MagicMock()
        mock_canvas.find_overlapping.return_value = [1]
        mock_canvas.gettags.return_value = ("circular_sector_1",)

        mock_g.return_value.canvas = mock_canvas
        mock_g.return_value.objects._objects = [sector]

        result = find_circle_at_position(event)

        self.assertIs(result, sector)

    def test_sidebar_uses_regular_polygon_lower_label(self):
        sidebar = Sidebar.__new__(Sidebar)
        point_a = Point.__new__(Point)
        point_a.label = "A"
        point_b = Point.__new__(Point)
        point_b.label = "B"

        polygon = Regular_polygon.__new__(Regular_polygon)
        polygon.lower_label = "p"
        polygon.length = 12.345
        polygon.line_points = [point_a, point_b]
        polygon.num_points = 5

        text = Sidebar._item_text(sidebar, polygon)

        self.assertTrue(text.startswith("p = Polygon("))
        self.assertNotIn("poly1", text)

    def test_sidebar_precision_controls_match_object_type(self):
        sidebar = Sidebar.__new__(Sidebar)
        point = Point.__new__(Point)
        angle = Angle.__new__(Angle)
        segment = Segment.__new__(Segment)

        self.assertFalse(Sidebar._shows_length_precision(sidebar, point))
        self.assertFalse(Sidebar._shows_angle_precision(sidebar, point))
        self.assertTrue(Sidebar._shows_length_precision(sidebar, segment))
        self.assertFalse(Sidebar._shows_angle_precision(sidebar, segment))
        self.assertFalse(Sidebar._shows_length_precision(sidebar, angle))
        self.assertTrue(Sidebar._shows_angle_precision(sidebar, angle))

    @patch("py_geogebra.tools.utils.g")
    def test_delete_object_removes_attached_dependents_and_label_object(self, mock_g):
        class FakeObjects:
            def __init__(self, registered):
                self._objects = list(registered)

            def unregister(self, obj):
                if obj in self._objects:
                    self._objects.remove(obj)

            def refresh(self):
                return None

        class FakeSidebar:
            def __init__(self, items):
                self.items = list(items)

            def update(self):
                return None

        class FakeObject:
            def __init__(self, tag, lower_label=""):
                self.tag = tag
                self.lower_label = lower_label

        state = MagicMock()
        state.points_for_obj = []
        state.selected_point = None
        state.drag_target = None
        state.selected_intersect_line_1 = None
        state.lower_label_unused = []
        state.label_unused = []
        state.angle_label_unused = []

        line = FakeObject("line_1", lower_label="l")
        line.lower_label_obj = FakeObject("line_1_label")
        attached_point = FakeObject("point_1")
        attached_point.parent_line = line

        canvas = MagicMock()
        sidebar = FakeSidebar([line, attached_point])
        objects = FakeObjects([line.lower_label_obj, line, attached_point])

        mock_g.return_value.canvas = canvas
        mock_g.return_value.sidebar = sidebar
        mock_g.return_value.objects = objects

        state.selected_point = line
        state.drag_target = line

        delete_object(line, state)

        self.assertEqual(objects._objects, [])
        self.assertEqual(sidebar.items, [])
        self.assertIn("l", state.lower_label_unused)
        canvas.delete.assert_any_call("line_1")
        canvas.delete.assert_any_call("line_1_label")
        canvas.delete.assert_any_call("point_1")
        self.assertIsNone(state.selected_point)
        self.assertIsNone(state.drag_target)

    @patch("py_geogebra.tools.utils.g")
    def test_delete_object_preserves_geometry_when_deleting_measurement(self, mock_g):
        class FakeObjects:
            def __init__(self, registered):
                self._objects = list(registered)

            def unregister(self, obj):
                if obj in self._objects:
                    self._objects.remove(obj)

            def refresh(self):
                return None

        point_1 = SimpleNamespace(tag="point_a")
        point_2 = SimpleNamespace(tag="point_b")
        segment = SimpleNamespace(tag="segment_1", point_1=point_1, point_2=point_2, lower_label="a")
        length = SimpleNamespace(
            tag="length_1",
            lower_label="d",
            point_1=point_1,
            point_2=point_2,
            owns_label=True,
        )

        canvas = MagicMock()
        sidebar = SimpleNamespace(items=[segment, length], selected_item=length, update=MagicMock(), show_item=MagicMock())
        objects = FakeObjects([segment, length])
        fake_state = SimpleNamespace(
            points_for_obj=[],
            selected_point=length,
            drag_target=None,
            selected_intersect_line_1=None,
            lower_label_unused=[],
            label_unused=[],
            angle_label_unused=[],
        )

        mock_g.return_value.canvas = canvas
        mock_g.return_value.sidebar = sidebar
        mock_g.return_value.objects = objects

        delete_object(length, fake_state)

        self.assertEqual(objects._objects, [segment])
        self.assertEqual(sidebar.items, [segment])
        self.assertIn("d", fake_state.lower_label_unused)
        sidebar.show_item.assert_called_with(None)

    @patch("py_geogebra.tools.utils.g")
    def test_delete_object_cleans_partial_construction_points_for_obj(self, mock_g):
        class FakeObjects:
            def __init__(self, registered):
                self._objects = list(registered)

            def unregister(self, obj):
                if obj in self._objects:
                    self._objects.remove(obj)

            def refresh(self):
                return None

        point = SimpleNamespace(tag="point_1", label="A")
        temp_segment = SimpleNamespace(tag="segment_1", lower_label="a")

        canvas = MagicMock()
        sidebar = SimpleNamespace(items=[temp_segment], selected_item=None, update=MagicMock(), show_item=MagicMock())
        objects = FakeObjects([point, temp_segment])
        fake_state = SimpleNamespace(
            points_for_obj=[point, temp_segment],
            selected_point=None,
            drag_target=None,
            selected_intersect_line_1=None,
            lower_label_unused=[],
            label_unused=[],
            angle_label_unused=[],
        )

        mock_g.return_value.canvas = canvas
        mock_g.return_value.sidebar = sidebar
        mock_g.return_value.objects = objects

        delete_object(point, fake_state)

        self.assertEqual(fake_state.points_for_obj, [])
        self.assertEqual(objects._objects, [])
        canvas.delete.assert_any_call("segment_1")


if __name__ == "__main__":
    unittest.main()
