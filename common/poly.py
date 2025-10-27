"""Classes and methods to read polygon files
"""
from pygeoif import LinearRing, MultiPolygon
from pygeoif.geometry import LineString, Polygon
from pygeoif.types import Point2D


class PolyFileFormatException(Exception):
    """Raised when a POLY file has an incorrect format
    """


class PolyFileIncorrectFiletypeException(PolyFileFormatException):
    """Raised when a POLY file has an incorrect filetype
    """

    def __init__(self, filetype) -> None:
        self.filetype = filetype
        super().__init__(f'Expecting polygon filetype, got "{filetype}" instead')


class Poly:
    """Polygon definition

    POLY file contains lines with longitude and latitude of points creating polygon.
    Points are ordered clockwise
    https://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format

    Attributes
    ----------
    coords : MultiPolygon
        list of polygons
    """

    coords: MultiPolygon

    def __init__(self, filename):
        with open(filename, encoding='UTF-8') as f:
            self.coords = self.__read_poly_file(f)

    @property
    def bounding_box(self):
        return self.coords.bounds

    def __read_poly_file(self, file) -> MultiPolygon:
        """Read the contents of the POLY file
        """
        filetype = file.readline().rstrip('\n')
        if filetype != 'polygon':
            raise PolyFileIncorrectFiletypeException(filetype)

        polygons: list[Polygon] = []
        shell: LineString = None
        holes: list[LineString] = []

        for line in file:
            line = line.strip()
            if line == 'END':
                break
            if line.startswith('!'):
                # ignore holes in the polygon
                holes.append(self.__read_linear_ring(file))
            else:
                if shell:
                    polygons.append(Polygon(shell=shell.coords, holes=tuple(h.coords for h in holes)))
                    shell = None
                    holes = []
                shell = self.__read_linear_ring(file)

        if shell:
            polygons.append(Polygon(shell=shell.coords, holes=tuple(h.coords for h in holes)))

        return MultiPolygon(polygons=[p.coords for p in polygons])

    def __read_linear_ring(self, file) -> LinearRing:
        """Read a single polygon section
        """
        geoms: list[Point2D] = []

        for line in file:
            line = line.strip()
            if line == 'END':
                break
            (poly_lon, poly_lat) = (map(float, line.split()))
            geoms.append((poly_lon, poly_lat))

        return LinearRing(geoms)