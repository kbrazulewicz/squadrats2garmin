import logging
import unittest
from pathlib import Path

import geojson
import pytest
import shapely
from pygeoif.geometry import Point, Polygon
from pytest_benchmark.plugin import benchmark

from squadrats2garmin.common.poly import parse_poly_file, parse_geojson_file
from squadrats2garmin.common.poly import PolyFileIncorrectFiletypeException


class TestPoly(unittest.TestCase):

    RESOURCES = Path('tests/test_poly')

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)

    def test_wrong_format(self):
        """
        Test that it can recognize a proper filetype
        """
        with self.assertRaises(PolyFileIncorrectFiletypeException) as cm:
            poly = parse_poly_file(self.RESOURCES / 'wrong_format.poly')

        self.assertEqual(str(cm.exception), "Expecting polygon filetype, got \"not-polygon\" instead")

    def test_pomorskie(self):
        """
        Test that it can load properly formatted POLY file
        """
        poly = parse_poly_file(self.RESOURCES / 'pomorskie.poly')
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
        poly = parse_poly_file(self.RESOURCES / 'pomorskie.poly')
        self.assertEqual((16.68, 53.47, 19.67, 54.855), poly.bounds)

    # @pytest.mark.usefixtures
    # def test_parse_poly(self):
    #     def parse():
    #         parse_poly_file(self.TEST_POLY / 'PL-Poland-67097-points.poly')
    #     benchmark(parse)
    #
    # def test_parse_json(self, benchmark):
    #     def parse():
    #         parse_geojson_file(self.TEST_POLY / 'PL-Poland-67097-points.json')
    #     benchmark(parse)

def test_parse_poly(benchmark):
    def parse():
        poly = parse_poly_file(TestPoly.RESOURCES / 'PL-Poland-67097-points.poly')
        return len(next(poly.geoms).exterior.coords)
    result = benchmark(parse)
    assert result == 67097

def test_parse_json(benchmark):
    def parse():
        poly = parse_geojson_file(TestPoly.RESOURCES / 'PL-Poland-67097-points.json')
        return len(poly.geoms[0].exterior.coords)
    result = benchmark(parse)
    assert result == 67097


def test_parse_trophies_geojson(benchmark):
    def parse():
        json_file = TestPoly.RESOURCES / "P2NkzJ2UfnOGnq7DNaA1Y1JZYkl1.json"
        with json_file.open() as f:
            return geojson.load(f)

    result = benchmark(parse)
    for feature in result.features:
        if isinstance(feature, geojson.feature.Feature):
            feature_name = feature.properties['name']
            if feature_name == 'squadratinhos':
                assert len(feature.geometry.coordinates[0][0]) == 13403

def test_parse_trophies_shapely(benchmark):
    def parse():
        json_file = TestPoly.RESOURCES / "P2NkzJ2UfnOGnq7DNaA1Y1JZYkl1.json"
        return shapely.from_geojson(json_file.read_bytes())

    result = benchmark(parse)

    assert len(result.geoms[4].geoms[0].exterior.coords) == 1291

if __name__ == '__main__':
    unittest.main()