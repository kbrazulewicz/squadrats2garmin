import logging
import unittest
from pathlib import Path

import shapely
from pytest_benchmark.plugin import benchmark

from squadrats2garmin.common.poly import parse_poly_file


class TestPoly(unittest.TestCase):
    RESOURCES = Path('tests/test_poly')

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)

    def test_pomorskie(self):
        """
        Test that it can load properly formatted POLY file
        """
        pomorskie: shapely.MultiPolygon = parse_poly_file(self.RESOURCES / 'PL-22-Pomorskie.json')
        self.assertEqual(1, len(list(pomorskie.geoms)))
        self.assertEqual(0, len(list(pomorskie.geoms[0].interiors)))

        exterior: shapely.geometry.Polygon = pomorskie.geoms[0].exterior
        self.assertEqual(70, len(exterior.coords))
        self.assertEqual((16.70, 54.60), exterior.coords[0])
        self.assertEqual((19.60, 53.96), exterior.coords[20])
        self.assertEqual((17.86, 53.66), exterior.coords[40])
        self.assertTrue(exterior.is_closed)

    def test_es_cn_canarias(self):
        """
        Test that it can load properly formatted POLY file
        """
        poly: shapely.MultiPolygon = parse_poly_file(self.RESOURCES / 'ES-CN-Canarias.json')
        self.assertEqual(9, len(list(poly.geoms)))
        self.assertEqual([5, 22, 6, 22, 21, 28, 10, 15, 11], [len(geom.exterior.coords) for geom in poly.geoms])

    def test_bounding_box(self):
        """
        Test that bounding box is properly calculated
        """
        poly = parse_poly_file(self.RESOURCES / 'PL-22-Pomorskie.json')
        self.assertEqual((16.68, 53.48, 19.66, 54.86), poly.bounds)

    def test_squadrats_rings_are_closed(self):
        json_file = TestPoly.RESOURCES / "P2NkzJ2UfnOGnq7DNaA1Y1JZYkl1.json"
        squadrats_trophies: shapely.GeometryCollection = shapely.from_geojson(json_file.read_bytes())
        shapely.get_parts(squadrats_trophies)
        for geom in squadrats_trophies.geoms:
            if geom.geom_type == 'MultiPolygon':
                multipolygon: shapely.MultiPolygon = geom
                for polygon in multipolygon.geoms:
                    for ring in [polygon.exterior, *polygon.interiors]:
                        self.assertTrue(ring.is_closed)

            elif geom.geom_type == 'Polygon':
                polygon: shapely.Polygon = geom
                for ring in [polygon.exterior, *polygon.interiors]:
                    self.assertTrue(ring.is_closed)


def test_parse_poly(benchmark):
    def parse():
        poly = parse_poly_file(TestPoly.RESOURCES / 'PL-Poland-67097-points.poly')
        return len(poly.geoms[0].exterior.coords)

    result = benchmark(parse)
    assert result == 67097


def test_parse_json(benchmark):
    def parse():
        poly = parse_poly_file(TestPoly.RESOURCES / 'PL-Poland-67097-points.json')
        return len(poly.geoms[0].exterior.coords)

    result = benchmark(parse)
    assert result == 67097


def test_parse_trophies_shapely(benchmark):
    def parse():
        json_file = TestPoly.RESOURCES / "P2NkzJ2UfnOGnq7DNaA1Y1JZYkl1.json"
        return shapely.from_geojson(json_file.read_bytes())

    result = benchmark(parse)

    assert len(result.geoms[4].geoms[0].exterior.coords) == 13403


if __name__ == '__main__':
    unittest.main()
