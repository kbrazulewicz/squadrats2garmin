import math

from common.osm import Node

# number of tiles: 4^14 = 268 435 456
# number of nodes: (2^14 + 1)^2 = 268 468 225
ZOOM_SQUADRATS = 14

# number of tiles: 4^17 = 17 179 869 184
# number of nodes: (2^17 + 1)^2 = 17 180 131 329
ZOOM_SQUADRATINHOS = 17


class Tile:
    """Representation of a tile

    see https://wiki.openstreetmap.org/wiki/Zoom_levels
    """

    x: int = None
    """tile's x coordinate"""
    y: int = None
    """tile's y coordinate"""
    zoom: int = None
    """tile's zoom level"""

    def __init__(self, x: int, y: int, zoom: int) -> None:
        self.x = x
        self.y = y
        self.zoom = zoom

    def __repr__(self) -> str:
        """Overrides the default implementation
        """
        return 'x {}; y {}; zoom {}'.format(self.x, self.y, self.zoom)

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
    def tile_at(coordinates_deg: tuple[int], zoom: int):
        """ Lon./lat. to tile numbers """
        lat_deg, lon_deg = coordinates_deg
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return Tile(xtile, ytile, zoom)
    
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
    
def to_osm_node(x: int, y: int, zoom: int) -> Node:
    id = y * (n + 1) + x
    n = 2.0 ** zoom
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    lon = x / n * 360.0 - 180.0
    return Node(id, lat, lon);