import argparse
import itertools
import logging
import sys
import tempfile
from pathlib import Path
from typing import Protocol

import fastkml.geometry
import geojson
from fastkml import KML
from fastkml import Placemark
from fastkml.utils import find
from geojson import FeatureCollection

from squadrats2garmin.common.mkgmap import VisitedSquadratsConfig
from squadrats2garmin.common.osm import Tag, MultiPolygon, OSMProducer, AbstractOSMProducer, node_to_xml, \
    way_to_xml
from squadrats2garmin.common.squadrats import SquadratsClient
from squadrats2garmin.common.timer import timeit

logger = logging.getLogger(__name__)


class GeoJSONProvider(Protocol):
    def load(self) -> FeatureCollection:
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
                self.__kml_placemark_to_osm(placemark=placemark, tags=[('name', placemark_name)])

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

    def __parse_kml_multipolygon(self, polygons: list[fastkml.geometry.Polygon], tags: list[Tag] = None) -> None:
        """Parse fastkml.geometry.Polygon"""
        outer: list[int] = []
        inner: list[int] = []

        for poly in polygons:
            outer.append(self.__parse_kml_linear_ring(ring=poly.outer_boundary.kml_geometry))
            inner.extend(
                [self.__parse_kml_linear_ring(ring=boundary.kml_geometry) for boundary in poly.inner_boundaries])

        self._document.append(MultiPolygon.element_to_xml(
            element_id=self._next_id(), outer_rings=outer, inner_rings=inner, tags=tags))

    def __kml_placemark_to_osm(self, placemark: Placemark, tags: list[Tag]):
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
        squadrats: geojson.feature.FeatureCollection = self.__provider.load()
        for feature in squadrats.features:
            if isinstance(feature, geojson.feature.Feature):
                feature_name = feature.properties['name']
                if feature_name in self.__GEOJSON_FEATURES:
                    with timeit(msg=f"Processing {feature_name}"):
                        self.__feature_to_osm(feature=feature, tags=[('name', feature_name)])

        self._write_document(file=file)

    def __parse_linear_ring(self, ring: list[tuple[float, float]]) -> int:
        """Parse geojson's LineString"""

        # first and last node are the same and this needs to be the same object in OSM file
        node_ids = [self._next_id() for _ in itertools.islice(ring, 0, len(ring) - 1)]

        for node_id, point in zip(node_ids, ring):
            self._document.append(node_to_xml(element_id=node_id, geom=point))

        node_ids.append(node_ids[0])

        way_id = self._next_id()
        self._document.append(way_to_xml(element_id=way_id, refs=node_ids))
        return way_id

    def __parse_multipolygon(self, polygons: list[list[list[tuple[float, float]]]], tags: list[Tag] = None):
        outer: list[int] = []
        inner: list[int] = []

        for poly in polygons:
            outer.append(self.__parse_linear_ring(ring=poly[0]))
            inner.extend([
                self.__parse_linear_ring(ring=inner_ring)
                for inner_ring in itertools.islice(poly, 1, len(poly))
            ])

        self._document.append(MultiPolygon.element_to_xml(
            element_id=self._next_id(), outer_rings=outer, inner_rings=inner, tags=tags))

    def __feature_to_osm(self, feature: geojson.feature.Feature, tags: list[Tag]):
        """Write geojson Feature to OSM XML"""
        match feature.geometry.type:
            case 'MultiPolygon':
                self.__parse_multipolygon(polygons=feature.geometry.coordinates, tags=tags)
                pass
            case 'Polygon':
                self.__parse_multipolygon(polygons=[feature.geometry.coordinates], tags=tags)


class SquadratsTrophiesProvider(GeoJSONProvider):
    def __init__(self, user_id: str) -> None:
        self.__user_id: str = user_id
        self.__client = SquadratsClient()

    def load(self) -> FeatureCollection:
        """GeoJSONProvider protocol"""
        logger.info("Fetching Squadrats data")
        return self.__client.get_trophies(user_id=self.__user_id)


def parse_args():
    parser = argparse.ArgumentParser(description="Convert Squadrats' 'visited squadrats' to Garmin IMG map")

    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('-u', '--user-id', help="Squadrats' user id")
    action.add_argument('-k', '--kml', help="Squadrats' 'visited squadrats' KML")

    parser.add_argument('-v', '--verbose', action='store_true', help="verbose output")
    parser.add_argument('--keep', action='store_true', help="keep output files after processing")
    parser.add_argument('-o', '--output', required=True, help="output file")

    return parser.parse_args()


def generate_osm(output: Path, args):
    osm_producer: OSMProducer

    if args.user_id:
        osm_producer = GeoJSONOSMProducer(provider=SquadratsTrophiesProvider(user_id=args.user_id))
    elif args.kml_file:
        osm_producer = KMLOSMProducer(kml=KML.parse(Path(args.kml_file)))
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
