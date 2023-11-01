import unittest

from common.poly import BoundingBox
from common.poly import Poly
from common.poly import PolyFileIncorrectFiletypeException
from common.poly import _generate_tiles_along_the_line
from common.poly import _generate_tiles_along_the_line_simple_vertical
from common.tile import ZOOM_SQUADRATS
from common.tile import ZOOM_SQUADRATINHOS
from common.tile import Tile

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
        self.assertEqual(poly.coords[0][0], (16.68, 54.58))
        self.assertEqual(poly.coords[0][100], (18.465, 53.665))
        self.assertEqual(poly.coords[0][200], (16.79, 54.35))
        self.assertEqual(poly.coords[0][214], (16.68, 54.58))
        
    def test_bounding_box(self):
        """
        Test that bounding box is properly calculated
        """
        poly = Poly('tests/test_poly/pomorskie.poly')
        self.assertEqual(poly.bounding_box, BoundingBox(n = 54.855, e = 19.67, s = 53.47, w = 16.68))

    def test_tiles_by_bounding_box(self):
        """
        Test that tiles are properly generated
        """
        poly = Poly('tests/test_poly/pomorskie.poly')
        squadrats = poly.generate_tiles_by_bounding_box(ZOOM_SQUADRATS)
        self.assertEqual(len(squadrats), 14933)
        squadratinhos = poly.generate_tiles_by_bounding_box(ZOOM_SQUADRATINHOS)
        self.assertEqual(len(squadratinhos), 939807)

    def test_tiles(self):
        """
        Test that tiles are properly generated
        """
        poly = Poly('tests/test_poly/pomorskie.poly')
        squadrats = poly.generate_tiles(ZOOM_SQUADRATS)
        self.assertEqual(len(squadrats), 10984)
        squadratinhos = poly.generate_tiles(ZOOM_SQUADRATINHOS)
        self.assertEqual(len(squadratinhos), 693067)

    def test_generate_tiles_along_the_line_simple_vertical(self):
        result = _generate_tiles_along_the_line_simple_vertical(pointA = (0, 0), pointB = (1, 1), zoom = ZOOM_SQUADRATS)
        self.assertEqual(len(result), 47)
        self.assertEqual(result[0],  Tile.tile_at(lon = 0, lat = 1, zoom = ZOOM_SQUADRATS))
        self.assertEqual(result[-1], Tile.tile_at(lon = 0, lat = 0, zoom = ZOOM_SQUADRATS))

        result = _generate_tiles_along_the_line_simple_vertical(pointA = (1, 1), pointB = (0, 0), zoom = ZOOM_SQUADRATS)
        self.assertEqual(len(result), 47)
        self.assertEqual(result[0],  Tile.tile_at(lon = 1, lat = 1, zoom = ZOOM_SQUADRATS))
        self.assertEqual(result[-1], Tile.tile_at(lon = 1, lat = 0, zoom = ZOOM_SQUADRATS))

        result = _generate_tiles_along_the_line_simple_vertical(pointA = (0, 0), pointB = (-1, 1), zoom = ZOOM_SQUADRATS)
        self.assertEqual(len(result), 47)
        self.assertEqual(result[0],  Tile.tile_at(lon = -1, lat = 1, zoom = ZOOM_SQUADRATS))
        self.assertEqual(result[-1], Tile.tile_at(lon = -1, lat = 0, zoom = ZOOM_SQUADRATS))

        result = _generate_tiles_along_the_line_simple_vertical(pointA = (-1, 1), pointB = (0, 0), zoom = ZOOM_SQUADRATS)
        self.assertEqual(len(result), 47)
        self.assertEqual(result[0],  Tile.tile_at(lon = 0, lat = 1, zoom = ZOOM_SQUADRATS))
        self.assertEqual(result[-1], Tile.tile_at(lon = 0, lat = 0, zoom = ZOOM_SQUADRATS))

    def test_generate_tiles_along_the_line(self):
        result = _generate_tiles_along_the_line(pointA = (0, 0), pointB = (0.1, 0.1), zoom = ZOOM_SQUADRATS)
        self.assertEqual(len(result), 10)
        self.assertEqual(result[0],  Tile.tile_at(lon = 0.08, lat = 0.1, zoom = ZOOM_SQUADRATS))
        self.assertEqual(result[1],  Tile.tile_at(lon = 0.1, lat = 0.1, zoom = ZOOM_SQUADRATS))
        self.assertEqual(result[-1], Tile.tile_at(lon = 0, lat = 0, zoom = ZOOM_SQUADRATS))

        result = _generate_tiles_along_the_line(pointA = (0, 0), pointB = (1, 1), zoom = ZOOM_SQUADRATS)
        self.assertEqual(len(result), 92)
        self.assertEqual(result[0],  Tile.tile_at(lon = 0.98, lat = 1, zoom = ZOOM_SQUADRATS))
        self.assertEqual(result[1],  Tile.tile_at(lon = 1, lat = 1, zoom = ZOOM_SQUADRATS))
        self.assertEqual(result[-1], Tile.tile_at(lon = 0, lat = 0, zoom = ZOOM_SQUADRATS))

if __name__ == '__main__':
    unittest.main()