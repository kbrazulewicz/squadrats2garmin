import itertools
from collections import defaultdict
from typing import NamedTuple

from common.tile import Tile


class PolyFileFormatException(Exception):
    """Raised when POLY file has an incorrect format
    """
    pass

class PolyFileIncorrectFiletypeException(PolyFileFormatException):
    """Raised when POLY file has an incorrect filetype
    """
    def __init__(self, filetype) -> None:
        self.filetype = filetype
        super().__init__('Expecting polygon filetype, got "{}" instead'.format(filetype))

class BoundingBox(NamedTuple):
    """Bounding box for a polygon
    """
    n: float
    e: float
    s: float
    w: float
    
class Coordinates(NamedTuple):
    """Representation of the geographical coordinates
    
    Attributes
    ----------
    lat : float
        latitute
    lon : float
        longitude
    """
    lat: float
    lon: float

class Poly:
    """Polygon definition

    POLY file contains lines with longitude and latitude of points creating polygon.
    Points are ordered clockwise
    https://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format

    Attributes
    ----------
    coords : list[list[Coordinates]]
        list of polygons
    """

    coords: list[list[Coordinates]]

    def __init__(self, filename):
        with open(filename) as f:
            self.coords = self.__read_poly_file(f)

        self.bounding_box = self.__calculate_bounding_box()

    def generate_tiles(self, zoom: int) -> list[Tile]:
        """Generate a list of tiles of a given zoom covering the entire polygon
        """
        return self.__generate_tiles_by_poly(zoom)

    def generate_tiles_by_bounding_box(self, zoom: int):
        """Generate a list of tiles of a given zoom covering the entire polygon
        """
        return self.__generate_tiles_by_bounding_box(zoom)


    def __read_poly_file(self, file):
        """Read contents of the POLY file
        """
        filetype = file.readline().rstrip('\n')
        if (filetype != 'polygon'):
            raise PolyFileIncorrectFiletypeException(filetype)

        coords = []

        for line in file:
            line = line.strip()
            if line == 'END': break
            if line.startswith('!'): 
                """ ignore holes in the polygon """
                self.__read_polygon(file)
            else:
                coords.append(self.__read_polygon(file))

        return coords

    def __read_polygon(self, file):
        """Read single polygon section
        """
        coords = []

        for line in file:
            line = line.strip()
            if (line == 'END'): break
            (poly_lon, poly_lat) = (map(float, line.split()))
            coords.append(Coordinates(lat = poly_lat, lon = poly_lon))

        return coords

    def __calculate_bounding_box(self) -> BoundingBox:
        """Calculate bounding box for a given set of coordinates
        """
        n = -90
        s = 90
        e = -180
        w = 180
        for poly in self.coords:
            for point in poly:
                n = max(n, point.lat)
                s = min(s, point.lat)
                e = max(e, point.lon)
                w = min(w, point.lon)

        return BoundingBox(n = n, e = e, s = s, w = w)

    def __generate_tiles_by_bounding_box(self, zoom: int):
        """Generate tiles for the rectangular area defined by the polygon bounding box
        """
        tile_nw = Tile.tile_at(self.bounding_box.n, self.bounding_box.w, zoom)
        tile_se = Tile.tile_at(self.bounding_box.s, self.bounding_box.e, zoom)
        tiles = []

        for y in range(tile_nw.y, tile_se.y + 1):
            for x in range(tile_nw.x, tile_se.x + 1):
                tiles.append(Tile(x, y, zoom))

        return tiles

    def __generate_tiles_by_poly(self, zoom: int) -> list[Tile]:
        """Generate minimal set of tiles overlapping with the polygon
        """
        tiles: list[Tile] = []
        for poly in self.coords:
            tilesL: list[Tile] = []
            tilesR: list[Tile] = []
            pointA = None
            for pointB in poly:
                if pointA is not None:
                    (dLat, dLon) = (pointB.lat - pointA.lat, pointB.lon - pointA.lon)
                    if dLat < 0:
                        # direction south (clockwise)
                        tilesR.extend(_generate_tiles_along_the_line(pointA, pointB, zoom))
                    elif (dLat > 0):
                        # direction north (clockwise)
                        tilesL.extend(_generate_tiles_along_the_line(pointA, pointB, zoom))

                pointA = pointB

            tileMinY = min(tile.y for tile in itertools.chain(tilesL, tilesR))
            tileMaxY = max(tile.y for tile in itertools.chain(tilesL, tilesR))

            tilesDict = defaultdict(list)

            # dictionary[y coordinate] of lists containing tuples(x coordinate, L|R)
            # it is important that 'L' < 'R'
            for tile in tilesL:
                tilesDict[tile.y].append((tile.x, 'L'))

            for tile in tilesR:
                tilesDict[tile.y].append((tile.x, 'R'))

            for y in range(tileMinY, tileMaxY + 1):
                tiles.extend(self.__generate_tiles_for_a_row(tilesDict[y], y, zoom))

        return tiles
    
    def __generate_tiles_for_a_row(self, row: list, y: int, zoom: int) -> list[Tile]:
        tiles: list[Tile] = []

        if (len(row) > 0):
            # sort the lists
            row.sort(key=lambda tup: (tup[0],tup[1]))

            # get the list and traverse it
            inside = False
            for x in range(row[0][0], row[-1][0] + 1):
                (tileX, tileLR) = row[0]
                # print(f'x: {x}; tileX: {tileX}; tileLR: {tileLR}; inside: {inside}')
                if x == tileX:
                    if tileLR == 'L': inside = True
                    if tileLR == 'R': inside = False
                    row.pop(0)
                    tiles.append(Tile(x, y, zoom))
                elif inside:
                    tiles.append(Tile(x, y, zoom))

        return tiles


def _generate_tiles_along_the_line_simple_vertical(pointA: Coordinates, pointB: Coordinates, zoom: int):
    """Generate tiles along the line - generates vertical line for the outmost tile
    """
    (dLat, dLon) = (pointB.lat - pointA.lat, pointB.lon - pointA.lon)
    if dLon == 0 and dLat == 0:
        # not an actual line - point
        return []
    
    if dLat == 0:
        # horizontal line
        return []

    (tileA, tileB) = (Tile.tile_at(lat = point.lat, lon = point.lon, zoom = zoom) for point in (pointA, pointB))

    x = None
    if dLat < 0:
        # direction south - generate eastmost vertical line of tiles
        x = max(tileA.x, tileB.x)
    else:
        # direction north - generate westmost vertical line of tiles
        x = min(tileA.x, tileB.x)
    
    return [Tile(x, y, zoom) for y in range(min(tileA.y, tileB.y), max(tileA.y, tileB.y) + 1)]


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
        lat = tile1.lat
        lon = (pointA.lon * (pointB.lat - lat) - pointB.lon * (pointA.lat - lat)) / (pointB.lat - pointA.lat)
        tile2 = Tile.tile_at(lon = lon, lat = lat, zoom = zoom)
        x2 = tile2.x
        # list of tiles overlapping in the y - 1 row
        tiles.extend(Tile(x, y - 1, zoom) for x in range(min(x1, x2), max(x1, x2) + 1))
        x1 = x2

    # add last row
    tiles.extend(Tile(x, tileB.y, zoom) for x in range(min(x1, tileB.x), max(x1, tileB.x) + 1))
    
    return tiles