import math
from collections import defaultdict

from common import osm
from common.osm import Node, Way

# number of tiles: 4^14 = 268 435 456
# number of nodes: (2^14 + 1)^2 = 268 468 225
ZOOM_SQUADRATS = 14

# number of tiles: 4^17 = 17 179 869 184
# number of nodes: (2^17 + 1)^2 = 17 180 131 329
ZOOM_SQUADRATINHOS = 17

TAGS_WAY = [('contour', 'elevation')]

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
    def tile_at(lat: float, lon: float, zoom: int):
        """ Lon./lat. to tile numbers """
        lat_rad = math.radians(lat)
        n = 2 ** zoom
        xtile = int((lon + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return Tile(x = xtile, y = ytile, zoom = zoom)

    @staticmethod
    def to_osm_node(x: int, y: int, zoom: int) -> Node:
        n = 2 ** zoom
        id = osm.NODE_BASE_ID + y * (n + 1) + x
        lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
        lon = x / n * 360.0 - 180.0
        return Node(id = id, lat = lat, lon = lon);

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
    return generate_grid_2(tiles)


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
        ways.append(Way(id, nodes = [node1, node2, node3, node4, node1], tags = TAGS_WAY))

    return ways

def node_cache_get_or_compute(nodeCache: dict, x, y, zoom) -> Node:
    k = (x, y)
    if k in nodeCache:
        return nodeCache[k]
    else:
        node = Tile.to_osm_node(x, y, zoom)
        nodeCache[k] = node
        return node

def generate_grid_2(tiles: list[Tile]) -> list[Way]:

    if not tiles:
        return []

    # sort tiles by y, x
    tilesByY = defaultdict(list)
    for tile in tiles:
        tilesByY[tile.y].append(tile)

    for row in tilesByY.values():
        row.sort(key=lambda tile: tile.x)

    # sort tiles by x, y
    tilesByX = defaultdict(list)
    for tile in tiles:
        tilesByX[tile.x].append(tile)

    for col in tilesByX.values():
        col.sort(key=lambda tile: tile.y)


    ways: list[Way] = []

    # generate horizontal lines
    # at the moment we're ignoring holes and generate one long horizontal line
    rows = sorted(tilesByY.keys())
    prevRow = -1
    for row in rows:
        # first row or a gap - generate top edge
        if prevRow + 1 != row:
            ways.extend(__calculate_ways_for_rows([], tilesByY[row]))
        # generate bottom edge either with next row or with empty row if the next row doesn't exist
        ways.extend(__calculate_ways_for_rows(tilesByY[row], tilesByY[row + 1]))
        prevRow = row

    # merge horizontal lines - ignoring at the moment


    # generate vertical lines
    # at the moment we're ignoring holes and generate one long vertical line
    cols = sorted(tilesByX.keys())
    prevCol = -1
    for col in cols:
        # first column or a gap - generate left edge
        if prevCol + 1 != col:
            ways.extend(__calculate_ways_for_rows([], tilesByX[col]))
        # generate right edge either with next column or with empty column if the next column doesn't exist
        ways.extend(__calculate_ways_for_cols(tilesByX[col], tilesByX[col + 1]))
        prevCol = col

    # merge vertical lines - ignoring at the moment

    return ways


def __calculate_ways_for_rows(row1: list[Tile], row2: list[Tile]) -> list[Way]:

    if not row1 and not row2:
        return []

    zoom = None
    y = None
    minXCandidates: list[int] = [] 
    maxXCandidates: list[int] = [] 

    if row1:
        zoom = row1[0].zoom
        y = row1[0].y + 1
        minXCandidates.append(row1[0].x)
        maxXCandidates.append(row1[-1].x + 1)

    if row2:
        zoom = row2[0].zoom
        y = row2[0].y
        minXCandidates.append(row2[0].x)
        maxXCandidates.append(row2[-1].x + 1)

    node1 = Tile.to_osm_node(min(minXCandidates), y, zoom)
    node2 = Tile.to_osm_node(max(maxXCandidates), y, zoom)

    id = node1.id - osm.NODE_BASE_ID + osm.WAY_BASE_ID
    return [Way(id, nodes = [node1, node2], tags = TAGS_WAY)]


def __calculate_ways_for_cols(col1: list[Tile], col2: list[Tile]) -> list[Way]:

    if not col1 and not col2:
        return []

    zoom = None
    x = None
    minYCandidates: list[int] = [] 
    maxYCandidates: list[int] = [] 

    if col1:
        zoom = col1[0].zoom
        x = col1[0].x + 1
        minYCandidates.append(col1[0].y)
        maxYCandidates.append(col1[-1].y + 1)

    if col2:
        zoom = col2[0].zoom
        x = col2[0].x
        minYCandidates.append(col2[0].y)
        maxYCandidates.append(col2[-1].y + 1)

    node1 = Tile.to_osm_node(x, min(minYCandidates), zoom)
    node2 = Tile.to_osm_node(x, max(maxYCandidates), zoom)

    id = node1.id - osm.NODE_BASE_ID + osm.WAY_BASE_ID
    return [Way(id, nodes = [node1, node2], tags = TAGS_WAY)]