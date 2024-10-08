import unittest

from common.poly import BoundingBox
from common.poly import Poly
from common.poly import Coordinates
from common.poly import PolyFileIncorrectFiletypeException
from common.tile import Tile
from common.zoom import ZOOM_SQUADRATS
from common.zoom import ZOOM_SQUADRATINHOS

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
        self.assertEqual(len(poly.coords[0]), 215)
        self.assertEqual(poly.coords[0][0], Coordinates(lat = 54.58, lon = 16.68))
        self.assertEqual(poly.coords[0][100], Coordinates(lat = 53.665, lon = 18.465))
        self.assertEqual(poly.coords[0][200], Coordinates(lat = 54.35, lon = 16.79))
        self.assertEqual(poly.coords[0][214], Coordinates(lat = 54.58, lon = 16.68))
        
    def test_bounding_box(self):
        """
        Test that bounding box is properly calculated
        """
        poly = Poly('tests/test_poly/pomorskie.poly')
        self.assertEqual(poly.bounding_box, BoundingBox(n = 54.855, e = 19.67, s = 53.47, w = 16.68))


if __name__ == '__main__':
    unittest.main()