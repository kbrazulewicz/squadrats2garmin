"""Classes and methods to handle map tiles
"""
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
        return f'Tile(x={self.x}, y={self.y}, zoom={self.zoom})'

    def __key(self):
        # not including zoom because we do not expect existence of tiles
        # of different zooms at the same time
        return self.x, self.y

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, __o: object) -> bool:
        """Overrides the default implementation
        """
        if isinstance(__o, Tile):
            return self.__key() == __o.__key()
        return NotImplemented

    @staticmethod
    def tile_at(lat: float, lon: float, zoom: Zoom) -> Tile:
        """ Lon./lat. to tile numbers """
        tile_x, tile_y = zoom.tile(lat=lat, lon=lon)
        return Tile(x=tile_x, y=tile_y, zoom=zoom)
