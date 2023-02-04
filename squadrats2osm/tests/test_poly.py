import unittest

from common.poly import BoundingBox
from common.poly import Poly
from common.poly import PolyFileIncorrectFiletypeException
from common.tile import ZOOM_SQUADRATS
from common.tile import ZOOM_SQUADRATINHOS

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
        self.assertEqual(len(poly.coords), 215)
        self.assertEqual(poly.coords[0], [16.68, 54.58])
        self.assertEqual(poly.coords[100], [18.465, 53.665])
        self.assertEqual(poly.coords[200], [16.79, 54.35])
        self.assertEqual(poly.coords[214], [16.68, 54.58])
        
    def test_bounding_box(self):
        """
        Test that bounding box is properly calculated
        """
        poly = Poly('tests/test_poly/pomorskie.poly')
        self.assertEqual(poly.bounding_box, BoundingBox(19.67, 54.855, 16.68, 53.47))

    def test_tiles(self):
        """
        Test that tiles are properly generated
        """
        poly = Poly('tests/test_poly/pomorskie.poly')
        squadrats = poly.generate_tiles(ZOOM_SQUADRATS)
        self.assertEqual(len(squadrats), 9216)
        squadratinhos = poly.generate_tiles(ZOOM_SQUADRATINHOS)
        self.assertEqual(len(squadratinhos), 580382)

if __name__ == '__main__':
    unittest.main()