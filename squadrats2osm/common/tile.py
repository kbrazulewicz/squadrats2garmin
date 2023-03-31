import math
from collections import defaultdict

from common import osm
from common.osm import Node, NodeRef, Way

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
        n = 2 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return Tile(xtile, ytile, zoom)
    
    @staticmethod
    def to_osm_node(x: int, y: int, zoom: int) -> Node:
        n = 2 ** zoom
        id = osm.NODE_BASE_ID + y * (n + 1) + x
        lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
        lon = x / n * 360.0 - 180.0
        return Node(id, lat, lon);

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


def generate_grid(tiles: list[Tile]) -> list[Way]:
    return generate_grid_1(tiles)


def generate_grid_1(tiles: list[Tile]) -> list[Way]:
    """Generate simple way consisting of 4 nodes for every tile"""

    tags = [('contour', 'elevation')]

    # dictionary, key: (x,y) tuple, value : Tile
    nodesByXY = {}
    ways = []
    for tile in tiles:
        k = (tile.x, tile.y)
        node1 = nodesByXY[k] if k in nodesByXY else nodesByXY.setdefault(k, Tile.to_osm_node(k[0], k[1], tile.zoom))
        k = (tile.x + 1, tile.y)
        node2 = nodesByXY[k] if k in nodesByXY else nodesByXY.setdefault(k, Tile.to_osm_node(k[0], k[1], tile.zoom))
        k = (tile.x + 1, tile.y + 1)
        node3 = nodesByXY[k] if k in nodesByXY else nodesByXY.setdefault(k, Tile.to_osm_node(k[0], k[1], tile.zoom))
        k = (tile.x, tile.y + 1)
        node4 = nodesByXY[k] if k in nodesByXY else nodesByXY.setdefault(k, Tile.to_osm_node(k[0], k[1], tile.zoom))

        id = node1.id - osm.NODE_BASE_ID + osm.WAY_BASE_ID
        ways.append(Way(id, nodes = [node1, node2, node3, node4], tags = tags))

    return ways



def generate_grid_2(tiles: list[Tile]) -> list[Way]:
    # sort tiles by y, x
    tilesByY = defaultdict(list)
    for tile in tiles:
        tilesByY[tile.y].append(tile)

    for x in tilesByY.values():
        x.sort(key=lambda tile: tile.x)
        print(x)

    # generate horizontal lines
    # merge horizontal lines

    # sort tiles by x, y
    # generate vertical lines
    # merge vertical lines

    return []