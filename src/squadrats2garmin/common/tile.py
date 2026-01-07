"""Classes and methods to handle map tiles
"""
import math
from typing import NamedTuple

import shapely

import squadrats2garmin.common.osm


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

    def to_geo(self, tile: Tile) -> shapely.Point:
        """Return the coordinates of the NW corner of the tile
        """
        return shapely.Point(
            self.lon(tile.x),
            self.lat(tile.y)
        )

    def x(self, lon: float) -> int:
        return int((lon + 180.0) / 360.0 * self._n)

    def y(self, lat: float) -> int:
        return int((1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * self._n)

    def to_tile(self, point: shapely.Point | squadrats2garmin.common.osm.Point) -> Tile:
        """Return tile coordinates (x, y) for given latitude and longitude
        """
        if isinstance(point, tuple):
            return Tile(self.x(point[0]), self.y(point[1]))
        elif isinstance(point, shapely.Point):
            return Tile(self.x(point.x), self.y(point.y))
        else:
            raise TypeError(f"type {type(point)} not supported")


# number of tiles: 4^14 = 268 435 456
# number of nodes: (2^14 + 1)^2 = 268 468 225
ZOOM_SQUADRATS: Zoom = Zoom(zoom=14)

# number of tiles: 4^17 = 17 179 869 184
# number of nodes: (2^17 + 1)^2 = 17 180 131 329
ZOOM_SQUADRATINHOS: Zoom = Zoom(zoom=17)
