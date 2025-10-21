import logging
import xml.etree.ElementTree as ET

from collections import defaultdict
from typing import NamedTuple

from common import util
from common.geo import Coordinates
from common.job import Job
from common.osm import Node, Way
from common.poly import Poly
from common.tile import Tile
from common.timer import timeit
from common.zoom import Zoom

TAGS_WAY = [('name', 'grid')]

logger = logging.getLogger(__name__)

class UnexpectedBoundaryException(Exception):
    """Raised when an unexpected Boundary is found
    """
    pass

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


def generate_tiles(poly: Poly, job: Job) -> dict[int, list[Tile]]:
    """Generate a list of tiles of a given zoom covering the entire polygon
    """
    contour_tiles = defaultdict(list)

    with timeit(f'{job}: generate contours'):
        contours: list[Boundary] = generate_contour_for_polygon(poly=poly, job=job)
        for boundary in contours:
            contour_tiles[boundary.y].append(boundary)

    with timeit(f'{job}: fill contours'):
        return dict(map(lambda k_v:(k_v[0], _generate_tiles_for_a_row(row=k_v[1], job=job)), contour_tiles.items()))

def line_intersection(a: Coordinates, b: Coordinates, lat: float) -> float:
    """Intersection of a line with a horizontal gridline
    """
    return (a.lon * (b.lat - lat) - b.lon * (a.lat - lat)) / (b.lat - a.lat)


def line_grid_intersections(a: Coordinates, b: Coordinates, zoom: Zoom) -> list[Boundary]:
    """Calculate intersections of a line with the grid

    Parameters
    ----------
    a : Coordinates
        line beginning
    b : Coordinates
        line end
    zoom : Zoom
        zoom
    """

    boundaries: list[Boundary] = []

    dLat = b.lat - a.lat
    (tileA, tileB) = [zoom.tile(lat = point.lat, lon = point.lon) for point in (a, b)]
    minY = min(tileA[1], tileB[1])
    maxY = max(tileA[1], tileB[1])

    if dLat < 0:
        # southward
        for y in range(minY, maxY + 1):
            lon1: float = None
            lon2: float = None

            if y == minY:
                lon1 = a.lon
            else:
                lon1 = line_intersection(a = a, b = b, lat = zoom.lat(y)) if lon2 is None else lon2

            if y == maxY:
                lon2 = b.lon
            else:
                lon2 = line_intersection(a = a, b = b, lat = zoom.lat(y + 1))

            boundaries.append(Boundary('R', y, max(lon1, lon2)))

    elif dLat > 0:
        # northward
        for y in range(minY, maxY + 1):
            lon1: float = None
            lon2: float = None

            if y == minY:
                lon1 = b.lon
            else:
                lon1 = line_intersection(a = a, b = b, lat = zoom.lat(y)) if lon2 is None else lon2

            if y == maxY:
                lon2 = a.lon
            else:
                lon2 = line_intersection(a = a, b = b, lat = zoom.lat(y + 1))

            boundaries.append(Boundary('L', y, min(lon1, lon2)))
    
    elif dLat == 0:
        y = minY
        minX = min(tileA[1], tileB[1])
        maxX = max(tileA[1], tileB[1])

        lon1: float = None
        lon2: float = None

        for x in range(minX, maxX + 1):
            if x == minX:
                lon1 = min(a.lon, b.lon)
            else:
                lon1 = zoom.lon(x) if lon2 is None else lon2
                
            if x == maxX:
                lon2 = max(a.lon, b.lon)
            else:
                lon2 = zoom.lon(x + 1)

            boundaries.append(Boundary('L', y, lon1))
            boundaries.append(Boundary('R', y, lon2))

    return boundaries

def generate_contour_for_polygon_area(poly_area: list[Coordinates], zoom: Zoom) -> list[Boundary]:
    boundaries: list[Boundary] = []
    point_a: Coordinates = None
    for point_b in poly_area:
        if point_a is not None:
            boundaries.extend(line_grid_intersections(a=point_a, b=point_b, zoom=zoom))
        point_a = point_b

    return boundaries

def generate_contour_for_polygon(poly: Poly, job: Job) -> list[Boundary]:
    return [b for area in poly.coords for b in generate_contour_for_polygon_area(poly_area=area, zoom=job.zoom)]

def _generate_tiles_for_a_row(row: list[Boundary], job: Job) -> list[Tile]:
    # sort the list by longitude and LR (important in case of the same longitude the L boundary needs preceed the R boundary)
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

    return [Tile(x=x, y=row[0].y, zoom=zoom) for x in list(tiles_x)]


def _generate_tile_range(west: Boundary, east: Boundary, zoom: Zoom) -> list[int]:
    
    if west is None:
        raise UnexpectedBoundaryException('West boundary not set')

    if east is None:
        raise UnexpectedBoundaryException('East boundary not set')

    if west.y != east.y:
        raise UnexpectedBoundaryException('Boundaries on a different row. west={}, east={}'.format(west, east))

    lat = zoom.lat(west.y)
    (westX, westY) = zoom.tile(lat=lat, lon=west.lon)
    (eastX, eastY) = zoom.tile(lat=lat, lon=east.lon)

    return range(westX, eastX + 1)


