import unittest

from common.poly import BoundingBox
from common.poly import Poly
from common.poly import Coordinates
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
        self.assertEqual(len(squadrats), 11093)
        squadratinhos = poly.generate_tiles(ZOOM_SQUADRATINHOS)
        self.assertEqual(len(squadratinhos), 693930)

    def test_generate_tiles_along_the_line_simple_vertical(self):
        zoom = ZOOM_SQUADRATS

        result = _generate_tiles_along_the_line_simple_vertical(pointA = Coordinates(lat = 0, lon = 0), pointB = Coordinates(lat = 1, lon = 1), zoom = zoom)
        self.assertEqual(len(result), 47)
        self.assertEqual(result[0],  Tile.tile_at(lon = 0, lat = 1, zoom = zoom))
        self.assertEqual(result[-1], Tile.tile_at(lon = 0, lat = 0, zoom = zoom))

        result = _generate_tiles_along_the_line_simple_vertical(pointA = Coordinates(lat = 1, lon = 1), pointB = Coordinates(lat = 0, lon = 0), zoom = zoom)
        self.assertEqual(len(result), 47)
        self.assertEqual(result[0],  Tile.tile_at(lon = 1, lat = 1, zoom = zoom))
        self.assertEqual(result[-1], Tile.tile_at(lon = 1, lat = 0, zoom = zoom))

        result = _generate_tiles_along_the_line_simple_vertical(pointA = Coordinates(lat = 0, lon = 0), pointB = Coordinates(lat = 1, lon = -1), zoom = zoom)
        self.assertEqual(len(result), 47)
        self.assertEqual(result[0],  Tile.tile_at(lon = -1, lat = 1, zoom = zoom))
        self.assertEqual(result[-1], Tile.tile_at(lon = -1, lat = 0, zoom = zoom))

        result = _generate_tiles_along_the_line_simple_vertical(pointA = Coordinates(lat = 1, lon = -1), pointB = Coordinates(lat = 0, lon = 0), zoom = zoom)
        self.assertEqual(len(result), 47)
        self.assertEqual(result[0],  Tile.tile_at(lon = 0, lat = 1, zoom = zoom))
        self.assertEqual(result[-1], Tile.tile_at(lon = 0, lat = 0, zoom = zoom))

    def test_generate_tiles_along_the_line(self):
        zoom = ZOOM_SQUADRATS

        result = _generate_tiles_along_the_line(pointA = Coordinates(lat = 0, lon = 0), pointB = Coordinates(lat = 0.1, lon = 0.1), zoom = zoom)
        self.assertEqual(len(result), 10)
        self.assertEqual(result[0],  Tile.tile_at(lon = 0.08, lat = 0.1, zoom = zoom))
        self.assertEqual(result[1],  Tile.tile_at(lon = 0.1, lat = 0.1, zoom = zoom))
        self.assertEqual(result[-1], Tile.tile_at(lon = 0, lat = 0, zoom = zoom))

        result = _generate_tiles_along_the_line(pointA = Coordinates(lat = 0, lon = 0), pointB = Coordinates(lat = 1, lon = 1), zoom = zoom)
        self.assertEqual(len(result), 92)
        self.assertEqual(result[0],  Tile.tile_at(lon = 0.98, lat = 1, zoom = zoom))
        self.assertEqual(result[1],  Tile.tile_at(lon = 1, lat = 1, zoom = zoom))
        self.assertEqual(result[-1], Tile.tile_at(lon = 0, lat = 0, zoom = zoom))


    def test_generate_tiles_for_a_row(self):
        # L R
        # XXX
        self.__generate_tiles_for_a_row_assert(
            input = [(1, 'L'), (3, 'R')],
            expected = "XXX")

        # LL R
        # XXXX
        self.__generate_tiles_for_a_row_assert(
            input = [(1, 'L'), (2, 'L'), (4, 'R')],
            expected = "XXXX")

        # L RR
        # XXXX
        self.__generate_tiles_for_a_row_assert(
            input = [(1, 'L'), (3, 'R'), (4, 'R')], 
            expected = "XXXX")

        # LL RR
        # XXXXX
        self.__generate_tiles_for_a_row_assert(
            input = [(1, 'L'), (2, 'L'), (4, 'R'), (5, 'R')], 
            expected = "XXXXX")

        # LLRR
        # XXXX
        self.__generate_tiles_for_a_row_assert(
            input = [(1, 'L'), (2, 'L'), (3, 'R'), (4, 'R')], 
            expected = "XXXX")

        # L R L R
        # XXX XXX
        self.__generate_tiles_for_a_row_assert(
            input = [(1, 'L'), (3, 'R'), (5, 'L'), (7, 'R')],
            expected = "XXX XXX")

        # LRR L R
        # XXX XXX
        self.__generate_tiles_for_a_row_assert(
            input = [(1, 'L'), (2, 'R'), (3, 'R'), (5, 'L'), (7, 'R')], 
            expected = "XXX XXX")

        # L RL R
        # XXXXXX
        self.__generate_tiles_for_a_row_assert(
            input = [(1, 'L'), (3, 'R'), (4, 'L'), (6, 'R')],
            expected = "XXXXXX")

        # L R
        #   L R
        # XXXXX
        self.__generate_tiles_for_a_row_assert(
            input = [(1, 'L'), (3, 'R'), (3, 'L'), (5, 'R')],
            expected = "XXXXX")

        # LR
        #  L R
        # XXXXX
        self.__generate_tiles_for_a_row_assert(
            input = [(1, 'L'), (2, 'R'), (2, 'L'), (4, 'R')],
            expected = "XXXX")

        # L
        # R
        # X
        self.__generate_tiles_for_a_row_assert(
            input = [(1, 'L'), (1, 'R')],
            expected = "X")

        # L L R
        # R
        # X
        # self.__generate_tiles_for_a_row_assert(
        #     input = [(1, 'L'), (1, 'R'), (3, 'L'), (5, 'R')],
        #     expected = "X XXX")
        
    # def test_generate_tiles_for_a_row1(self):
    #     self.__generate_tiles_for_a_row_assert(
    #         input = [(1, 'L'), (1, 'R'), (3, 'L'), (5, 'R')],
    #         expected = "X XXX")


    def __generate_tiles_for_a_row_assert(self, input: list, expected: str):
        poly = Poly('tests/test_poly/pomorskie.poly')
        y = 1
        zoom = ZOOM_SQUADRATS
        expectedArray = [i + 1 for i in range(len(expected)) if expected[i] == 'X']
        
        # ordered elements, one continuous segment
        result = poly._Poly__generate_tiles_for_a_row(row = input, y = y, zoom = zoom)
        self.assertEqual(result, [Tile(x = x, y = y, zoom = zoom) for x in expectedArray])

if __name__ == '__main__':
    unittest.main()