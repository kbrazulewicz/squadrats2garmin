import logging
import unittest
from pathlib import Path
from typing import cast

import shapely

from squadrats2garmin.common.region import RegionIndex


class MyTestCase(unittest.TestCase):
    RESOURCE_DIR = Path(__file__).parent / "test_region"

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)

    def test_region_index_poly_handling(self):
        region_index = RegionIndex(root_path=self.RESOURCE_DIR / "index-1")

        # no country with XX code
        with self.assertRaises(ValueError):
            region_index.select_regions(['XX'])

        # no polygon file for Ireland as a country
        with self.assertRaises(ValueError):
            region_index.select_regions(['IE'])

        # no province in IE with IE-X code
        with self.assertRaises(ValueError):
            region_index.select_regions(['IE-X'])

        # test selecting one or more existing provinces
        self.assertEqual(1, len(region_index.select_regions(['IE-C'])))
        self.assertEqual(4, len(region_index.select_regions(['IE-*'])))

        regions = region_index.select_regions(['IE-C', 'IE-L'])
        self.assertEqual(2, len(regions))
        [ie_c, ie_l] = regions
        self.assertEqual("IE-C", ie_c.code)
        self.assertEqual("Ireland - Connaught", ie_c.name)
        self.assertEqual((-10.34, 52.94, -7.56, 54.5), ie_c.coords.bounds)
        self.assertEqual("IE-L", ie_l.code)
        self.assertEqual("Ireland - Leinster", ie_l.name)
        self.assertEqual((-8.1, 52.08, -5.98, 54.14), ie_l.coords.bounds)

    def test_region_index_geojson_handling(self):
        region_index = RegionIndex(root_path=self.RESOURCE_DIR / "index-1")

        # check if GeoJSON discovery works (MT-Malta.geojson)
        regions = region_index.select_regions(['MT'])
        self.assertEqual(len(regions), 1)  # add assertion here

        [malta] = regions
        self.assertEqual("MT", malta.code)
        self.assertEqual("Malta", malta.name)
        self.assertEqual((13.92, 35.56, 14.84, 36.3), malta.coords.bounds)

    def test_all_polygons_are_properly_oriented(self):
        region_index = RegionIndex(root_path=Path("config/polygons"))

        for country in region_index.country.values():
            for region in [country, *country.get_all_subdivisions()]:
                if region.has_coords:
                    poly = region.coords
                    for geom in poly.geoms:
                        self.assertIsInstance(geom, shapely.Polygon, msg=f"{region.code}: all geometries should be Polygons")
                        geom = cast('shapely.Polygon', geom)
                        self.assertTrue(geom.exterior.is_ccw, msg=f"{region.code}: exterior of all Polygons should be counterclockwise")
                        for interior in geom.interiors:
                            self.assertFalse(interior.is_ccw, msg=f"{region.code}: interior of all Polygons should be clockwise")


if __name__ == '__main__':
    unittest.main()
