import itertools
import unittest
from collections.abc import Iterable
from pathlib import Path

import shapely
from shapely import Point

import squadrats2garmin.common.squadrats as squadrats
from squadrats2garmin.common import job
from squadrats2garmin.common.job import Job
from squadrats2garmin.common.poly import ExtensionAwarePolyLoader
from squadrats2garmin.common.region import Subdivision, Country
from squadrats2garmin.common.tile import ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS, Tile, Zoom


class TestSquadratsClient(unittest.TestCase):

    def setUp(self):
        self._client = squadrats.SquadratsClient()

    def test_get_trophies(self):
        self._client.get_trophies(user_id='P2NkzJ2UfnOGnq7DNaA1Y1JZYkl1')


class TestBoundingBoxTileGenerator(unittest.TestCase):
    """
    Test that tiles are properly generated for the bounding box method
    """
    RESOURCE_DIR = Path(__file__).parent / "test_poly"

    def setUp(self):
        self._generator = squadrats.BoundingBoxTileGenerator()

    def test_generate_tiles_PL_22_bounding_box(self):
        region = Subdivision(
            country=Country(iso_code='PL'),
            iso_code='PL-22',
            poly_loader=ExtensionAwarePolyLoader(self.RESOURCE_DIR / 'pomorskie.poly'))
        job_14 = Job(region=region, zoom=ZOOM_SQUADRATS, osm_file=None)
        job_17 = Job(region=region, zoom=ZOOM_SQUADRATINHOS, osm_file=None)

        with self.subTest(msg=f"{job_14}"):
            tiles = squadrats.generate_tiles(poly=region.coords, job=job_14, generator=self._generator)
            self.assertEqual(109, len(tiles.keys()))
            self.assertEqual(14933, sum(map(len, tiles.values())))
            self.assertEqual(5193, min(tiles.keys()))
            self.assertEqual(5301, max(tiles.keys()))

        with self.subTest(msg=f"{job_17}"):
            tiles = squadrats.generate_tiles(poly=region.coords, job=job_17, generator=self._generator)
            self.assertEqual(863, len(tiles.keys()))
            self.assertEqual(939807, sum(map(len, tiles.values())))
            self.assertEqual(41549, min(tiles.keys()))
            self.assertEqual(42411, max(tiles.keys()))

    def test_generate_tiles_PL_bounding_box(self):
        """
        Test that tiles are properly generated
        """
        region = Country(
            iso_code='PL',
            poly_loader=ExtensionAwarePolyLoader(self.RESOURCE_DIR / 'PL-Poland-67097-points.geojson'))
        job_14 = Job(region=region, zoom=ZOOM_SQUADRATS, osm_file=None)
        job_17 = Job(region=region, zoom=ZOOM_SQUADRATINHOS, osm_file=None)

        with self.subTest(msg=f"{job_14}"):
            tiles = squadrats.generate_tiles(poly=region.coords, job=job_14, generator=self._generator)
            self.assertEqual(448, len(tiles.keys()))
            self.assertEqual(205632, sum(map(len, tiles.values())))
            self.assertEqual(5179, min(tiles.keys()))
            self.assertEqual(5626, max(tiles.keys()))

        with self.subTest(msg=f"{job_17}"):
            tiles = squadrats.generate_tiles(poly=region.coords, job=job_17, generator=self._generator)
            self.assertEqual(3578, len(tiles.keys()))
            self.assertEqual(13131260, sum(map(len, tiles.values())))
            self.assertEqual(41434, min(tiles.keys()))
            self.assertEqual(45011, max(tiles.keys()))


