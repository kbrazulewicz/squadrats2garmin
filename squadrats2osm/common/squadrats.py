from typing import NamedTuple

from common.poly import Coordinates
from common.tile import tile_coordinates
from common.tile import tile_lat

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

def line_intersections(pointA: Coordinates, pointB: Coordinates, zoom: int) -> list[Boundary]:
    """Calculate intersections of a line with the grid

    Parameters
    ----------
    pointA : Coordinates
        line beginning
    pointB : Coordinates
        line end
    """

    boundaries: list[Boundary] = []

    dLat = pointB.lat - pointA.lat
    (coordinatesA, coordinatesB) = [tile_coordinates(lat = point.lat, lon = point.lon, zoom = zoom) for point in (pointA, pointB)]
    minY = min(coordinatesA[1], coordinatesB[1])
    maxY = max(coordinatesA[1], coordinatesB[1])

    if dLat < 0 :
        # southward
        for y in range(minY, maxY + 1):
            lon1: float = None
            lon2: float = None

            if y == minY:
                lon1 = pointA.lon
            else    
                lon1 = line_intersection(pointA = pointA, pointB = pointB, lat = tile_lat(y = y, zoom = zoom))

            if y == maxY:
                lon2 = pointB.lon
            else    
                lon2 = line_intersection(pointA = pointA, pointB = pointB, lat = tile_lat(y = y + 1, zoom = zoom))

            lon = max(lon1, lon2)

            boundaries.append(Boundary('R', y, lon))

    elif dLat > 0 :
        # northward
        for y in range(minY, maxY + 1):
            lon1: float = None
            lon2: float = None

            if y == minY:
                lon1 = pointB.lon
            else    
                lon1 = line_intersection(pointA = pointA, pointB = pointB, lat = tile_lat(y = y, zoom = zoom))

            if y == maxY:
                lon2 = pointA.lon
            else    
                lon2 = line_intersection(pointA = pointA, pointB = pointB, lat = tile_lat(y = y + 1, zoom = zoom))

            lon = min(lon1, lon2)

            boundaries.append(Boundary('L', y, lon))
    
    return boundaries


def line_intersection(pointA: Coordinates, pointB: Coordinates, lat: float)
    """Intersection of a line with a horizontal gridline"""
    return (pointA.lon * (pointB.lat - lat) - pointB.lon * (pointA.lat - lat)) / (pointB.lat - pointA.lat)


def _generate_tiles_along_the_line(pointA: Coordinates, pointB: Coordinates, zoom: int):
    """Generate tiles along the line
    """
    tiles: list[Tile] = []
    # tileA is the northernmost tile of the range, tileB is the southernmost tile of the range (but not necessarily the nothern/southern end of the line)
    (tileA, tileB) = sorted([Tile.tile_at(lat = point.lat, lon = point.lon, zoom = zoom) for point in (pointA, pointB)], key=lambda tile:tile.y)

    # x1 is the Tile.x of the northern end of line
    x1: int = tileA.x
    x2: int = None
    # starting from the second row
    for y in range(tileA.y + 1, tileB.y + 1):
        # TODO calculate longitude where tile latitude intersects with the line
        tile1 = Tile(x = x1, y = y, zoom = zoom)
        lon = line_intersection(pointA = pointA, pointB = pointB, tile1.lat)
        tile2 = Tile.tile_at(lon = lon, lat = lat, zoom = zoom)
        x2 = tile2.x
        # list of tiles overlapping in the y - 1 row
        tiles.extend(Tile(x, y - 1, zoom) for x in range(min(x1, x2), max(x1, x2) + 1))
        x1 = x2

    # add last row
    tiles.extend(Tile(x, tileB.y, zoom) for x in range(min(x1, tileB.x), max(x1, tileB.x) + 1))
    
    return tiles