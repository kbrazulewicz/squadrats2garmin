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
        return f"Zoom(zoom={self.zoom})"

    def __key(self):
        return self.zoom

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, __o: object) -> bool:
        """Override the default implementation
        """
        if isinstance(__o, Zoom):
            return self.__key() == __o.__key()
        return NotImplemented

    def lat(self, y: int) -> float:
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / self.n))))
    
    def lon(self, x: int) -> float:
        return x / self.n * 360.0 - 180.0    
    
    def tile(self, lat: float, lon: float) -> tuple[int, int]:
        xtile = int((lon + 180.0) / 360.0 * self.n)
        ytile = int((1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * self.n)
        return (xtile, ytile)
    
# number of tiles: 4^14 = 268 435 456
# number of nodes: (2^14 + 1)^2 = 268 468 225
ZOOM_SQUADRATS: Zoom = Zoom(zoom = 14)

# number of tiles: 4^17 = 17 179 869 184
# number of nodes: (2^17 + 1)^2 = 17 180 131 329
ZOOM_SQUADRATINHOS: Zoom = Zoom(zoom = 17)