class TestShapelyTileGenerator(unittest.TestCase):
    """
    Test that tiles are properly generated using Shapely
    """
    RESOURCE_DIR = Path(__file__).parent / "test_poly"

    def setUp(self):
        self._generator = squadrats.ShapelyTileGenerator()

    def test_generate_tiles_ES_CN(self):
        region = Subdivision(
            country=Country(iso_code='ES'),
            iso_code='ES-CN',
            poly_loader=ExtensionAwarePolyLoader(self.RESOURCE_DIR / "ES-CN-Canarias.geojson"))
        job_14 = Job(region=region, zoom=ZOOM_SQUADRATS, osm_file=None)
        job_17 = Job(region=region, zoom=ZOOM_SQUADRATINHOS, osm_file=None)

        with self.subTest(msg=f"{job_14}"):
            tiles = squadrats.generate_tiles(poly=region.coords, job=job_14, generator=self._generator)
            self.assertEqual(96, len(tiles.keys()))
            self.assertEqual(2552, sum(map(len, tiles.values())))
            self.assertEqual(6788, min(tiles.keys()))
            self.assertEqual(6883, max(tiles.keys()))

        with self.subTest(msg=f"{job_17}"):
            tiles = squadrats.generate_tiles(poly=region.coords, job=job_17, generator=self._generator)
            self.assertEqual(749, len(tiles.keys()))
            self.assertEqual(143157, sum(map(len, tiles.values())))
            self.assertEqual(54311, min(tiles.keys()))
            self.assertEqual(55066, max(tiles.keys()))

    def test_generate_tiles_PL_22(self):
        region = Subdivision(
            country=Country(iso_code='PL'),
            iso_code='PL-22',
            poly_loader=ExtensionAwarePolyLoader(self.RESOURCE_DIR / 'pomorskie.poly'))
        job_14 = Job(region=region, zoom=ZOOM_SQUADRATS, osm_file=None)
        job_17 = Job(region=region, zoom=ZOOM_SQUADRATINHOS, osm_file=None)

        with self.subTest(msg=f"{job_14}"):
            tiles = squadrats.generate_tiles(poly=region.coords, job=job_14, generator=self._generator)
            self.assertEqual(109, len(tiles.keys()))
            self.assertEqual(10565, sum(map(len, tiles.values())))
            self.assertEqual(5193, min(tiles.keys()))
            self.assertEqual(5301, max(tiles.keys()))

        with self.subTest(msg=f"{job_17}"):
            tiles = squadrats.generate_tiles(poly=region.coords, job=job_17, generator=self._generator)
            self.assertEqual(863, len(tiles.keys()))
            self.assertEqual(657750, sum(map(len, tiles.values())))
            self.assertEqual(41549, min(tiles.keys()))
            self.assertEqual(42411, max(tiles.keys()))

    def test_generate_tiles_PL(self):
        """
        Test that tiles are properly generated
        """
        region = Country(
            iso_code='PL',
            poly_loader=ExtensionAwarePolyLoader(self.RESOURCE_DIR / 'PL-Poland-67097-points.geojson'))
        job_14 = Job(region=region, zoom=ZOOM_SQUADRATS, osm_file=None)
        job_17 = Job(region=region, zoom=ZOOM_SQUADRATINHOS, osm_file=None)

        with self.subTest(msg=f"{job_14}"):
            tiles = squadrats.generate_tiles(poly=region.coords, job=job_14, generator=self._generator)
            self.assertEqual(448, len(tiles.keys()))
            self.assertEqual(145066, sum(map(len, tiles.values())))
            self.assertEqual(5179, min(tiles.keys()))
            self.assertEqual(5626, max(tiles.keys()))

        with self.subTest(msg=f"{job_17}"):
            tiles = squadrats.generate_tiles(poly=region.coords, job=job_17, generator=self._generator)
            self.assertEqual(3578, len(tiles.keys()))
            self.assertEqual(9204896, sum(map(len, tiles.values())))
            self.assertEqual(41434, min(tiles.keys()))
            self.assertEqual(45011, max(tiles.keys()))

    def test_write_geojson(self):
        """
        Test that tiles are properly generated
        """
        name = "ES-CN-Canarias"
        region = Subdivision(
            country=Country(iso_code='PL'),
            iso_code='PL-22',
            poly_loader=ExtensionAwarePolyLoader(self.RESOURCE_DIR / f"{name}.geojson"))
        job_14 = Job(region=region, zoom=ZOOM_SQUADRATS, osm_file=None)
        job_17 = Job(region=region, zoom=ZOOM_SQUADRATINHOS, osm_file=None)

        with self.subTest(msg=f"{job_14}"):
            tiles = squadrats.generate_tiles(poly=region.coords, job=job_14, generator=self._generator)
            with Path(f"output/{name}-14.geojson").open(mode="w") as f:
                f.write(tiles_to_geojson(tiles=itertools.chain.from_iterable(tiles.values()), zoom=job_14.zoom))

        with self.subTest(msg=f"{job_17}"):
            tiles = squadrats.generate_tiles(poly=region.coords, job=job_17, generator=self._generator)
            with Path(f"output/{name}-17.geojson").open(mode="w") as f:
                f.write(tiles_to_geojson(tiles=itertools.chain.from_iterable(tiles.values()), zoom=job_17.zoom))

    def test_write_geojson_contour(self):
        """
        Test that tiles are properly generated
        """
        name = "PL-22-Pomorskie-11349"
        region = Subdivision(
            country=Country(iso_code='PL'),
            iso_code='PL-22',
            poly_loader=ExtensionAwarePolyLoader(self.RESOURCE_DIR / f"{name}.geojson"))
        job_14 = Job(region=region, zoom=ZOOM_SQUADRATS, osm_file=None)
        job_17 = Job(region=region, zoom=ZOOM_SQUADRATINHOS, osm_file=None)

        with self.subTest(msg=f"{job_14}"):
            tiles = squadrats.generate_tile_ranges(poly=region.coords, job=job_14, generator=self._generator)
            with Path(f"output/{name}-contour-14.geojson").open(mode="w") as f:
                f.write(contour_to_geojson(contour=itertools.chain.from_iterable(tiles.values()), zoom=job_14.zoom))

        with self.subTest(msg=f"{job_17}"):
            tiles = squadrats.generate_tile_ranges(poly=region.coords, job=job_17, generator=self._generator)
            with Path(f"output/{name}-contour-17.geojson").open(mode="w") as f:
                f.write(contour_to_geojson(contour=itertools.chain.from_iterable(tiles.values()), zoom=job_17.zoom))


def tiles_to_geojson(tiles: Iterable[Tile], zoom: Zoom) -> str:
    return shapely.to_geojson(shapely.multipolygons([tile_to_polygon(tile=tile, zoom=zoom) for tile in tiles]))

def contour_to_geojson(contour: Iterable[tuple[Tile, Tile]], zoom: Zoom) -> str:
    return shapely.to_geojson(shapely.multipolygons([tile_to_polygon(tile=t, zoom=zoom) for p in contour for t in p]))

def tile_to_polygon(tile: Tile, zoom: Zoom) -> shapely.Polygon:
    return shapely.box(
        xmin=zoom.lon(tile.x),
        ymin=zoom.lat(tile.y + 1),
        xmax=zoom.lon(tile.x + 1),
        ymax=zoom.lat(tile.y),
    )

if __name__ == '__main__':
    unittest.main()
