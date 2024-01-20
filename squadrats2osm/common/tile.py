import math
from collections import defaultdict

from common import osm
from common.osm import Node
from common.zoom import Zoom

class Tile:
    """Representation of a tile

    see https://wiki.openstreetmap.org/wiki/Zoom_levels
    """

    x: int = None
    """tile's x coordinate"""
    y: int = None
    """tile's y coordinate"""
    zoom: Zoom = None
    """tile's zoom level"""
    lon: float = None
    """tile's NW corner longitude"""
    lat: float = None
    """tile's NW corner latitude"""

    def __init__(self, x: int, y: int, zoom: Zoom) -> None:
        self.x = x
        self.y = y
        self.zoom = zoom

        self.lon = zoom.lon(x)
        self.lat = zoom.lat(y)

    def __repr__(self) -> str:
        """Overrides the default implementation
        """
        return 'x {}; y {}; zoom {}'.format(self.x, self.y, self.zoom.zoom)

    def __key(self):
        # not including zoom because we do not expect existence of tiles of different zooms at the same time
        return (self.x, self.y)

    def __hash(self):
        return hash(self.__key())

    def __eq__(self, __o: object) -> bool:
        """Overrides the default implementation
        """
        if isinstance(__o, Tile):
            return (self.__key() == __o.__key())
        return NotImplemented

    @staticmethod
    def tile_at(lat: float, lon: float, zoom: Zoom):
        """ Lon./lat. to tile numbers """
        (xtile, ytile) = zoom.tile(lat = lat, lon = lon)
        return Tile(x = xtile, y = ytile, zoom = zoom)

    @staticmethod
    def to_osm_node(x: int, y: int, zoom: Zoom) -> Node:
        tile = Tile(x = x, y = y, zoom = zoom)
        id = osm.NODE_BASE_ID + y * (zoom.n + 1) + x
        return Node(id = id, lon = tile.lon, lat = tile.lat);

    def to_osm_nodes(self) -> list[Node]:
        # zoom levels: 0 .. 20
        # number of tiles: 4 ^ zoom level
        # number of tiles in a row: 2 ^^ zoom level
        # number of nodes in a row: 2 ^^ zoom level + 1 -> 
        # number of nodes on the map: (2 ^^ zoom level + 1) ^^ 2 = 4 ^^ zoom_level + 2 * 2 ^^ zoom_level + 1
        # 0: 4
        # 1: 9
        # 2: 25
        # 3: (2^3 + 1)^2 = 81
        # 4: (2^4 + 1)^2 = 17^2 = 289

        # (x, y)
        # (x + 1, y)
        # (x + 1, y + 1)
        # (x, y + 1)

        tile_seq_number = self.__to_seq_number()
        nodes = []