import logging
import xml.etree.ElementTree as ET

from collections import defaultdict

from pygeoif import MultiPolygon
from pygeoif.geometry import Point, Polygon
from typing import NamedTuple

from common import util
from common.job import Job
from common.osm import Node, Way
from common.tile import Tile, Zoom
from common.timer import timeit

TAGS_WAY = [('name', 'grid')]

logger = logging.getLogger(__name__)

class UnexpectedBoundaryException(Exception):
    """Raised when an unexpected Boundary is found
    """

class Boundary(NamedTuple):
    """Representation of the geographical coordinates
    
    Attributes
    ----------
    lr : str
        'L' or 'R' boundary
    y : int
        y coordinate of a tile
    lon : float
        westmost (for 'L') or eastmost (for 'R') longitude
    """
    lr: str
    y: int
    lon: float


def generate_tiles(poly: MultiPolygon, job: Job) -> dict[int, list[Tile]]:
    """Generate a list of tiles of a given zoom covering the entire polygon
    """
    contour_tiles = defaultdict(list)

    with timeit(f'{job}: generate contours'):
        contours: list[Boundary] = generate_contour_for_multipolygon(multipolygon=poly, job=job)
        for boundary in contours:
            contour_tiles[boundary.y].append(boundary)

    with timeit(f'{job}: fill contours'):
        return dict(map(lambda k_v:(k_v[0], _generate_tiles_for_a_row(row=k_v[1], job=job)),
                        contour_tiles.items()))

def line_intersection(a: Point, b: Point, lat: float) -> float:
    """Intersection of a line with a horizontal gridline
    """
    return (a.x * (b.y - lat) - b.x * (a.y - lat)) / (b.y - a.y)


def line_grid_intersections(a: Point, b: Point, zoom: Zoom) -> list[Boundary]:
    """Calculate intersections of a line with the grid

    Parameters
    ----------
    a : Point
        line beginning
    b : Point
        line end
    zoom : Zoom
        zoom
    """

    boundaries: list[Boundary] = []

    lat_delta = b.y - a.y
    (tile_a, tile_b) = [zoom.point_to_tile(point) for point in (a, b)]
    min_y = min(tile_a.y, tile_b.y)
    max_y = max(tile_a.y, tile_b.y)

    if lat_delta < 0:
        # southward
        for y in range(min_y, max_y + 1):
            lon1: float = None
            lon2: float = None

            if y == min_y:
                lon1 = a.x
            else:
                lon1 = line_intersection(a = a, b = b, lat = zoom.lat(y)) if lon2 is None else lon2

            if y == max_y:
                lon2 = b.x
            else:
                lon2 = line_intersection(a = a, b = b, lat = zoom.lat(y + 1))

            boundaries.append(Boundary('R', y, max(lon1, lon2)))

    elif lat_delta > 0:
        # northward
        for y in range(min_y, max_y + 1):
            lon1: float = None
            lon2: float = None

            if y == min_y:
                lon1 = b.x
            else:
                lon1 = line_intersection(a = a, b = b, lat = zoom.lat(y)) if lon2 is None else lon2

            if y == max_y:
                lon2 = a.x
            else:
                lon2 = line_intersection(a = a, b = b, lat = zoom.lat(y + 1))

            boundaries.append(Boundary('L', y, min(lon1, lon2)))

    elif lat_delta == 0:
        y = min_y
        min_x = min(tile_a[1], tile_b[1])
        max_x = max(tile_a[1], tile_b[1])

        lon1: float = None
        lon2: float = None

        for x in range(min_x, max_x + 1):
            if x == min_x:
                lon1 = min(a.x, b.x)
            else:
                lon1 = zoom.lon(x) if lon2 is None else lon2

            if x == max_x:
                lon2 = max(a.x, b.x)
            else:
                lon2 = zoom.lon(x + 1)

            boundaries.append(Boundary('L', y, lon1))
            boundaries.append(Boundary('R', y, lon2))

    return boundaries

def generate_contour_for_polygon(polygon: Polygon, zoom: Zoom) -> list[Boundary]:
    boundaries: list[Boundary] = []
    point_a: Point = None
    for point_b in polygon.exterior.geoms:
        if point_a is not None:
            boundaries.extend(line_grid_intersections(a=point_a, b=point_b, zoom=zoom))
        point_a = point_b

    return boundaries


def generate_contour_for_multipolygon(multipolygon: MultiPolygon, job: Job) -> list[Boundary]:
    return [
        b
        for area in multipolygon.geoms
        for b in generate_contour_for_polygon(polygon=area, zoom=job.zoom)
    ]

def _generate_tiles_for_a_row(row: list[Boundary], job: Job) -> list[Tile]:
    # sort the list by longitude and LR
    # (important in case of the same longitude the L boundary needs to preceed the R boundary)
    row.sort(key=lambda b: (b.lon, 0 if b.lr == 'R' else 1))
    return _generate_tiles_for_a_sorted_row(row=row, zoom=job.zoom)

def _generate_tiles_for_a_sorted_row(row: list[Boundary], zoom: Zoom) -> list[Tile]:
    if len(row) == 0:
        return []

    tiles_x: set[int] = set()
    west: Boundary = None
    east: Boundary = None

    for b in row:
        if b.lr == 'L':
            if west is None:
                west = b
            elif east is not None:
                tiles_x.update(_generate_tile_range(west=west, east=east, zoom=zoom))
                west = b
                east = None
        elif b.lr == 'R':
            east = b

    if east is not None:
        tiles_x.update(_generate_tile_range(west=west, east=east, zoom=zoom))

    return [Tile(x, row[0].y) for x in list(tiles_x)]


