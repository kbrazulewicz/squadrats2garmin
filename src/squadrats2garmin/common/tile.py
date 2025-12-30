"""Classes and methods to handle map tiles
"""
import math
from typing import NamedTuple

from pygeoif.geometry import Point


class Tile(NamedTuple):
    """
    Representation of a tile

    See https://wiki.openstreetmap.org/wiki/Zoom_levels.
    """

    x: int
    """tile's x coordinate"""
    y: int
    """tile's y coordinate"""

    def __repr__(self) -> str:
        """Overrides the default implementation
        """
        return f'Tile(x={self.x}, y={self.y})'


class Zoom:
    """Representation of zoom on the OSM map

    see https://wiki.openstreetmap.org/wiki/Zoom_levels
    """

    _zoom: int
    _n: int

    def __init__(self, zoom: int) -> None:
        self._zoom = zoom
        self._n = 2 ** zoom

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

    @property
    def zoom(self):
        return self._zoom

    def lat(self, y: int) -> float:
        """Return the latitude of the north edge of the tile with y coordinate
        """
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / self._n))))

    def lon(self, x: int) -> float:
        """Return the longitude of the west edge of the tile with x coordinate
        """
        return x / self._n * 360.0 - 180.0

    def to_geo(self, tile: Tile) -> Point:
        """Return the coordinates of the NW corner of the tile
        """
        return Point(
            x=self.lon(tile.x),
            y=self.lat(tile.y)
        )

    def to_tile(self, point: Point) -> Tile:
        """Return tile coordinates (x, y) for given latitude and longitude
        """
        tile_x = int((point.x + 180.0) / 360.0 * self._n)
        tile_y = int((1.0 - math.asinh(math.tan(math.radians(point.y))) / math.pi) / 2.0 * self._n)
        return Tile(tile_x, tile_y)


# number of tiles: 4^14 = 268 435 456
# number of nodes: (2^14 + 1)^2 = 268 468 225
ZOOM_SQUADRATS: Zoom = Zoom(zoom=14)

# number of tiles: 4^17 = 17 179 869 184
# number of nodes: (2^17 + 1)^2 = 17 180 131 329
ZOOM_SQUADRATINHOS: Zoom = Zoom(zoom=17)
