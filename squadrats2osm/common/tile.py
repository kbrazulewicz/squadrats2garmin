import math

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

    @staticmethod
    def tile_at(coordinates_deg, zoom):
        """ Lon./lat. to tile numbers """
        lat_deg, lon_deg = coordinates_deg
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return Tile(xtile, ytile, zoom)