"""Classes and methods to handle map tiles
"""
import math
from functools import cached_property
from typing import NamedTuple, Union

from pygeoif.geometry import Point

class TilePoint(NamedTuple):
    x: int
    y: int

class Tile:
    """Representation of a tile

    see https://wiki.openstreetmap.org/wiki/Zoom_levels
    """

    _coords: TilePoint
    """tile's coordinates"""
    _zoom: Zoom = None
    """tile's zoom level"""

    def __init__(self, coords: Union[TilePoint|tuple[int,int]], zoom: Zoom) -> None:
        if isinstance(coords, TilePoint):
            self._coords = coords
        else:
            self._coords = TilePoint(*coords)
        self._zoom = zoom

    def __repr__(self) -> str:
        """Overrides the default implementation
        """
        return f'Tile(coords={self._coords}, zoom={self._zoom})'

    def __key(self):
        # not including zoom because we do not expect existence of tiles
        # of different zooms at the same time
        return self._coords

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, __o: object) -> bool:
        """Overrides the default implementation
        """
        if isinstance(__o, Tile):
            return self.__key() == __o.__key()
        return NotImplemented

    @property
    def x(self) -> int:
        """tile's x coordinate"""
        return self._coords.x

    @property
    def y(self) -> int:
        """tile's y coordinate"""
        return self._coords.y

    @cached_property
    def lon(self) -> float:
        """tile's NW corner longitude"""
        return self._zoom.lon(self.x)

    @cached_property
    def lat(self) -> float:
        """tile's NW corner latitude"""
        return self._zoom.lat(self.y)

    @staticmethod
    def tile_at(point: Point, zoom: Zoom) -> Tile:
        """ Lon./lat. to tile numbers """
        return Tile(coords=zoom.tile(point), zoom=zoom)


class Zoom:
    """Representation of zoom on the OSM map

    see https://wiki.openstreetmap.org/wiki/Zoom_levels
    """

    zoom: int
    n: int

    def __init__(self, zoom: int) -> None:
        self.zoom = zoom
        self.n = 2 ** zoom

    def __repr__(self) -> str:
        """Override the default implementation
        """
        return f'Zoom(zoom={self.zoom})'

    def __hash__(self):
        return hash(self.zoom)

    def __eq__(self, __o: object) -> bool:
        """Override the default implementation
        """
        if isinstance(__o, Zoom):
            return self.zoom == __o.zoom
        return NotImplemented

    def geo_coords(self, point: TilePoint) -> Point:
        """Return the coordinates of the NW corner of the tile
        """
        return Point(
            x=point.x / self.n * 360.0 - 180.0,
            y=math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * point.y / self.n))))
        )

    def lat(self, y: int) -> float:
        """Return the latitude of the north edge of the tile with y coordinate
        """
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / self.n))))

    def lon(self, x: int) -> float:
        """Return the longitude of the west edge of the tile with x coordinate
        """
        return x / self.n * 360.0 - 180.0

    def tile(self, point: Point) -> TilePoint:
        """Return tile coordinates (x, y) for given latitude and longitude
        """
        tile_x = int((point.x + 180.0) / 360.0 * self.n)
        tile_y = int((1.0 - math.asinh(math.tan(math.radians(point.y))) / math.pi) / 2.0 * self.n)
        return TilePoint(tile_x, tile_y)

# number of tiles: 4^14 = 268 435 456
# number of nodes: (2^14 + 1)^2 = 268 468 225
ZOOM_SQUADRATS: Zoom = Zoom(zoom = 14)

# number of tiles: 4^17 = 17 179 869 184
# number of nodes: (2^17 + 1)^2 = 17 180 131 329
ZOOM_SQUADRATINHOS: Zoom = Zoom(zoom = 17)
