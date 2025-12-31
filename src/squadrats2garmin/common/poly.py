"""Classes and methods to read polygon files

Polygon definition
POLY file contains lines with longitude and latitude of points creating polygon.
Points are ordered clockwise
https://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format
"""
from pathlib import Path
from typing import cast, Protocol

import shapely


class PolyFileFormatException(Exception):
    """Raised when a POLY file has an incorrect format
    """


class PolyFileIncorrectFiletypeException(PolyFileFormatException):
    """Raised when a POLY file has an incorrect filetype
    """

    def __init__(self, filetype) -> None:
        self.filetype = filetype
        super().__init__(f'Expecting polygon filetype, got "{filetype}" instead')


class PolyLoader(Protocol):
    def load(self) -> shapely.MultiPolygon:
        ...


class GeoJSONPolyLoader(PolyLoader):
    def __init__(self, path: Path):
        self._path = path

    def load(self) -> shapely.MultiPolygon:
        geometry = shapely.from_geojson(self._path.read_bytes())
        if geometry.geom_type == 'MultiPolygon':
            return cast('shapely.MultiPolygon', geometry)
        elif geometry.geom_type == 'Polygon':
            return shapely.MultiPolygon([cast('shapely.Polygon', geometry)])
        else:
            raise PolyFileFormatException(f"Geometry type {geometry.geom_type} is not supported")


def _read_points(file):
    for line in file:
        line = line.strip()
        if line == 'END':
            break
        yield tuple(float(c) for c in line.split())


class POLYPolyLoader(PolyLoader):
    def __init__(self, path: Path):
        self._path = path

    def load(self) -> shapely.MultiPolygon:
        with self._path.open(encoding='UTF-8') as f:
            filetype = f.readline().rstrip('\n')
            if filetype != 'polygon':
                raise PolyFileIncorrectFiletypeException(filetype)

            polygons: list[shapely.Polygon] = []
            shell: shapely.LineString = None
            holes: list[shapely.LineString] = []

            for line in f:
                line = line.strip()
                if line == 'END':
                    break
                if line.startswith('!'):
                    # ignore holes in the polygon
                    holes.append(shapely.LinearRing([p for p in _read_points(f)]))
                else:
                    if shell:
                        polygons.append(shapely.Polygon(shell=shell.coords, holes=tuple(h.coords for h in holes)))
                        holes = []
                    shell = shapely.LinearRing([p for p in _read_points(f)])

            if shell:
                polygons.append(shapely.Polygon(shell=shell.coords, holes=tuple(h.coords for h in holes)))

            return shapely.MultiPolygon(polygons)

class ExtensionAwarePolyLoader(PolyLoader):
    def __init__(self, path: Path):
        match path.suffix:
            case '.poly':
                self._delegate = POLYPolyLoader(path)
            case '.json' | '.geojson':
                self._delegate = GeoJSONPolyLoader(path)
            case _:
                raise ValueError(f"Don't know how to parse file with '{path.suffix}' extension")

    def load(self) -> shapely.MultiPolygon:
        return self._delegate.load()


def parse_poly_file(path: Path) -> shapely.MultiPolygon:
    return ExtensionAwarePolyLoader(path).load()