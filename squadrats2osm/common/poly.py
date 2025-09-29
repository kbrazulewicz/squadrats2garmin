from common.geo import BoundingBox
from common.geo import Coordinates


class PolyFileFormatException(Exception):
    """Raised when a POLY file has an incorrect format
    """
    pass

class PolyFileIncorrectFiletypeException(PolyFileFormatException):
    """Raised when a POLY file has an incorrect filetype
    """
    def __init__(self, filetype) -> None:
        self.filetype = filetype
        super().__init__('Expecting polygon filetype, got "{}" instead'.format(filetype))

class Poly:
    """Polygon definition

    POLY file contains lines with longitude and latitude of points creating polygon.
    Points are ordered clockwise
    https://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format

    Attributes
    ----------
    coords : list[list[Coordinates]]
        list of polygons
    """

    coords: list[list[Coordinates]]

    def __init__(self, filename):
        with open(filename) as f:
            self.coords = self.__read_poly_file(f)

        self.bounding_box = self.__calculate_bounding_box()

    def __read_poly_file(self, file):
        """Read the contents of the POLY file
        """
        filetype = file.readline().rstrip('\n')
        if filetype != 'polygon':
            raise PolyFileIncorrectFiletypeException(filetype)

        coords = []

        for line in file:
            line = line.strip()
            if line == 'END': break
            if line.startswith('!'): 
                """ ignore holes in the polygon """
                self.__read_polygon(file)
            else:
                coords.append(self.__read_polygon(file))

        return coords

    def __read_polygon(self, file):
        """Read a single polygon section
        """
        coords = []

        for line in file:
            line = line.strip()
            if line == 'END': break
            (poly_lon, poly_lat) = (map(float, line.split()))
            coords.append(Coordinates(lat = poly_lat, lon = poly_lon))

        return coords

    def __calculate_bounding_box(self) -> BoundingBox:
        """Calculate bounding box for a given set of coordinates
        """
        n = -90
        s = 90
        e = -180
        w = 180
        for poly in self.coords:
            for point in poly:
                n = max(n, point.lat)
                s = min(s, point.lat)
                e = max(e, point.lon)
                w = min(w, point.lon)

        return BoundingBox(n = n, e = e, s = s, w = w)