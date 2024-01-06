import math
from collections import defaultdict

from common import osm
from common import util
from common.osm import Node, Way

# number of tiles: 4^14 = 268 435 456
# number of nodes: (2^14 + 1)^2 = 268 468 225
ZOOM_SQUADRATS = 14

# number of tiles: 4^17 = 17 179 869 184
# number of nodes: (2^17 + 1)^2 = 17 180 131 329
ZOOM_SQUADRATINHOS = 17

TAGS_WAY = [('name', 'grid')]

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
    lon: float = None
    """tile's NW corner longitude"""
    lat: float = None
    """tile's NW corner latitude"""

    def __init__(self, x: int, y: int, zoom: int) -> None:
        self.x = x
        self.y = y
        self.zoom = zoom

        n = 2 ** zoom
        self.lon = x / n * 360.0 - 180.0
        self.lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))

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
    def tile_at(lat: float, lon: float, zoom: int):
        """ Lon./lat. to tile numbers """
        lat_rad = math.radians(lat)
        n = 2 ** zoom
        xtile = int((lon + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return Tile(x = xtile, y = ytile, zoom = zoom)

    @staticmethod
    def to_osm_node(x: int, y: int, zoom: int) -> Node:
        tile = Tile(x = x, y = y, zoom = zoom)
        n = 2 ** zoom
        id = osm.NODE_BASE_ID + y * (n + 1) + x
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


def generate_grid(tiles: list[Tile]) -> list[Way]:
    return generate_grid(tiles)


def generate_grid_simple(tiles: list[Tile]) -> list[Way]:
    """Generate simple way consisting of 4 nodes for every tile"""

    # dictionary, key: (x,y) tuple, value : Tile
    nodesByXY = {}
    ways = []
    for tile in tiles:
        node1 = node_cache_get_or_compute(nodesByXY, tile.x, tile.y, tile.zoom)
        node2 = node_cache_get_or_compute(nodesByXY, tile.x + 1, tile.y, tile.zoom)
        node3 = node_cache_get_or_compute(nodesByXY, tile.x + 1, tile.y + 1, tile.zoom)
        node4 = node_cache_get_or_compute(nodesByXY, tile.x, tile.y + 1, tile.zoom)

        id = node1.id - osm.NODE_BASE_ID + osm.WAY_BASE_ID
        ways.append(Way(id, nodes = [node1, node2, node3, node4, node1], tags = [*TAGS_WAY, ('zoom', tile.zoom)]))

    return ways

def node_cache_get_or_compute(nodeCache: dict, x, y, zoom) -> Node:
    k = (x, y)
    if k in nodeCache:
        return nodeCache[k]
    else:
        node = Tile.to_osm_node(x, y, zoom)
        nodeCache[k] = node
        return node

def generate_grid(tiles: list[Tile]) -> list[Way]:

    if not tiles: return []

    ways: list[Way] = []
    zoom: int = tiles[0].zoom

    # sort tiles by y, x
    tilesByY = defaultdict(list)
    for tile in tiles:
        tilesByY[tile.y].append(tile)

    # find the horizontal ranges
    rangesByY = {y: util.make_ranges_end_inclusive(util.find_ranges(sorted([tile.x for tile in row]))) for (y, row) in tilesByY.items()}

    # generate horizontal lines
    prevY = None
    for y in sorted(rangesByY.keys()):
        if prevY is None or prevY + 1 != y:
            # first row or a gap - generate top edge
            ways.extend(__create_horizontal_ways_for_ranges(y = y, ranges = rangesByY[y], zoom = zoom))
        
        if y + 1 in rangesByY:
            # generate bottom edge between current and next row
            ways.extend(__create_horizontal_ways_for_ranges(y = y + 1, ranges = util.merge_ranges(rangesByY[y] + rangesByY[y + 1]), zoom = zoom))
        else:
            # generate bottom edge when next row is empty    
            ways.extend(__create_horizontal_ways_for_ranges(y = y + 1, ranges = rangesByY[y], zoom = zoom))

        prevY = y

    # sort tiles by x, y
    tilesByX = defaultdict(list)
    for tile in tiles:
        tilesByX[tile.x].append(tile)

    # find the vertical ranges
    rangesByX = {x: util.make_ranges_end_inclusive(util.find_ranges(sorted([tile.y for tile in column]))) for (x, column) in tilesByX.items()}

    # generate vertical lines
    prevX = None
    for x in sorted(rangesByX.keys()):
        if prevX is None or prevX + 1 != x:
            # first column or a gap - generate left edge
            ways.extend(__create_vertical_ways_for_ranges(x = x, ranges = rangesByX[x], zoom = zoom))
        
        if x + 1 in rangesByX:
            # generate right edge between current and next column
            ways.extend(__create_vertical_ways_for_ranges(x = x + 1, ranges = util.merge_ranges(rangesByX[x] + rangesByX[x + 1]), zoom = zoom))
        else:
            # generate right edge when next column is empty    
            ways.extend(__create_vertical_ways_for_ranges(x = x + 1, ranges = rangesByX[x], zoom = zoom))

        prevX = x

    return ways

def __create_horizontal_ways_for_ranges(y: int, ranges: list[tuple[int, int]], zoom: int) -> list[Way]:
    if not ranges:
        return []
    
    ways: list[Way] = []

    for range in ranges:
        (node1, node2) = (Tile.to_osm_node(x, y, zoom) for x in range)
        id = (node1.id - osm.NODE_BASE_ID + osm.WAY_BASE_ID) * 2
        ways.append(Way(id = id, nodes = [node1, node2], tags = [*TAGS_WAY, ('zoom', zoom)]))

    return ways

def __create_vertical_ways_for_ranges(x: int, ranges: list[tuple[int, int]], zoom: int) -> list[Way]:
    if not ranges:
        return []
    
    ways: list[Way] = []

    for range in ranges:
        (node1, node2) = (Tile.to_osm_node(x, y, zoom) for y in range)
        id = (node1.id - osm.NODE_BASE_ID + osm.WAY_BASE_ID) * 2 + 1
        ways.append(Way(id = id, nodes = [node1, node2], tags = [*TAGS_WAY, ('zoom', zoom)]))

    return ways