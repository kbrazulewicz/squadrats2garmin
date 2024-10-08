from typing import NamedTuple

class BoundingBox(NamedTuple):
    """Bounding box for a polygon
    """
    n: float
    e: float
    s: float
    w: float
    
class Coordinates(NamedTuple):
    """Representation of the geographical coordinates
    
    Attributes
    ----------
    lat : float
        latitute
    lon : float
        longitude
    """
    lat: float
    lon: float