import argparse
import itertools
import json
import logging
import sys
import tempfile
from collections import defaultdict
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Protocol

import fastkml.geometry
import shapely
from fastkml import KML
from fastkml import Placemark
from fastkml.utils import find
from shapely import LinearRing, Polygon
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry

from squadrats2garmin.common.mkgmap import VisitedSquadratsConfig
from squadrats2garmin.common.osm import Tags, OSMProducer, AbstractOSMProducer, node_to_xml, \
    way_to_xml, multipolygon_to_xml
from squadrats2garmin.common.squadrats import SquadratsClient
from squadrats2garmin.common.tile import Zoom, ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS
from squadrats2garmin.common.timer import timeit

logger = logging.getLogger(__name__)

# Map from GeoJSON feature name to zoom level for scanline center-point generation
_FEATURE_ZOOM: dict[str, Zoom] = {
    'squadrats': ZOOM_SQUADRATS,
    'squadratinhos': ZOOM_SQUADRATINHOS,
}


def scanline_tiles(geojson_coordinates: list, zoom: Zoom) -> Iterator[tuple[int, int]]:
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
                yield (x, y)


class GeoJSONProvider(Protocol):
    def load(self) -> dict:
        ...


class KMLOSMProducer(AbstractOSMProducer, OSMProducer):
    """Convert Squadrats' KML to OSM"""

    __KML_PLACEMARKS: list[str] = ['squadrats', 'squadratinhos', 'ubersquadrat', 'ubersquadratinho']

    def __init__(self, kml: KML):
        super().__init__()
        self.__kml = kml

    def to_file(self, file: Path) -> None:
        """OSMProducer protocol"""
        logger.info("Processing KML data")
        for placemark_name in self.__KML_PLACEMARKS:
            with timeit(msg=f"Processing {placemark_name}"):
                placemark: Placemark = find(self.__kml, name=placemark_name)
                self.__kml_placemark_to_osm(placemark=placemark, tags={'name': placemark_name})

        self._write_document(file=file)

    def __parse_kml_linear_ring(self, ring: fastkml.geometry.LinearRing) -> int:
        """Parse fastkml.geometry.LinearRing"""
        coords = ring.kml_coordinates.coords

        # first and last node are the same and this needs to be the same object in OSM file
        node_ids = [self._next_id() for _ in itertools.islice(coords, 0, len(coords) - 1)]

        for node_id, point in zip(node_ids, coords):
            self._document.append(node_to_xml(element_id=node_id, geom=point))

        node_ids.append(node_ids[0])

        way_id = self._next_id()
        self._document.append(way_to_xml(element_id=way_id, refs=node_ids))
        return way_id

    def __parse_kml_multipolygon(self, polygons: list[fastkml.geometry.Polygon], tags: Tags | None = None) -> None:
        """Parse fastkml.geometry.Polygon"""
        outer: list[int] = []
        inner: list[int] = []

        for poly in polygons:
            outer.append(self.__parse_kml_linear_ring(ring=poly.outer_boundary.kml_geometry))
            inner.extend(
                [self.__parse_kml_linear_ring(ring=boundary.kml_geometry) for boundary in poly.inner_boundaries])

        self._document.append(multipolygon_to_xml(
            element_id=self._next_id(), outer_rings=outer, inner_rings=inner, tags=tags))

    def __kml_placemark_to_osm(self, placemark: Placemark, tags: Tags):
        """Write fastkml.Placemark to OSM XML"""
        # use kml_geometry as it doesn't require recalculation
        if isinstance(placemark.kml_geometry, fastkml.geometry.MultiGeometry):
            self.__parse_kml_multipolygon(polygons=placemark.kml_geometry.kml_geometries, tags=tags)
        elif isinstance(placemark.kml_geometry, fastkml.geometry.Polygon):
            self.__parse_kml_multipolygon(polygons=[placemark.kml_geometry], tags=tags)
        else:
            return