def _generate_tiles_by_bounding_box(poly: Poly, zoom: Zoom):
    """Generate tiles for the rectangular area defined by the polygon bounding box
    """
    tile_nw = Tile.tile_at(poly.bounding_box.n, poly.bounding_box.w, zoom)
    tile_se = Tile.tile_at(poly.bounding_box.s, poly.bounding_box.e, zoom)
    tiles = []

    for y in range(tile_nw.y, tile_se.y + 1):
        for x in range(tile_nw.x, tile_se.x + 1):
            tiles.append(Tile(x, y, zoom))

    return tiles

def node_cache_get_or_compute(nodeCache: dict, x, y, zoom) -> Node:
    k = (x, y)
    if k in nodeCache:
        return nodeCache[k]
    else:
        node = _osm_node(x, y, zoom)
        nodeCache[k] = node
        return node

def generate_grid(tiles: dict[int, list[Tile]], job: Job) -> list[Way]:

    if not tiles: return []

    ways: list[Way] = []

    # sort tiles by y, x
    tilesByY = tiles

    # find the horizontal ranges
    rangesByY = {y: util.make_ranges_end_inclusive(util.find_ranges(sorted([tile.x for tile in row]))) for (y, row) in tilesByY.items()}

    # generate horizontal lines
    prevY = None
    for y in sorted(rangesByY.keys()):
        if prevY is None or prevY + 1 != y:
            # first row or a gap - generate top edge
            ways.extend(_create_horizontal_ways_for_ranges(y=y, ranges=rangesByY[y], job=job))
        
        if y + 1 in rangesByY:
            # generate bottom edge between current and next row
            ways.extend(_create_horizontal_ways_for_ranges(y=y + 1, ranges=util.merge_ranges(rangesByY[y] + rangesByY[y + 1]), job=job))
        else:
            # generate bottom edge when next row is empty    
            ways.extend(_create_horizontal_ways_for_ranges(y=y + 1, ranges=rangesByY[y], job=job))

        prevY = y

    # sort tiles by x, y
    tilesByX = defaultdict(list)
    for row in tiles.values():
        for tile in row:
            tilesByX[tile.x].append(tile)

    # find the vertical ranges
    rangesByX = {x: util.make_ranges_end_inclusive(util.find_ranges(sorted([tile.y for tile in column]))) for (x, column) in tilesByX.items()}

    # generate vertical lines
    prevX = None
    for x in sorted(rangesByX.keys()):
        if prevX is None or prevX + 1 != x:
            # first column or a gap - generate left edge
            ways.extend(_create_vertical_ways_for_ranges(x=x, ranges=rangesByX[x], job=job))
        
        if x + 1 in rangesByX:
            # generate right edge between current and next column
            ways.extend(_create_vertical_ways_for_ranges(x=x + 1, ranges=util.merge_ranges(rangesByX[x] + rangesByX[x + 1]), job=job))
        else:
            # generate right edge when next column is empty    
            ways.extend(_create_vertical_ways_for_ranges(x=x + 1, ranges=rangesByX[x], job=job))

        prevX = x

    return ways

def _create_horizontal_ways_for_ranges(y: int, ranges: list[tuple[int, int]], job: Job) -> list[Way]:
    if not ranges:
        return []
    
    ways: list[Way] = []

    for range in ranges:
        (node1, node2) = (_osm_node(x, y, job) for x in range)
        ways.append(Way(id=job.next_id(), nodes=[node1, node2], tags=[*TAGS_WAY, ('zoom', job.zoom.zoom)]))

    return ways

def _create_vertical_ways_for_ranges(x: int, ranges: list[tuple[int, int]], job: Job) -> list[Way]:
    if not ranges:
        return []
    
    ways: list[Way] = []

    for range in ranges:
        (node1, node2) = (_osm_node(x, y, job) for y in range)
        ways.append(Way(id=job.next_id(), nodes=[node1, node2], tags=[*TAGS_WAY, ('zoom', job.zoom.zoom)]))

    return ways


def _osm_node(x: int, y: int, job: Job) -> Node:
    return Node(id=job.next_id(), lon=job.zoom.lon(x), lat=job.zoom.lat(y))


def generate_osm(job: Job):
    logger.info(f'Generating OSM: {job} -> {job.osm_file}')

    with timeit(f'{job}: generate_tiles'):
        tiles = generate_tiles(poly=job.region.poly, job=job)

    logger.debug(f'{job}: {sum(map(len, tiles.values()))} tiles')

    with timeit(f'{job}: generate_grid'):
        ways = generate_grid(tiles=tiles, job=job)

    logger.debug(f'{job}: {len(ways)} ways')

    unique_nodes = set()
    with timeit(f'{job}: collect unique nodes'):
        for w in ways:
            unique_nodes.update(w.nodes)

    logger.debug(f'{job}: {len(unique_nodes)} unique nodes')

    with timeit(f'{job}: build OSM document'):
        document = ET.Element("osm", {"version": '0.6'})
        document.extend(n.to_xml() for n in sorted(unique_nodes, key=lambda node: node.id))
        document.extend(w.to_xml() for w in sorted(ways, key=lambda way: way.id))
        ET.indent(document)

    with timeit(f'{job}: write OSM document {job.osm_file}'):
        job.osm_file.parent.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(document).write(job.osm_file, encoding='utf-8', xml_declaration=True)
