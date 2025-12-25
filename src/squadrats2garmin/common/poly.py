"""Classes and methods to read polygon files

Polygon definition
POLY file contains lines with longitude and latitude of points creating polygon.
Points are ordered clockwise
https://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format
"""
from pathlib import Path
from typing import cast
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


def parse_poly_file(path: Path) -> MultiPolygon:
    """Read the contents of the POLY file
    """
    with path.open(encoding='UTF-8') as f:
        filetype = f.readline().rstrip('\n')
        if filetype != 'polygon':
            raise PolyFileIncorrectFiletypeException(filetype)

        polygons: list[Polygon] = []
        shell: LineString = None
        holes: list[LineString] = []

        for line in f:
            line = line.strip()
            if line == 'END':
                break
            if line.startswith('!'):
                # ignore holes in the polygon
                holes.append(LinearRing([p for p in _read_points(f)]))
            else:
                if shell:
                    polygons.append(Polygon(shell=shell.coords, holes=tuple(h.coords for h in holes)))
                    holes = []
                shell = LinearRing([p for p in _read_points(f)])

        if shell:
            polygons.append(Polygon(shell=shell.coords, holes=tuple(h.coords for h in holes)))

        return MultiPolygon(polygons=[p.coords for p in polygons])


def _read_points(file):
    for line in file:
        line = line.strip()
        if line == 'END':
            break
        yield cast("Point2D", tuple(float(c) for c in line.split()))
