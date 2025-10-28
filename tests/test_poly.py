import unittest
from pathlib import Path

from pygeoif.geometry import Point, Polygon

from common.poly import parse_poly_file
from common.poly import PolyFileIncorrectFiletypeException


class TestPoly(unittest.TestCase):
    def test_wrong_format(self):
        """
        Test that it can recognize a proper filetype
        """
        with self.assertRaises(PolyFileIncorrectFiletypeException) as cm:
            poly = parse_poly_file(Path('tests/test_poly/wrong_format.poly'))

        self.assertEqual(str(cm.exception), 'Expecting polygon filetype, got "not-polygon" instead')

    def test_pomorskie(self):
        """
        Test that it can load properly formatted POLY file
        """
        poly = parse_poly_file(Path('tests/test_poly/pomorskie.poly'))
        self.assertEqual(1, len(list(poly.geoms)))

        pomorskie: Polygon = next(poly.geoms)

        self.assertEqual(213, len(pomorskie.exterior.geoms))
        self.assertEqual(Point(16.68, 54.58), pomorskie.exterior.geoms[0])
        self.assertEqual(Point(18.355, 53.665), pomorskie.exterior.geoms[100])
        self.assertEqual(Point(16.8, 54.39), pomorskie.exterior.geoms[200])
        self.assertEqual(Point(16.68, 54.58), pomorskie.exterior.geoms[212])
        
    def test_bounding_box(self):
        """
        Test that bounding box is properly calculated
        """
        poly = parse_poly_file(Path('tests/test_poly/pomorskie.poly'))
        self.assertEqual((16.68, 53.47, 19.67, 54.855), poly.bounds)


if __name__ == '__main__':
    unittest.main()