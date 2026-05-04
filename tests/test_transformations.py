import unittest
import builtins

from py_geogebra.tools.utils import (
    dilate_point_from_point,
    get_transform_reference_kind,
    is_transform_tool,
    reflect_point_across_line,
    reflect_point_across_point,
    rotate_point_around_point,
    translate_point_by_vector,
)


def _(text):
    return text


builtins._ = _


class TestTransformations(unittest.TestCase):
    def test_reflect_point_across_point(self):
        self.assertEqual(reflect_point_across_point(3.0, 4.0, 1.0, 2.0), (-1.0, 0.0))

    def test_translate_point_by_vector(self):
        self.assertEqual(translate_point_by_vector(1.5, -2.0, 3.0, 4.5), (4.5, 2.5))

    def test_rotate_point_around_point(self):
        x, y = rotate_point_around_point(2.0, 0.0, 0.0, 0.0, 90.0)
        self.assertAlmostEqual(x, 0.0, places=6)
        self.assertAlmostEqual(y, 2.0, places=6)

    def test_dilate_point_from_point(self):
        self.assertEqual(dilate_point_from_point(3.0, 5.0, 1.0, 2.0, 2.0), (5.0, 8.0))

    def test_reflect_point_across_line(self):
        x, y = reflect_point_across_line(4.0, 3.0, 0.0, 0.0, 0.0, 5.0)
        self.assertAlmostEqual(x, -4.0, places=6)
        self.assertAlmostEqual(y, 3.0, places=6)

    def test_transform_tool_metadata(self):
        self.assertTrue(is_transform_tool("translate_by_vector"))
        self.assertFalse(is_transform_tool("point"))
        self.assertEqual(get_transform_reference_kind("rotate_around_point"), "point")
        self.assertEqual(get_transform_reference_kind("reflect_about_line"), "line")
        self.assertEqual(get_transform_reference_kind("translate_by_vector"), "vector")
        self.assertEqual(get_transform_reference_kind("reflect_about_circle"), "circle")


if __name__ == "__main__":
    unittest.main()
