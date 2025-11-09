import unittest
from pathlib import Path

from pygeoif.geometry import Point

import common.squadrats
from common.job import Job
from common.poly import parse_poly_file
from common.region import Subdivision, Country
from common.tile import Tile, ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS


class TestSquadrats(unittest.TestCase):
    """Test functionality provided by the Squadrats module"""

    def test_line_intersection(self):
        point_a: Point = Point(y=0, x=0)
        point_b: Point = Point(y=5, x=7)

        # intersections with the ends of the line
        self.assertEqual(common.squadrats.line_intersection(a=point_a, b=point_b, lat=point_a.y), point_a.x)
        self.assertEqual(common.squadrats.line_intersection(a=point_a, b=point_b, lat=point_b.y), point_b.x)

        # other intersections
        self.assertEqual(common.squadrats.line_intersection(a=point_a, b=point_b, lat=1), 1.4)
        self.assertEqual(common.squadrats.line_intersection(a=point_a, b=point_b, lat=2), 2.8)
        self.assertEqual(common.squadrats.line_intersection(a=point_a, b=point_b, lat=3), 4.2)
        self.assertEqual(common.squadrats.line_intersection(a=point_a, b=point_b, lat=4), 5.6)

    def test_line_grid_intersections(self):
        point_s: Point = Point(0.0, 0.0)
        point_n: Point = Point(0.1, 0.1)

        boundariesNorthward = common.squadrats.line_grid_intersections(a=point_s, b=point_n, zoom=ZOOM_SQUADRATS)
        boundariesSouthward = common.squadrats.line_grid_intersections(a=point_n, b=point_s, zoom=ZOOM_SQUADRATS)

        self.assertEqual(len(boundariesNorthward), 6)
        self.assertEqual(len(boundariesSouthward), 6)

        # print(boundariesNorthward)
        # print(boundariesSouthward)

    def test_tiles_by_bounding_box(self):
        """Test that tiles are properly generated for the bounding box method
        """
        poly = parse_poly_file(Path('tests/test_poly/pomorskie.poly'))
        squadrats = common.squadrats._generate_tiles_by_bounding_box(poly=poly, zoom=ZOOM_SQUADRATS)
        self.assertEqual(len(squadrats), 14933)
        squadratinhos = common.squadrats._generate_tiles_by_bounding_box(poly=poly, zoom=ZOOM_SQUADRATINHOS)
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
            # LRR L R
            # XXX XXX
            (
                    [(1, 'L'), (2, 'R'), (3, 'R'), (5, 'L'), (7, 'R')],
                    "XXX XXX"
            ),
            # L RL R
            # XXXXXX
            (
                    [(1, 'L'), (3, 'R'), (4, 'L'), (6, 'R')],
                    "XXXXXX"
            ),
            # L R
            #   L R
            # XXXXX
            (
                    [(1, 'L'), (3, 'R'), (3, 'L'), (5, 'R')],
                    "XXXXX"
            ),
            #   L R
            # L R
            # XXXXX
            (
                    [(1, 'L'), (3, 'L'), (3, 'R'), (5, 'R')],
                    "XXXXX"
            ),
            # LR
            #  L R
            # XXXXX
            (
                    [(1, 'L'), (2, 'R'), (2, 'L'), (4, 'R')],
                    "XXXX"
            ),
            #  L R
            # LR
            # XXXXX
            (
                    [(1, 'L'), (2, 'L'), (2, 'R'), (4, 'R')],
                    "XXXX"
            ),
            # L
            # R
            # X
            (
                    [(1, 'L'), (1, 'R')],
                    "X"
            ),
            # R
            # L
            # X
            (
                    [(1, 'R'), (1, 'L')],
                    "X"
            ),
            # L
            # R
            #   L R
            # X XXX
            (
                    [(1, 'L'), (1, 'R'), (3, 'L'), (5, 'R')],
                    "X XXX"
            ),
            # R
            # L
            #   L R
            # X XXX
            (
                    [(1, 'R'), (1, 'L'), (3, 'L'), (5, 'R')],
                    "X XXX"
            ),

            # L R L R
            #   L R
            # XXXXXXX
            (
                    [(1, 'L'), (3, 'R'), (3, 'L'), (5, 'L'), (5, 'R'), (7, 'R')],
                    "XXXXXXX"
            ),
            # (
            #     [(1, 'L'), (3, 'L'), (3, 'R'), (5, 'L'), (5, 'R'), (7, 'R')],
            #     "XXXXXXX"
            # ),
            (
                    [(1, 'L'), (3, 'R'), (3, 'L'), (5, 'R'), (5, 'L'), (7, 'R')],
                    "XXXXXXX"
            ),
            (
                    [(1, 'L'), (3, 'L'), (3, 'R'), (5, 'R'), (5, 'L'), (7, 'R')],
                    "XXXXXXX"
            ),
        ]:
            with self.subTest(input=input, expected=expected):
                y = 1
                job = Job(region=None, zoom=ZOOM_SQUADRATS, osm_file=None)
                row = [common.squadrats.Boundary(lon=job.zoom.lon(i[0]), lr=i[1], y=y) for i in input]
                expectedArray = [i + 1 for i in range(len(expected)) if expected[i] == 'X']

                result = common.squadrats._generate_tiles_for_a_sorted_row(row=row, zoom=job.zoom)
                self.assertEqual(result, [Tile(coords=(x, y), zoom=job.zoom) for x in expectedArray])

    def test_generate_tiles(self):
        """
        Test that tiles are properly generated
        """
        poly = parse_poly_file(Path('tests/test_poly/pomorskie.poly'))
        region = Subdivision(country=Country(iso_code='PL'), iso_code='PL-22', coordinates=poly)
        squadrats = common.squadrats.generate_tiles(poly=poly, job=Job(region=region, zoom=ZOOM_SQUADRATS, osm_file=None))
        self.assertEqual(sum(map(len, squadrats.values())), 10561)
        squadratinhos = common.squadrats.generate_tiles(poly=poly, job=Job(region=region, zoom=ZOOM_SQUADRATINHOS, osm_file=None))
        self.assertEqual(sum(map(len, squadratinhos.values())), 657749)


if __name__ == '__main__':
    unittest.main()
