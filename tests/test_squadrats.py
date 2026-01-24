import unittest
from pathlib import Path

import shapely

import squadrats2garmin.common.squadrats as squadrats
from squadrats2garmin.common.job import Job
from squadrats2garmin.common.osm import Way
from squadrats2garmin.common.poly import ExtensionAwarePolyLoader
from squadrats2garmin.common.region import Subdivision, Country
from squadrats2garmin.common.tile import ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS, Zoom


class TestSquadratsClient(unittest.TestCase):

    def setUp(self):
        self._client = squadrats.SquadratsClient()

    def test_get_trophies(self):
        self._client.get_trophies(user_id='P2NkzJ2UfnOGnq7DNaA1Y1JZYkl1')


class TestShapelyTileGenerator(unittest.TestCase):
    """
    Test that tiles are properly generated using Shapely
    """
    RESOURCE_DIR = Path(__file__).parent / "test_poly"

    def setUp(self):
        self._generator = squadrats.ShapelyTileMapGenerator()
        self.region = {
            'ES-CN': Subdivision(
                country=Country(iso_code='ES'),
                iso_code='ES-CN',
                poly_loader=ExtensionAwarePolyLoader(self.RESOURCE_DIR / "ES-CN-Canarias.geojson")),
            'PL-22': Subdivision(
                country=Country(iso_code='PL'),
                iso_code='PL-22',
                poly_loader=ExtensionAwarePolyLoader(self.RESOURCE_DIR / 'PL-22-Pomorskie.geojson'))
        }

    def test_generate_tiles_ES_CN(self):
        region = self.region['ES-CN']

        with self.subTest(msg=f"{ZOOM_SQUADRATS}"):
            tiles = self._generator.generate_rows(poly=region.coords, zoom=ZOOM_SQUADRATS)
            self.assertEqual(96, len(tiles.keys()))
            self.assertEqual(193, sum(map(len, tiles.values())))
            self.assertEqual(6788, min(tiles.keys()))
            self.assertEqual(6883, max(tiles.keys()))

        with self.subTest(msg=f"{ZOOM_SQUADRATINHOS}"):
            tiles = self._generator.generate_rows(poly=region.coords, zoom=ZOOM_SQUADRATINHOS)
            self.assertEqual(749, len(tiles.keys()))
            self.assertEqual(1490, sum(map(len, tiles.values())))
            self.assertEqual(54311, min(tiles.keys()))
            self.assertEqual(55066, max(tiles.keys()))

    def test_generate_tiles_PL_22(self):
        region = self.region['PL-22']

        with self.subTest(msg=f"{ZOOM_SQUADRATS}"):
            tiles = self._generator.generate_rows(poly=region.coords, zoom=ZOOM_SQUADRATS)
            self.assertEqual(108, len(tiles.keys()))
            self.assertEqual(141, sum(map(len, tiles.values())))
            self.assertEqual(5193, min(tiles.keys()))
            self.assertEqual(5300, max(tiles.keys()))

        with self.subTest(msg=f"{ZOOM_SQUADRATINHOS}"):
            tiles = self._generator.generate_rows(poly=region.coords, zoom=ZOOM_SQUADRATINHOS)
            self.assertEqual(859, len(tiles.keys()))
            self.assertEqual(1137, sum(map(len, tiles.values())))
            self.assertEqual(41546, min(tiles.keys()))
            self.assertEqual(42404, max(tiles.keys()))

    def test_generate_tiles_PL(self):
        """
        Test that tiles are properly generated
        """
        region = Country(
            iso_code='PL',
            poly_loader=ExtensionAwarePolyLoader(self.RESOURCE_DIR / 'PL-Poland-67097-points.geojson'))

        with self.subTest(msg=f"{ZOOM_SQUADRATS}"):
            tiles = self._generator.generate_rows(poly=region.coords, zoom=ZOOM_SQUADRATS)
            self.assertEqual(448, len(tiles.keys()))
            self.assertEqual(606, sum(map(len, tiles.values())))
            self.assertEqual(5179, min(tiles.keys()))
            self.assertEqual(5626, max(tiles.keys()))

        with self.subTest(msg=f"{ZOOM_SQUADRATINHOS}"):
            tiles = self._generator.generate_rows(poly=region.coords, zoom=ZOOM_SQUADRATINHOS)
            self.assertEqual(3578, len(tiles.keys()))
            self.assertEqual(5464, sum(map(len, tiles.values())))
            self.assertEqual(41434, min(tiles.keys()))
            self.assertEqual(45011, max(tiles.keys()))

    def test_write_geojson(self):
        """
        Test that tiles are properly generated
        """
        region = self.region['ES-CN']

        with self.subTest(msg=f"{ZOOM_SQUADRATS}"):
            tiles = self._generator.generate_rows(poly=region.coords, zoom=ZOOM_SQUADRATS)
            with Path(f"output/{region.name}-14.geojson").open(mode="w") as f:
                f.write(tiles_to_geojson(tiles=tiles, zoom=ZOOM_SQUADRATS))

        with self.subTest(msg=f"{ZOOM_SQUADRATINHOS}"):
            tiles = self._generator.generate_rows(poly=region.coords, zoom=ZOOM_SQUADRATINHOS)
            with Path(f"output/{region.name}-17.geojson").open(mode="w") as f:
                f.write(tiles_to_geojson(tiles=tiles, zoom=ZOOM_SQUADRATINHOS))


class TestSquadrats(unittest.TestCase):

    RESOURCE_DIR = Path(__file__).parent / "test_poly"

    def setUp(self):
        self.region = {
            'PL-22': Subdivision(
                country=Country(iso_code='PL'),
                iso_code='PL-22',
                poly_loader=ExtensionAwarePolyLoader(self.RESOURCE_DIR / 'PL-22-Pomorskie.geojson'))
        }

    def test_generate_grid(self):
        job = Job(region=self.region['PL-22'], zoom=ZOOM_SQUADRATS, osm_file=None)
        ways: list[Way] = squadrats.generate_grid(poly=job.region.coords, job=job)
        self.assertEqual(len(ways), 307)

def tiles_to_geojson(tiles: squadrats.TileMap, zoom: Zoom) -> str:
    return shapely.to_geojson(shapely.multipolygons([
        tile_to_polygon(x=x, y=y, zoom=zoom)
        for y, tile_bars in tiles.items()
        for tile_range in tile_bars
        for x in range(tile_range[0], tile_range[1] + 1)
    ]))

def contour_to_geojson(tiles: squadrats.TileMap, zoom: Zoom) -> str:
    return shapely.to_geojson(shapely.multipolygons([
        tile_to_polygon(x=x, y=y, zoom=zoom)
        for y, tile_bars in tiles.items()
        for tile_range in tile_bars
        for x in tile_range
    ]))

def tile_to_polygon(y: int, x: int, zoom: Zoom) -> shapely.Polygon:
    return shapely.box(
        xmin=zoom.lon(x),
        ymin=zoom.lat(y + 1),
        xmax=zoom.lon(x + 1),
        ymax=zoom.lat(y),
    )

if __name__ == '__main__':
    unittest.main()
