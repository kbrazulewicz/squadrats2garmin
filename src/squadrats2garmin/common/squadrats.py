import itertools
import logging
import xml.etree.ElementTree as ET

from collections import defaultdict

import requests
import shapely
from shapely.geometry import MultiPolygon
from typing import Protocol

from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from squadrats2garmin.common import util
from squadrats2garmin.common.job import Job
from squadrats2garmin.common.osm import Node, Way
from squadrats2garmin.common.tile import Tile, Zoom
from squadrats2garmin.common.timer import timeit

TAGS_WAY = [('name', 'grid')]

logger = logging.getLogger(__name__)


class SquadratsClient:
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'SquadratsClient/1.0'
        })

        retry = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount('https://', adapter)

        self._timeout = 10

    def _get_geojson(self, user_id: str) -> dict:
        response = self._session.get(f'https://mainframe-api.squadrats.com/anonymous/squadrants/{user_id}/geojson',
                                     timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    def get_trophies(self, user_id: str):
        with timeit(msg=f"Fetching trophies for user {user_id}"):
            geojson_info = self._get_geojson(user_id)

            response = self._session.get(geojson_info['url'], timeout=self._timeout)
            response.raise_for_status()
            return response.json()


class TileGenerator(Protocol):
    def generate(self, poly: shapely.MultiPolygon, zoom: Zoom) -> dict[int, list[tuple[int, int]]]:
        """

        :param poly:
        :param zoom:
        :return:
        {
            y_1 -> [(x_1_1_start, x_1_1_end)],
            y_2 -> [(x_2_1_start, x_2_1_end), (x_2_2_start, x_2_2_end)],
            ...
        }
        """
        ...


class BoundingBoxTileGenerator(TileGenerator):
    """
    Generate tiles for the rectangular area defined by the polygon bounding box
    """

    def generate(self, poly: shapely.MultiPolygon, zoom: Zoom) -> dict[int, list[tuple[int, int]]]:
        (bounds_w, bounds_s, bounds_e, bounds_n) = poly.bounds
        (y_min, y_max) = [zoom.y(y) for y in [bounds_n, bounds_s]]
        (x_min, x_max) = [zoom.x(x) for x in [bounds_w, bounds_e]]

        return {
            y: [(x_min, x_max)]
            for y in range(y_min, y_max + 1)
        }


class ShapelyTileGenerator(TileGenerator):
    """
    Generate tiles for the rectangular area defined by the polygon bounding box
    """

    def __init__(self):
        self.__logger = logging.getLogger(__name__ + "." + type(self).__name__)

    def generate(self, poly: shapely.MultiPolygon, zoom: Zoom) -> dict[int, list[tuple[int, int]]]:
        tiles = {}

        (bounds_w, bounds_s, bounds_e, bounds_n) = poly.bounds
        (y_min, y_max) = [zoom.y(y) for y in [bounds_n, bounds_s]]

        for y in range(y_min, y_max + 1):
            ranges = []
            result = shapely.clip_by_rect(poly, xmin=bounds_w, ymin=zoom.lat(y + 1), xmax=bounds_e, ymax=zoom.lat(y))
            if result.is_empty: continue

            if isinstance(result, shapely.Polygon):
                ranges.append(self._clipped_polygon_to_range(poly=result, zoom=zoom))
            elif isinstance(result, shapely.MultiPolygon):
                for part in result.geoms:
                    ranges.append(self._clipped_polygon_to_range(poly=part, zoom=zoom))
            else:
                self.__logger.warning("type %s not supported", type(result))

            tiles[y] = util.merge_ranges_end_inclusive(ranges)

        return tiles

    def _clipped_polygon_to_range(self, poly: shapely.Polygon, zoom: Zoom) -> tuple[int, int]:
        (clip_w, clip_s, clip_e, clip_n) = poly.bounds
        (x_min, x_max) = [zoom.x(x) for x in [clip_w, clip_e]]
        return x_min, x_max


def generate_ranges(poly: MultiPolygon, job: Job, generator: TileGenerator = ShapelyTileGenerator()) -> dict[
    int, list[tuple[int, int]]]:
    """Generate horizontal ranges at a given zoom covering the entire polygon
    """
    with timeit(f"{job}: generate ranges"):
        return generator.generate(poly=poly, zoom=job.zoom)


def generate_tiles(poly: MultiPolygon, job: Job, generator: TileGenerator = ShapelyTileGenerator()) -> dict[
    int, list[Tile]]:
    """Generate tiles at a given zoom covering the entire polygon
    """
    with timeit(f"generate_tiles({job})"):
        tile_ranges = generator.generate(poly=poly, zoom=job.zoom)

        # TODO eliminate this step
        tiles: dict[int, list[Tile]] = {}
        for y, ranges in tile_ranges.items():
            tiles[y] = [
                Tile(x, y)
                for x1, x2 in ranges
                for x in range(x1, x2 + 1)
            ]

        return tiles


def generate_grid(ranges: dict[int, list[tuple[int, int]]], job: Job) -> list[Way]:
    if not ranges:
        return []

    ways: list[Way] = []

    ranges_by_x = defaultdict(list)
    ranges_by_y = {
        y: util.make_ranges_end_inclusive(rr)
        for y, rr in ranges.items()
    }

    with timeit(f"{job}: horizontal lines"):
        # generate horizontal lines
        for y in sorted(ranges_by_y.keys()):
            if y - 1 not in ranges_by_y:
                # first row or a gap - generate top edge
                ways.extend(_create_horizontal_ways_for_ranges(y=y, ranges=ranges_by_y[y], job=job))

            if y + 1 in ranges_by_y:
                # generate bottom edge between current and next row
                z = itertools.chain(ranges_by_y[y], ranges_by_y[y + 1])
                type(z)
                ways.extend(
                    _create_horizontal_ways_for_ranges(
                        y=y + 1,
                        ranges=util.merge_ranges(itertools.chain(ranges_by_y[y], ranges_by_y[y + 1])),
                        job=job))
            else:
                # generate bottom edge when next row is empty
                ways.extend(_create_horizontal_ways_for_ranges(y=y + 1, ranges=ranges_by_y[y], job=job))

            for r in ranges_by_y[y]:
                for x in range(r[0], r[1] + 1):
                    ranges_by_x[x].append((y, y + 1))

    with timeit(f"{job}: vertical lines"):
        ranges_by_x = {y: util.merge_ranges(rr) for y, rr in ranges_by_x.items()}

        # generate vertical lines
        for x in sorted(ranges_by_x.keys()):
            if x - 1 not in ranges_by_x:
                # first column or a gap - generate left edge
                ways.extend(_create_vertical_ways_for_ranges(x=x, ranges=ranges_by_x[x], job=job))

            if x + 1 in ranges_by_x:
                # generate right edge between current and next column
                ways.extend(
                    _create_vertical_ways_for_ranges(
                        x=x + 1,
                        ranges=util.merge_ranges(itertools.chain(ranges_by_x[x], ranges_by_x[x + 1])),
                        job=job)
                )
            else:
                # generate right edge when next column is empty
                ways.extend(_create_vertical_ways_for_ranges(x=x + 1, ranges=ranges_by_x[x], job=job))

    return ways


def _create_horizontal_ways_for_ranges(y: int, ranges: list[tuple[int, int]], job: Job) -> list[Way]:
    return [
        Way(
            way_id=job.next_id(),
            nodes=[_osm_node((x, y), job) for x in r],
            tags=TAGS_WAY + [('zoom', job.zoom.zoom)]
        )
        for r in ranges
    ]

def _create_vertical_ways_for_ranges(x: int, ranges: list[tuple[int, int]], job: Job) -> list[Way]:
    return [
        Way(
            way_id=job.next_id(),
            nodes=[_osm_node((x, y), job) for y in r],
            tags=TAGS_WAY + [('zoom', job.zoom.zoom)]
        )
        for r in ranges
    ]

def _osm_node(tile: tuple[int, int], job: Job) -> Node:
    return Node(node_id=job.next_id(), geom=job.zoom.to_point(tile))


def generate_osm(job: Job):
    """Generate a single OSM file for a job"""
    logger.info('Generating OSM: %s -> %s', job, job.osm_file)

    with timeit(f'{job}: generate_tiles'):
        ranges = generate_ranges(poly=job.region.coords, job=job)

    # logger.debug('%s: %d tiles', job, sum(map(len, tiles.values())))

    with timeit(f'{job}: generate_grid_for_ranges'):
        ways = generate_grid(ranges=ranges, job=job)

    logger.debug('%s: %d ways', job, len(ways))

    unique_nodes = set()
    with timeit(f'{job}: collect unique nodes'):
        for w in ways:
            unique_nodes.update(w.nodes)

    logger.debug('%s: %d unique nodes', job, len(unique_nodes))

    with timeit(f'{job}: build OSM document'):
        document = ET.Element("osm", {"version": '0.6'})
        document.extend(n.to_xml() for n in sorted(unique_nodes, key=lambda node: node.element_id))
        document.extend(w.to_xml() for w in sorted(ways, key=lambda way: way.element_id))
        ET.indent(document)

    with timeit(f'{job}: write OSM document {job.osm_file}'):
        job.osm_file.parent.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(document).write(job.osm_file, encoding='utf-8', xml_declaration=True)
