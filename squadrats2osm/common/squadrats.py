from collections import defaultdict
from typing import NamedTuple

from common import osm
from common import util
from common.geo import Coordinates
from common.id import Id
from common.job import Job
from common.osm import Node, Way
from common.poly import Poly
from common.tile import Tile
from common.timer import timeit
from common.zoom import Zoom

TAGS_WAY = [('name', 'grid')]

class UnexpectedBoundaryException(Exception):
    """Raised when unexpected Boundary is found
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

    contourTiles = defaultdict(list)

    with timeit(f'{job.id}: generate contours'):
        contours: list[Boundary] = generate_contour_for_polygon(poly=poly, zoom=job.zoom)
        for boundary in contours:
            contourTiles[boundary.y].append(boundary)

    with timeit(f'{job.id}: fill contours'):
        return dict(map(lambda k_v:(k_v[0], _generate_tiles_for_a_row(row=k_v[1], zoom=job.zoom)), contourTiles.items()))

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

def generate_contour_for_polygon_area(polyArea: list[Coordinates], zoom: Zoom) -> list[Boundary]:
    boundaries: list[Boundary] = []
    pointA: Coordinates = None
    for pointB in polyArea:
        if pointA is not None:
            boundaries.extend(line_grid_intersections(a = pointA, b = pointB, zoom = zoom))
        pointA = pointB

    return boundaries

def generate_contour_for_polygon(poly: Poly, zoom: Zoom) -> list[Boundary]:
    return [b for area in poly.coords for b in generate_contour_for_polygon_area(polyArea=area, zoom=zoom)]

def _generate_tiles_for_a_row(row: list[Boundary], zoom: Zoom) -> list[Tile]:
    # sort the list by longitude and LR (important in case of the same longitude the L boundary needs preceed the R boundary)
    row.sort(key=lambda b: (b.lon, 0 if b.lr == 'R' else 1))
    return _generate_tiles_for_a_sorted_row(row=row, zoom=zoom)

def _generate_tiles_for_a_sorted_row(row: list[Boundary], zoom: Zoom) -> list[Tile]:
    if len(row) == 0:
        return []

    tilesX: set[int] = set()
    west: Boundary = None
    east: Boundary = None

    for b in row:
        if b.lr == 'L':
            if west is None:
                west = b
            elif east is not None:
                tilesX.update(_generate_tile_range(west=west, east=east, zoom=zoom))
                west = b
                east = None
        elif b.lr == 'R':
            east = b

    if east is not None:
        tilesX.update(_generate_tile_range(west=west, east=east, zoom=zoom))

    return [Tile(x=x, y=row[0].y, zoom=zoom) for x in list(tilesX)]


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


def generate_grid_simple(tiles: list[Tile]) -> list[Way]:
    """Generate simple way consisting of 4 nodes for every tile"""

    # dictionary, key: (x,y) tuple, value : Tile
    nodesByXY = {}
    ways = []
    for tile in tiles:
        node1 = node_cache_get_or_compute(nodesByXY, tile.x, tile.y, tile.zoom)
        node2 = node_cache_get_or_compute(nodesByXY, tile.x + 1, tile.y, tile.zoom)
        node3 = node_cache_get_or_compute(nodesByXY, tile.x + 1, tile.y + 1, tile.zoom)
        node4 = node_cache_get_or_compute(nodesByXY, tile.x, tile.y + 1, tile.zoom)

        id = node1.id - osm.WAY_BASE_ID
        ways.append(Way(id, nodes = [node1, node2, node3, node4, node1], tags = [*TAGS_WAY, ('zoom', tile.zoom)]))

    return ways

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

    id = Id()

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
            ways.extend(_create_horizontal_ways_for_ranges(y = y, ranges = rangesByY[y], zoom = job.zoom))
        
        if y + 1 in rangesByY:
            # generate bottom edge between current and next row
            ways.extend(_create_horizontal_ways_for_ranges(y = y + 1, ranges = util.merge_ranges(rangesByY[y] + rangesByY[y + 1]), zoom = job.zoom))
        else:
            # generate bottom edge when next row is empty    
            ways.extend(_create_horizontal_ways_for_ranges(y = y + 1, ranges = rangesByY[y], zoom = job.zoom))

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
            ways.extend(_create_vertical_ways_for_ranges(x = x, ranges = rangesByX[x], zoom = job.zoom))
        
        if x + 1 in rangesByX:
            # generate right edge between current and next column
            ways.extend(_create_vertical_ways_for_ranges(x = x + 1, ranges = util.merge_ranges(rangesByX[x] + rangesByX[x + 1]), zoom = job.zoom))
        else:
            # generate right edge when next column is empty    
            ways.extend(_create_vertical_ways_for_ranges(x = x + 1, ranges = rangesByX[x], zoom = job.zoom))

        prevX = x

    return ways

def _create_horizontal_ways_for_ranges(y: int, ranges: list[tuple[int, int]], zoom: Zoom) -> list[Way]:
    if not ranges:
        return []
    
    ways: list[Way] = []

    for range in ranges:
        (node1, node2) = (_osm_node(x, y, zoom) for x in range)
        id = (node1.id - osm.WAY_BASE_ID) * 2
        ways.append(Way(id = id, nodes = [node1, node2], tags = [*TAGS_WAY, ('zoom', zoom.zoom)]))

    return ways

def _create_vertical_ways_for_ranges(x: int, ranges: list[tuple[int, int]], zoom: Zoom) -> list[Way]:
    if not ranges:
        return []
    
    ways: list[Way] = []

    for range in ranges:
        (node1, node2) = (_osm_node(x, y, zoom) for y in range)
        id = (node1.id - osm.WAY_BASE_ID) * 2 - 1
        ways.append(Way(id = id, nodes = [node1, node2], tags = [*TAGS_WAY, ('zoom', zoom.zoom)]))

    return ways


def _osm_node(x: int, y: int, zoom: Zoom) -> Node:
    tile_no = y * (zoom.n + 1) + x
    id = - (tile_no + 1)
    return Node(id=id, lon=zoom.lon(x), lat=zoom.lat(y));