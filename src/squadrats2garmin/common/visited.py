import io
import itertools
import json
import logging
from collections import defaultdict
from collections.abc import Iterator, Sequence
from functools import singledispatchmethod
from pathlib import Path
from typing import IO, Protocol

import shapely
from shapely import LinearRing, Polygon
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry

from squadrats2garmin.common.osm import AbstractOSMProducer, OSMProducer, Tags, node_to_xml, way_to_xml
from squadrats2garmin.common.squadrats import SquadratsClient
from squadrats2garmin.common.tile import Zoom, ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS
from squadrats2garmin.common.timer import timeit

logger = logging.getLogger(__name__)

class GeoJSONProvider(Protocol):
    def load(self) -> dict:
        ...


class SquadratsTrophiesProvider(GeoJSONProvider):
    def __init__(self, user_id: str) -> None:
        self.__user_id: str = user_id
        self.__client = SquadratsClient()

    def load(self):
        """GeoJSONProvider protocol"""
        logger.info("Fetching Squadrats data")
        return self.__client.get_trophies(user_id=self.__user_id).json()


class SquadratsGeoJsonProvider(GeoJSONProvider):
    def __init__(self, source: str | Path | IO[str] | IO[bytes] | io.TextIOBase) -> None:
        self.__source = source

    def load(self):
        """GeoJSONProvider protocol"""
        return self._load_from(self.__source)

    @singledispatchmethod
    def _load_from(self, source) -> dict:
        raise TypeError(f"Unsupported GeoJSON source type: {type(source)}")

    @_load_from.register
    def _(self, source: str | Path) -> dict:
        path = Path(source)
        logger.info("Reading GeoJSON data from %s", path)
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @_load_from.register
    def _(self, source: io.TextIOBase) -> dict:
        logger.info("Reading GeoJSON data from TextIOWrapper stream")
        return json.load(source)

    @_load_from.register
    def _(self, source: IO) -> dict:
        logger.info("Reading GeoJSON data from stream")
        return json.load(source)


class GeoJSONOSMProducer(AbstractOSMProducer, OSMProducer):
    """Convert Squadrats' GeoJSON to OSM"""

    # Map from GeoJSON feature name to zoom level for scanline center-point generation
    __FEATURE_ZOOM: dict[str, Zoom] = {
        'squadrats': ZOOM_SQUADRATS,
        'squadratinhos': ZOOM_SQUADRATINHOS,
    }
    __GEOJSON_FEATURES: list[str] = ['squadrats', 'squadratinhos', 'ubersquadrat', 'ubersquadratinho']

    def __init__(self, provider: GeoJSONProvider):
        super().__init__()
        self.__provider = provider

    def to_file(self, file: Path) -> None:
        self.__parse_input()
        self._to_file(file=file)

    def to_string(self) -> str:
        self.__parse_input()
        return self._to_string()

    def __parse_input(self):
        """OSMProducer protocol"""
        geo_json = self.__provider.load()
        for feature in geo_json['features']:
            feature_name = feature['properties']['name']
            if feature_name in self.__GEOJSON_FEATURES:
                with timeit(msg=f"Processing {feature_name}"):
                    self.__shape_to_osm(geom=shapely.orient_polygons(shape(feature)), tags={'name': feature_name})

            # Emit center-point nodes for visited squadrats/squadratinhos
            if feature_name in self.__FEATURE_ZOOM:
                zoom = self.__FEATURE_ZOOM[feature_name]
                with timeit(msg=f"Generating center points for {feature_name}"):
                    count = 0
                    for tile in self.__scanline_tiles(feature['geometry']['coordinates'], zoom):
                        self._document.append(node_to_xml(
                            element_id=self._next_id(),
                            geom=zoom.to_center_point(tile),
                            tags={'grid_center': str(zoom.zoom)}
                        ))
                        count += 1
                    logger.info("Generated %d center points for %s", count, feature_name)

    def __parse_linear_ring(self, ring: LinearRing, tags: Tags | None = None) -> int:
        """Parse LinearRing"""

        # first and last node are the same and this needs to be the same object in OSM file
        node_ids = [self._next_id() for _ in itertools.islice(ring.coords, 0, len(ring.coords) - 1)]

        for node_id, point in zip(node_ids, ring.coords):
            self._document.append(node_to_xml(element_id=node_id, geom=point))

        node_ids.append(node_ids[0])

        way_id = self._next_id()
        self._document.append(way_to_xml(element_id=way_id, refs=node_ids, tags=tags))
        return way_id

    def __parse_multipolygon(self, polygons: Sequence[Polygon], tags: Tags | None = None):
        for poly in polygons:
            self.__parse_linear_ring(ring=poly.exterior, tags=tags)
            for inner_ring in poly.interiors:
                self.__parse_linear_ring(ring=inner_ring, tags=tags)

    def __shape_to_osm(self, geom: BaseGeometry, tags: Tags):
        """Write shape to OSM XML"""
        match geom.geom_type:
            case 'MultiPolygon':
                self.__parse_multipolygon(polygons=geom.geoms, tags=tags)
                pass
            case 'Polygon':
                self.__parse_multipolygon(polygons=[geom], tags=tags)

    @staticmethod
    def __scanline_tiles(geojson_coordinates: list, zoom: Zoom) -> Iterator[tuple[int, int]]:
        """Enumerate every individual tile (x, y) covered by a MultiPolygon outline.

        The GeoJSON outline consists of strictly orthogonal segments whose vertices
        lie exactly on tile boundaries.  We convert each vertex to integer tile
        coordinates (using round() to avoid float truncation), collect all vertical
        edges, and apply the even-odd scanline rule to recover the filled tiles.

        Yields (x, y) for every visited tile.
        """
        vertical_edges_by_y: dict[int, list[int]] = defaultdict(list)

        def _process_ring(ring: list[list[float]]) -> None:
            tile_coords = [(zoom.x_round(lon), zoom.y_round(lat)) for lon, lat in ring]
            for (x1, y1), (x2, y2) in zip(tile_coords, tile_coords[1:]):
                if x1 == x2:  # vertical segment
                    y_lo, y_hi = min(y1, y2), max(y1, y2)
                    for y in range(y_lo, y_hi):
                        vertical_edges_by_y[y].append(x1)

        # MultiPolygon: list of polygons, each polygon is a list of rings
        for polygon in geojson_coordinates:
            for ring in polygon:
                _process_ring(ring)

        for y in sorted(vertical_edges_by_y):
            xs = sorted(vertical_edges_by_y[y])
            for i in range(0, len(xs), 2):
                for x in range(xs[i], xs[i + 1]):
                    yield x, y