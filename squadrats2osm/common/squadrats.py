from collections import defaultdict
from typing import NamedTuple

from common.poly import Coordinates
from common.poly import Poly
from common.tile import Tile
from common.zoom import Zoom

class UnexpectedBoundaryException(Exception):
    """Raised when unexpected Boundary is found
    """
    pass

class Boundary(NamedTuple):
    """Representation of the geographical coordinates
    
    Attributes
    ----------
    lr : int
        'L' or 'R' boundary
    y : int
        y coordinate of a tile
    lon : float
        westmost (for 'L') or eastmost (for 'R') longitude
    """
    lr: int
    y: int
    lon: float


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
    (coordinatesA, coordinatesB) = [zoom.tile(lat = point.lat, lon = point.lon) for point in (a, b)]
    minY = min(coordinatesA[1], coordinatesB[1])
    maxY = max(coordinatesA[1], coordinatesB[1])

    if dLat < 0 :
        # southward
        for y in range(minY, maxY + 1):
            lon1: float = None
            lon2: float = None

            if y == minY:
                lon1 = a.lon
            else:
                lon1 = line_intersection(a = a, b = b, lat = zoom.lat(y))

            if y == maxY:
                lon2 = b.lon
            else:
                lon2 = line_intersection(a = a, b = b, lat = zoom.lat(y + 1))

            lon = max(lon1, lon2)

            boundaries.append(Boundary('R', y, lon))

    elif dLat > 0 :
        # northward
        for y in range(minY, maxY + 1):
            lon1: float = None
            lon2: float = None

            if y == minY:
                lon1 = b.lon
            else:
                lon1 = line_intersection(a = a, b = b, lat = zoom.lat(y))

            if y == maxY:
                lon2 = a.lon
            else:
                lon2 = line_intersection(a = a, b = b, lat = zoom.lat(y + 1))

            lon = min(lon1, lon2)

            boundaries.append(Boundary('L', y, lon))
    
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

def generate_tiles(poly: Poly, zoom: Zoom) -> list[Tile]:
    """Generate a list of tiles of a given zoom covering the entire polygon
    """

    # return poly.generate_tiles(zoom=zoom)

    tiles: list[Tile] = []
    tilesDict = defaultdict(list)

    contours: list[Boundary] = generate_contour_for_polygon(poly=poly, zoom=zoom)
    for boundary in contours:
        tilesDict[boundary.y].append(boundary)

    for row in tilesDict.values():
        tiles.extend(_generate_tiles_for_a_row(row=row, zoom=zoom))

    return tiles

def _generate_tiles_for_a_row(row: list[Boundary], zoom: Zoom) -> list[Tile]:
    tiles: list[Tile] = []

    if (len(row) > 0):
        # sort the list by longitude
        row.sort(key=lambda b: b.lon)

        west: Boundary = None
        east: Boundary = None

        for b in row:
            if b.lr == 'L':
                if west is None:
                    west = b
                elif east is not None:
                    tiles.extend(_generate_tile_range(west=west, east=east, zoom=zoom))
                    west = b
                    east = None
            elif b.lr == 'R':
                east = b

        if east is not None:
            tiles.extend(_generate_tile_range(west=west, east=east, zoom=zoom))

    return tiles


def _generate_tile_range(west: Boundary, east: Boundary, zoom: Zoom):
    
    if west is None:
        raise UnexpectedBoundaryException('West boundary not set')

    if east is None:
        raise UnexpectedBoundaryException('East boundary not set')

    if west.y != east.y:
        raise UnexpectedBoundaryException('Boundaries on a different row. west={}, east={}'.format(west, east))

    lat = zoom.lat(west.y)
    (westX, westY) = zoom.tile(lat=lat, lon=west.lon)
    (eastX, eastY) = zoom.tile(lat=lat, lon=east.lon)

    return [Tile(x=x, y=west.y, zoom=zoom) for x in range(westX, eastX + 1)]


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