class GeoJSONOSMProducer(AbstractOSMProducer, OSMProducer):
    """Convert Squadrats' GeoJSON to OSM"""

    __GEOJSON_FEATURES: list[str] = ['squadrats', 'squadratinhos', 'ubersquadrat', 'ubersquadratinho']

    def __init__(self, provider: GeoJSONProvider):
        super().__init__()
        self.__provider = provider

    def to_file(self, file: Path) -> None:
        """OSMProducer protocol"""
        geo_json = self.__provider.load()
        for feature in geo_json['features']:
            feature_name = feature['properties']['name']
            if feature_name in self.__GEOJSON_FEATURES:
                with timeit(msg=f"Processing {feature_name}"):
                    self.__shape_to_osm(geom=shapely.orient_polygons(shape(feature)), tags={'name': feature_name})

            # Emit center-point nodes for visited squadrats/squadratinhos
            if feature_name in _FEATURE_ZOOM:
                zoom = _FEATURE_ZOOM[feature_name]
                with timeit(msg=f"Generating center points for {feature_name}"):
                    count = 0
                    for tile in scanline_tiles(feature['geometry']['coordinates'], zoom):
                        self._document.append(node_to_xml(
                            element_id=self._next_id(),
                            geom=zoom.to_center_point(tile),
                            tags={'grid_center': str(zoom.zoom)}
                        ))
                        count += 1
                    logger.info("Generated %d center points for %s", count, feature_name)

        self._write_document(file=file)

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
        outer: list[int] = []
        inner: list[int] = []

        for poly in polygons:
            outer.append(self.__parse_linear_ring(ring=poly.exterior, tags=tags))
            inner.extend([
                self.__parse_linear_ring(ring=inner_ring, tags=tags)
                for inner_ring in poly.interiors
            ])

        # self._document.append(multipolygon_to_xml(
        #     element_id=self._next_id(), outer_rings=outer, inner_rings=inner, tags=tags))

    def __shape_to_osm(self, geom: BaseGeometry, tags: Tags):
        """Write shape to OSM XML"""
        match geom.geom_type:
            case 'MultiPolygon':
                self.__parse_multipolygon(polygons=geom.geoms, tags=tags)
                pass
            case 'Polygon':
                self.__parse_multipolygon(polygons=[geom], tags=tags)


class SquadratsTrophiesProvider(GeoJSONProvider):
    def __init__(self, user_id: str) -> None:
        self.__user_id: str = user_id
        self.__client = SquadratsClient()

    def load(self):
        """GeoJSONProvider protocol"""
        logger.info("Fetching Squadrats data")
        return self.__client.get_trophies(user_id=self.__user_id)


class SquadratsGeoJsonProvider(GeoJSONProvider):
    def __init__(self, geojson_file: Path | str) -> None:
        self.__geojson_file: Path = Path(geojson_file)

    def load(self):
        """GeoJSONProvider protocol"""
        logger.info("Reading GeoJSON data from %s", self.__geojson_file)
        with self.__geojson_file.open("r", encoding="utf-8") as f:
            return json.load(f)


def parse_args():
    parser = argparse.ArgumentParser(description="Convert Squadrats' 'visited squadrats' to Garmin IMG map")

    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('-u', '--user-id', help="Squadrats' user id")
    action.add_argument('-k', '--kml', type=Path, help="Squadrats' 'visited squadrats' KML")
    action.add_argument('-g', '--geojson', type=Path, help="Squadrats' 'visited squadrats' GeoJSON")

    parser.add_argument('-v', '--verbose', action='store_true', help="verbose output")
    parser.add_argument('--keep', action='store_true', help="keep output files after processing")
    parser.add_argument('-o', '--output', required=True, help="output file")

    return parser.parse_args()


def generate_osm(output: Path, args):
    osm_producer: OSMProducer

    if args.user_id:
        osm_producer = GeoJSONOSMProducer(provider=SquadratsTrophiesProvider(user_id=args.user_id))
    elif args.geojson:
        osm_producer = GeoJSONOSMProducer(provider=SquadratsGeoJsonProvider(geojson_file=args.geojson))
    elif args.kml:
        osm_producer = KMLOSMProducer(kml=KML.parse(args.kml))
    else:
        raise ValueError

    osm_producer.to_file(output)


def visited_squadrats():
    args = parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    with tempfile.TemporaryDirectory(prefix="mkgmap-", delete=(not args.keep)) as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        osm_path = tmp_dir / 'squadrats-visited.osm'

        generate_osm(output=osm_path, args=args)

        config = VisitedSquadratsConfig(
            output=Path(args.output),
            config={
                'output_dir': tmp_dir
            },
            osm_path=osm_path
        )

        logger.info("Building Garmin IMG file %s", config.output)
        config.build_garmin_img()

        if args.keep:
            logger.info(f"Keeping output files in {tmp_dir_name}")


def main():
    with timeit(msg=f"{sys.argv}"):
        visited_squadrats()


if __name__ == "__main__":
    main()
