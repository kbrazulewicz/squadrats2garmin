"""Classes and methods for geo coordinates concepts"""
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
        latitude
    lon : float
        longitude
    """
    lat: float
    lon: float
