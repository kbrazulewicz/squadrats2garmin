import unittest

from common.poly import Coordinates
from common.poly import Poly
from common.squadrats import Boundary
from common.squadrats import line_grid_intersections
from common.squadrats import line_intersection
from common.squadrats import generate_tiles
from common.squadrats import _generate_tiles_by_bounding_box
from common.squadrats import _generate_tiles_for_a_row
from common.tile import Tile
from common.zoom import ZOOM_SQUADRATS
from common.zoom import ZOOM_SQUADRATINHOS

class TestSquadrats(unittest.TestCase):
    """Test functionality provided by the Squadrats module"""

    def test_line_intersection(self):
        pointA: Coordinates = Coordinates(lat = 0, lon = 0)
        pointB: Coordinates = Coordinates(lat = 5, lon = 7)

        # intersections with the ends of the line
        self.assertEqual(line_intersection(a = pointA, b = pointB, lat = pointA.lat), pointA.lon)
        self.assertEqual(line_intersection(a = pointA, b = pointB, lat = pointB.lat), pointB.lon)

        # other intersections
        self.assertEqual(line_intersection(a = pointA, b = pointB, lat = 1), 1.4)
        self.assertEqual(line_intersection(a = pointA, b = pointB, lat = 2), 2.8)
        self.assertEqual(line_intersection(a = pointA, b = pointB, lat = 3), 4.2)
        self.assertEqual(line_intersection(a = pointA, b = pointB, lat = 4), 5.6)

    
    def test_line_grid_intersections(self):
        pointS: Coordinates = Coordinates(lat = 0.0, lon = 0.0)
        pointN: Coordinates = Coordinates(lat = 0.1, lon = 0.1)

        boundariesNorthward = line_grid_intersections(a = pointS, b = pointN, zoom = ZOOM_SQUADRATS)
        boundariesSouthward = line_grid_intersections(a = pointN, b = pointS, zoom = ZOOM_SQUADRATS)

        self.assertEqual(len(boundariesNorthward), 6)
        self.assertEqual(len(boundariesSouthward), 6)

        # print(boundariesNorthward)
        # print(boundariesSouthward)

    def test_tiles_by_bounding_box(self):
        """Test that tiles are properly generated for the bounding box method
        """
        poly = Poly('tests/test_poly/pomorskie.poly')
        squadrats = _generate_tiles_by_bounding_box(poly=poly, zoom=ZOOM_SQUADRATS)
        self.assertEqual(len(squadrats), 14933)
        squadratinhos = _generate_tiles_by_bounding_box(poly=poly, zoom=ZOOM_SQUADRATINHOS)
        self.assertEqual(len(squadratinhos), 939807)


    def test_generate_tiles_for_a_row(self):

        for (input, expected) in [
            # L R
            # XXX
            (
                [(1, 'L'), (3, 'R')],
                "XXX"
            ),
            # LL R
            # XXXX
            (
                [(1, 'L'), (2, 'L'), (4, 'R')],
                "XXXX"
            ),
            # L RR
            # XXXX
            (
                [(1, 'L'), (3, 'R'), (4, 'R')],
                "XXXX"
            ),
            # LL RR
            # XXXXX
            (
                [(1, 'L'), (2, 'L'), (4, 'R'), (5, 'R')],
                "XXXXX"
            ),
            # LLRR
            # XXXX
            (
                [(1, 'L'), (2, 'L'), (3, 'R'), (4, 'R')],
                "XXXX"
            ),
            # L R L R
            # XXX XXX
            (
                [(1, 'L'), (3, 'R'), (5, 'L'), (7, 'R')],
                "XXX XXX"
            ),
        # # LRR L R
        # # XXX XXX
        # self.__generate_tiles_for_a_row_assert(
        #     input = [(1, 'L'), (2, 'R'), (3, 'R'), (5, 'L'), (7, 'R')], 
        #     expected = "XXX XXX")

        # # L RL R
        # # XXXXXX
        # self.__generate_tiles_for_a_row_assert(
        #     input = [(1, 'L'), (3, 'R'), (4, 'L'), (6, 'R')],
        #     expected = "XXXXXX")

        # # L R
        # #   L R
        # # XXXXX
        # self.__generate_tiles_for_a_row_assert(
        #     input = [(1, 'L'), (3, 'R'), (3, 'L'), (5, 'R')],
        #     expected = "XXXXX")

        # # LR
        # #  L R
        # # XXXXX
        # self.__generate_tiles_for_a_row_assert(
        #     input = [(1, 'L'), (2, 'R'), (2, 'L'), (4, 'R')],
        #     expected = "XXXX")

        # # L
        # # R
        # # X
        # self.__generate_tiles_for_a_row_assert(
        #     input = [(1, 'L'), (1, 'R')],
        #     expected = "X")

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


            ]:
            with self.subTest(input = input, expected = expected):
                y = 1
                zoom = ZOOM_SQUADRATS
                row = [Boundary(lon=zoom.lon(i[0]), lr=i[1], y=y) for i in input]
                expectedArray = [i + 1 for i in range(len(expected)) if expected[i] == 'X']

                result = _generate_tiles_for_a_row(row=row, zoom=zoom)        
                self.assertEqual(result, [Tile(x=x, y=y, zoom=zoom) for x in expectedArray])
        
    def test_generate_tiles(self):
        """
        Test that tiles are properly generated
        """
        poly = Poly('tests/test_poly/pomorskie.poly')
        squadrats = generate_tiles(poly=poly, zoom=ZOOM_SQUADRATS)
        self.assertEqual(len(squadrats), 10549)
        squadratinhos = generate_tiles(poly=poly, zoom=ZOOM_SQUADRATINHOS)
        self.assertEqual(len(squadratinhos), 657742)


    # def test_generate_tiles_along_the_line(self):
    #     zoom = ZOOM_SQUADRATS

    #     result = _generate_tiles_along_the_line(pointA = Coordinates(lat = 0, lon = 0), pointB = Coordinates(lat = 0.1, lon = 0.1), zoom = zoom)
    #     self.assertEqual(len(result), 10)
    #     self.assertEqual(result[0],  Tile.tile_at(lon = 0.08, lat = 0.1, zoom = zoom))
    #     self.assertEqual(result[1],  Tile.tile_at(lon = 0.1, lat = 0.1, zoom = zoom))
    #     self.assertEqual(result[-1], Tile.tile_at(lon = 0, lat = 0, zoom = zoom))

    #     result = _generate_tiles_along_the_line(pointA = Coordinates(lat = 0, lon = 0), pointB = Coordinates(lat = 1, lon = 1), zoom = zoom)
    #     self.assertEqual(len(result), 92)
    #     self.assertEqual(result[0],  Tile.tile_at(lon = 0.98, lat = 1, zoom = zoom))
    #     self.assertEqual(result[1],  Tile.tile_at(lon = 1, lat = 1, zoom = zoom))
    #     self.assertEqual(result[-1], Tile.tile_at(lon = 0, lat = 0, zoom = zoom))



if __name__ == '__main__':
    unittest.main()