def _generate_tile_range(west: Boundary, east: Boundary, zoom: Zoom) -> list[int]:
    if west is None:
        raise UnexpectedBoundaryException('West boundary not set')

    if east is None:
        raise UnexpectedBoundaryException('East boundary not set')

    if west.y != east.y:
        raise UnexpectedBoundaryException(
            f'Boundaries on a different row. west={west}, east={east}'
        )

    lat = zoom.lat(west.y)
    (west_x, west_y) = zoom.point_to_tile(Point(west.lon, lat))
    (east_x, east_y) = zoom.point_to_tile(Point(east.lon, lat))

    return range(west_x, east_x + 1)


def _generate_tiles_by_bounding_box(poly: MultiPolygon, zoom: Zoom):
    """Generate tiles for the rectangular area defined by the polygon bounding box
    """
    bounds = poly.bounds
    tile_nw = zoom.point_to_tile(Point(x=bounds[0], y=bounds[3]))
    tile_se = zoom.point_to_tile(Point(x=bounds[2], y=bounds[1]))
    tiles = []

    for y in range(tile_nw.y, tile_se.y + 1):
        for x in range(tile_nw.x, tile_se.x + 1):
            tiles.append(Tile(x, y))

    return tiles

def generate_grid(tiles: dict[int, list[Tile]], job: Job) -> list[Way]:
    if not tiles:
        return []

    ways: list[Way] = []

    # sort tiles by y, x
    tiles_by_y = tiles

    # find the horizontal ranges
    ranges_by_y = {
        y: util.make_ranges_end_inclusive(util.find_ranges(sorted([tile.x for tile in row])))
        for (y, row) in tiles_by_y.items()
    }

    # generate horizontal lines
    prev_y = None
    for y in sorted(ranges_by_y.keys()):
        if prev_y is None or prev_y + 1 != y:
            # first row or a gap - generate top edge
            ways.extend(_create_horizontal_ways_for_ranges(y=y, ranges=ranges_by_y[y], job=job))

        if y + 1 in ranges_by_y:
            # generate bottom edge between current and next row
            ways.extend(
                _create_horizontal_ways_for_ranges(
                    y=y + 1,
                    ranges=util.merge_ranges(ranges_by_y[y] + ranges_by_y[y + 1]),
                    job=job))
        else:
            # generate bottom edge when next row is empty
            ways.extend(_create_horizontal_ways_for_ranges(y=y + 1, ranges=ranges_by_y[y], job=job))

        prev_y = y

    # sort tiles by x, y
    tiles_by_x = defaultdict(list)
    for row in tiles.values():
        for tile in row:
            tiles_by_x[tile.x].append(tile)

    # find the vertical ranges
    ranges_by_x = {
        x: util.make_ranges_end_inclusive(util.find_ranges(sorted([tile.y for tile in column])))
        for (x, column) in tiles_by_x.items()
    }

    # generate vertical lines
    prev_x = None
    for x in sorted(ranges_by_x.keys()):
        if prev_x is None or prev_x + 1 != x:
            # first column or a gap - generate left edge
            ways.extend(_create_vertical_ways_for_ranges(x=x, ranges=ranges_by_x[x], job=job))

        if x + 1 in ranges_by_x:
            # generate right edge between current and next column
            ways.extend(
                _create_vertical_ways_for_ranges(
                    x=x + 1,
                    ranges=util.merge_ranges(ranges_by_x[x] + ranges_by_x[x + 1]),
                    job=job)
            )
        else:
            # generate right edge when next column is empty
            ways.extend(_create_vertical_ways_for_ranges(x=x + 1, ranges=ranges_by_x[x], job=job))

        prev_x = x

    return ways

def _create_horizontal_ways_for_ranges(y: int, ranges: list[tuple[int, int]], job: Job) -> list[Way]:
    if not ranges:
        return []

    ways: list[Way] = []

    for range in ranges:
        (node1, node2) = (_osm_node(Tile(x, y), job) for x in range)
        ways.append(
            Way(way_id=job.next_id(), nodes=[node1, node2], tags=TAGS_WAY + [('zoom', job.zoom.zoom)])
        )

    return ways

def _create_vertical_ways_for_ranges(x: int, ranges: list[tuple[int, int]], job: Job) -> list[Way]:
    if not ranges:
        return []

    ways: list[Way] = []

    for range in ranges:
        (node1, node2) = (_osm_node(Tile(x, y), job) for y in range)
        ways.append(
            Way(way_id=job.next_id(), nodes=[node1, node2], tags=TAGS_WAY + [('zoom', job.zoom.zoom)])
        )

    return ways


def _osm_node(tile: Tile, job: Job) -> Node:
    point = job.zoom.tile_to_point(tile)
    return Node(node_id=job.next_id(), geom=point.coords[0])


def generate_osm(job: Job):
    """Generate a single OSM file for a job"""
    logger.info('Generating OSM: %s -> %s', job, job.osm_file)

    with timeit(f'{job}: generate_tiles'):
        tiles = generate_tiles(poly=job.region.coords, job=job)

    logger.debug('%s: %d tiles', job, sum(map(len, tiles.values())))

    with timeit(f'{job}: generate_grid'):
        ways = generate_grid(tiles=tiles, job=job)

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
