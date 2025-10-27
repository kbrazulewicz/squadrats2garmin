import unittest

from pygeoif.geometry import Point, Polygon

from common.poly import Poly
from common.poly import PolyFileIncorrectFiletypeException


class TestPoly(unittest.TestCase):
    def test_wrong_format(self):
        """
        Test that it can recognize a proper filetype
        """
        with self.assertRaises(PolyFileIncorrectFiletypeException) as cm:
            poly = Poly('tests/test_poly/wrong_format.poly')

        self.assertEqual(str(cm.exception), 'Expecting polygon filetype, got "not-polygon" instead')

    def test_pomorskie(self):
        """
        Test that it can load properly formatted POLY file
        """
        poly = Poly('tests/test_poly/pomorskie.poly')
        self.assertEqual(len(poly.coords), 1)

        pomorskie: Polygon = next(poly.coords.geoms)

        self.assertEqual(213, len(pomorskie.exterior.geoms))
        self.assertEqual(Point(16.68, 54.58), pomorskie.exterior.geoms[0])
        self.assertEqual(Point(18.355, 53.665), pomorskie.exterior.geoms[100])
        self.assertEqual(Point(16.8, 54.39), pomorskie.exterior.geoms[200])
        self.assertEqual(Point(16.68, 54.58), pomorskie.exterior.geoms[212])
        
    def test_bounding_box(self):
        """
        Test that bounding box is properly calculated
        """
        poly = Poly('tests/test_poly/pomorskie.poly')
        self.assertEqual((16.68, 53.47, 19.67, 54.855), poly.bounding_box)


if __name__ == '__main__':
    unittest.main()