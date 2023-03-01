from collections import defaultdict
import itertools
import re
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

class BoundingBox:
    """Bounding box for a polygon
    """
    def __init__(self, n, e, s, w):
        self.n = n
        self.e = e
        self.s = s
        self.w = w

    def __repr__(self) -> str:
        """Overrides the default implementation
        """
        return 'N {}; E {}; S {}; W {};'.format(self.n, self.e, self.s, self.w)

    def __eq__(self, __o: object) -> bool:
        """Overrides the default implementation
        """
        if isinstance(__o, BoundingBox):
            return (self.n == __o.n and 
                self.e == __o.e and
                self.s == __o.s and
                self.w == __o.w)
        return False

class Poly:
    """Polygon definition
    """
    def __init__(self, filename):
        with open(filename) as f:
            self.coords = self.__read_poly_file(f)

        self.bounding_box = self.__calculate_bounding_box(self.coords)

    def generate_tiles(self, zoom: int):
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

        for l1 in file:
            l1 = l1.strip()
            if (l1 == 'END'): break
            for l2 in file:
                l2 = l2.strip()
                if (l2 == 'END'): break
                coords.append([float(s) for s in re.split('\s+', l2)])

        return coords

    def __calculate_bounding_box(self, coords) -> BoundingBox:
        """Calculate bounding box for a given set of coordinates
        """
        n = -90
        s = 90
        e = -180
        w = 180
        for point in coords:
            n = max(n, point[0])
            s = min(s, point[0])
            e = max(e, point[1])
            w = min(w, point[1])

        return BoundingBox(n, e, s, w)

    def __generate_tiles_by_bounding_box(self, zoom: int):
        """Generate tiles for the rectangular area defined by the polygon bounding box
        """
        tile_nw = Tile.tile_at((self.bounding_box.n, self.bounding_box.w), zoom)
        tile_se = Tile.tile_at((self.bounding_box.s, self.bounding_box.e), zoom)
        tiles = []

        for y in range(tile_nw.y, tile_se.y + 1):
            for x in range(tile_nw.x, tile_se.x + 1):
                tiles.append(Tile(x, y, zoom))

        return tiles

    def __generate_tiles_by_poly(self, zoom: int):
        """Generate minimal set of tiles overlapping with the polygon
        """
        tiles = []

        return tiles


    def __generate_tiles_by_outline(self, zoom: int):
        """Generate tiles 
        """
        tiles = []
        tilesL = []
        tilesR = []
        pointA = None
        for pointB in self.coords:
            if pointA is not None:
                (dX, dY) = (pointB[1] - pointA[1], pointB[0] - pointA[0])
                if dY < 0:
                    # direction south
                    tilesL.extend(_generate_tiles_along_the_line(pointA, pointB, zoom))
                elif (dY > 0):
                    # direction north
                    tilesR.extend(_generate_tiles_along_the_line(pointA, pointB, zoom))

            pointA = pointB

        tileMinY = min(tile.y for tile in itertools.chain(tilesL, tilesR))
        tileMaxY = max(tile.y for tile in itertools.chain(tilesL, tilesR))

        tilesLDict = defaultdict(list)
        tilesRDict = defaultdict(list)

        for tile in tilesL:
            tilesLDict[tile.y].append(tile)

        for tile in tilesR:
            tilesRDict[tile.y].append(tile)

        return tiles


def _generate_tiles_along_the_line(pointA: tuple[int], pointB: tuple[int], zoom: int):
    """Redirect to the proper method
    """
    return _generate_tiles_along_the_line_simple_vertical(pointA, pointB, zoom)

def _generate_tiles_along_the_line_simple_vertical(pointA: tuple[int], pointB: tuple[int], zoom: int):
    """Generate tiles along the line - generates vertical line for the outmost tile
    """
    (dX, dY) = (pointB[1] - pointA[1], pointB[0] - pointA[0])
    if dX == 0 and dY == 0:
        """not an actual line - point"""
        return []

    (tileA, tileB) = (Tile.tile_at(point, zoom) for point in (pointA, pointB))

    if dY < 0:
        """Direction south - generate westmost vertical line of tiles"""
        x = min(tileA.x, tileB.x)
        return (Tile(x, y, zoom) for y in range(tileA.y, tileB.y + 1))

    elif dY > 0:
        """Direction north - generate eastmost vertical line of tiles"""
        x = max(tileA.x, tileB.x)
        return (Tile(x, y, zoom) for y in range(tileB.y, tileA.y + 1))

    else:
        """horizontal line"""
        return []