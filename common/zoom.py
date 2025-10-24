"""Conversion between geo and tile coordinates for different zoom levels
"""
import math

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

    def lat(self, y: int) -> float:
        """Return the latitude of the north edge of the tile with y coordinate
        """
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / self.n))))

    def lon(self, x: int) -> float:
        """Return the longitude of the west edge of the tile with x coordinate
        """
        return x / self.n * 360.0 - 180.0

    def tile(self, lat: float, lon: float) -> tuple[int, int]:
        """Return tile coordinates (x, y) for given latitude and longitude
        """
        tile_x = int((lon + 180.0) / 360.0 * self.n)
        tile_y = int((1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * self.n)
        return tile_x, tile_y

# number of tiles: 4^14 = 268 435 456
# number of nodes: (2^14 + 1)^2 = 268 468 225
ZOOM_SQUADRATS: Zoom = Zoom(zoom = 14)

# number of tiles: 4^17 = 17 179 869 184
# number of nodes: (2^17 + 1)^2 = 17 180 131 329
ZOOM_SQUADRATINHOS: Zoom = Zoom(zoom = 17)
