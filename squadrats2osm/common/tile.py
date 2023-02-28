import math

ZOOM_SQUADRATS = 14
ZOOM_SQUADRATINHOS = 17

class Tile:
    """Class representing a tile

    Attributes
        x : int
            x-coordinate
        y : int
            y-coordinate
        zoom : int
            zoom level
    """

    def __init__(self, x: int, y: int, zoom: int) -> None:
        self.x = x
        self.y = y
        self.zoom = zoom

    def __repr__(self) -> str:
        """Overrides the default implementation
        """
        return 'x {}; y {}; zoom {}'.format(self.x, self.y, self.zoom)

    def __eq__(self, __o: object) -> bool:
        """Overrides the default implementation
        """
        if isinstance(__o, Tile):
            return (self.x == __o.x and 
                self.y == __o.y and
                self.zoom == __o.zoom)
        return False

    @staticmethod
    def tile_at(coordinates_deg: tuple[int], zoom: int):
        """ Lon./lat. to tile numbers """
        lat_deg, lon_deg = coordinates_deg
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return Tile(xtile, ytile, zoom)