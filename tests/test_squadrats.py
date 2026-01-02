import unittest
from pathlib import Path

from shapely import Point

import squadrats2garmin.common.squadrats
from squadrats2garmin.common.job import Job
from squadrats2garmin.common.poly import parse_poly_file, ExtensionAwarePolyLoader, PolyLoader
from squadrats2garmin.common.region import Subdivision, Country
from squadrats2garmin.common.tile import Tile, ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS

class TestSquadratsClient(unittest.TestCase):

    def setUp(self):
        self._client = squadrats2garmin.common.squadrats.SquadratsClient()

    def test_get_trophies(self):
        self._client.get_trophies(user_id='P2NkzJ2UfnOGnq7DNaA1Y1JZYkl1')


class TestSquadrats(unittest.TestCase):
    """Test functionality provided by the Squadrats module"""

    def test_line_intersection(self):
        point_a: Point = Point(0, 0)
        point_b: Point = Point(7, 5)

        # intersections with the ends of the line
        self.assertEqual(squadrats2garmin.common.squadrats.line_intersection(a=point_a, b=point_b, lat=point_a.y), point_a.x)
        self.assertEqual(squadrats2garmin.common.squadrats.line_intersection(a=point_a, b=point_b, lat=point_b.y), point_b.x)

        # other intersections
        self.assertEqual(squadrats2garmin.common.squadrats.line_intersection(a=point_a, b=point_b, lat=1), 1.4)
        self.assertEqual(squadrats2garmin.common.squadrats.line_intersection(a=point_a, b=point_b, lat=2), 2.8)
        self.assertEqual(squadrats2garmin.common.squadrats.line_intersection(a=point_a, b=point_b, lat=3), 4.2)
        self.assertEqual(squadrats2garmin.common.squadrats.line_intersection(a=point_a, b=point_b, lat=4), 5.6)

    def test_line_grid_intersections(self):
        point_s: Point = Point(0.0, 0.0)
        point_n: Point = Point(0.1, 0.1)

        boundariesNorthward = squadrats2garmin.common.squadrats.line_grid_intersections(a=point_s, b=point_n, zoom=ZOOM_SQUADRATS)
        boundariesSouthward = squadrats2garmin.common.squadrats.line_grid_intersections(a=point_n, b=point_s, zoom=ZOOM_SQUADRATS)

        self.assertEqual(len(boundariesNorthward), 6)
        self.assertEqual(len(boundariesSouthward), 6)

        # print(boundariesNorthward)
        # print(boundariesSouthward)

    def test_tiles_by_bounding_box(self):
        """Test that tiles are properly generated for the bounding box method
        """
        poly = parse_poly_file(Path('tests/test_poly/PL-22-Pomorskie.geojson'))
        squadrats = squadrats2garmin.common.squadrats._generate_tiles_by_bounding_box(poly=poly, zoom=ZOOM_SQUADRATS)
        self.assertEqual(len(squadrats), 14688)
        squadratinhos = squadrats2garmin.common.squadrats._generate_tiles_by_bounding_box(poly=poly, zoom=ZOOM_SQUADRATINHOS)
        self.assertEqual(len(squadratinhos), 932015)

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
                row = [squadrats2garmin.common.squadrats.Boundary(lon=job.zoom.lon(i[0]), lr=i[1], y=y) for i in input]
                expected_array = [i + 1 for i in range(len(expected)) if expected[i] == 'X']

                result = squadrats2garmin.common.squadrats._generate_tiles_for_a_sorted_row(row=row, zoom=job.zoom)
                self.assertEqual(result, [Tile(x, y) for x in expected_array])

    def test_generate_tiles(self):
        """
        Test that tiles are properly generated
        """
        poly_loader: PolyLoader = ExtensionAwarePolyLoader(Path('tests/test_poly/pomorskie.poly'))
        poly = poly_loader.load()
        region = Subdivision(country=Country(iso_code='PL'), iso_code='PL-22', poly_loader=poly_loader)
        squadrats = squadrats2garmin.common.squadrats.generate_tiles(poly=poly, job=Job(region=region, zoom=ZOOM_SQUADRATS, osm_file=None))
        self.assertEqual(sum(map(len, squadrats.values())), 10561)
        squadratinhos = squadrats2garmin.common.squadrats.generate_tiles(poly=poly, job=Job(region=region, zoom=ZOOM_SQUADRATINHOS, osm_file=None))
        self.assertEqual(sum(map(len, squadratinhos.values())), 657749)


if __name__ == '__main__':
    unittest.main()
