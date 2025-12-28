import argparse
import itertools
import logging
import pathlib
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator

# import fastkml.geometry
import geojson
# from fastkml import KML
# from fastkml import Placemark
# from fastkml.utils import find

from squadrats2garmin.common.mkgmap import VisitedSquadratsConfig
from squadrats2garmin.common.osm import Node, Tag, MultiPolygon, Way
from squadrats2garmin.common.squadrats import SquadratsClient
from squadrats2garmin.common.timer import timeit

logger = logging.getLogger(__name__)


class VisitedSquadrats:
    _document: ET.Element
    _id_generator: Iterator[int]

    def __init__(self):
        self._document = ET.Element("osm", {"version": '0.6'})
        self._id_generator = itertools.count(start=1)

    def parse_kml_linear_ring(self, ring: fastkml.geometry.LinearRing) -> int:
        """Parse fastkml.geometry.LinearRing"""
        coords = ring.kml_coordinates.coords

        # first and last node are the same and this needs to be the same object in OSM file
        node_ids = [next(self._id_generator) for _ in itertools.islice(coords, 0, len(coords) - 1)]

        for node_id, point in zip(node_ids, coords):
            self._document.append(Node(node_id=node_id, geom=point).to_xml())

        node_ids.append(node_ids[0])

        way_id = next(self._id_generator)
        self._document.append(Way.way_to_xml(element_id=way_id, refs=node_ids))
        return way_id

    def parse_kml_multipolygon(self, polygons: list[fastkml.geometry.Polygon], tags: list[Tag]=None) -> None:
        """Parse fastkml.geometry.Polygon"""
        outer: list[int] = []
        inner: list[int] = []

        for poly in polygons:
            outer.append(self.parse_kml_linear_ring(ring=poly.outer_boundary.kml_geometry))
            inner.extend([self.parse_kml_linear_ring(ring=boundary.kml_geometry) for boundary in poly.inner_boundaries])

        self._document.append(MultiPolygon.element_to_xml(
            element_id=next(self._id_generator), outer_rings=outer, inner_rings=inner, tags=tags))

    def kml_placemark_to_osm(self, placemark: Placemark, tags: list[Tag]):
        """Write fastkml.Placemark to OSM XML"""
        # use kml_geometry as it doesn't require recalculation
        if isinstance(placemark.kml_geometry, fastkml.geometry.MultiGeometry):
            self.parse_kml_multipolygon(polygons=placemark.kml_geometry.kml_geometries, tags=tags)
        elif isinstance(placemark.kml_geometry, fastkml.geometry.Polygon):
            self.parse_kml_multipolygon(polygons=[placemark.kml_geometry], tags=tags)
        else:
            return

    def parse_geojson_linear_ring(self, ring: list[tuple[float, float]]) -> int:
        """Parse geojson's LineString"""

        # first and last node are the same and this needs to be the same object in OSM file
        node_ids = [next(self._id_generator) for _ in itertools.islice(ring, 0, len(ring) - 1)]

        for node_id, point in zip(node_ids, ring):
            self._document.append(Node(node_id=node_id, geom=point).to_xml())

        node_ids.append(node_ids[0])

        way_id = next(self._id_generator)
        self._document.append(Way.way_to_xml(element_id=way_id, refs=node_ids))
        return way_id

    def parse_geojson_multipolygon(self, polygons:list[list[list[tuple[float, float]]]], tags: list[Tag]=None):
        outer: list[int] = []
        inner: list[int] = []

        for poly in polygons:
            outer.append(self.parse_geojson_linear_ring(ring=poly[0]))
            inner.extend([
                self.parse_geojson_linear_ring(ring=inner_ring)
                for inner_ring in itertools.islice(poly, 1, len(poly))
            ])

        self._document.append(MultiPolygon.element_to_xml(
            element_id=next(self._id_generator), outer_rings=outer, inner_rings=inner, tags=tags))

    def geojson_feature_to_osm(self, feature: geojson.feature.Feature, tags: list[Tag]):
        """Write geojson Feature to OSM XML"""
        match feature.geometry.type:
            case 'MultiPolygon':
                self.parse_geojson_multipolygon(polygons=feature.geometry.coordinates, tags=tags)
                pass
            case 'Polygon':
                self.parse_geojson_multipolygon(polygons=[feature.geometry.coordinates], tags=tags)

    def write_document(self, path: Path):
        ET.indent(self._document)
        ET.ElementTree(self._document).write(path, encoding='utf-8', xml_declaration=True)


def kml_to_osm(path: Path, kml):
    """Convert Squadrats' KML to OSM"""
    visited_squadrats = VisitedSquadrats()

    for name in ['squadrats', 'squadratinhos', 'ubersquadrat', 'ubersquadratinho']:
        with timeit(msg=f"Processing {name}"):
            placemark: Placemark = find(kml, name=name)
            visited_squadrats.kml_placemark_to_osm(placemark=placemark, tags=[('name', name)])

    with timeit(msg=f"Writing {path}"):
        visited_squadrats.write_document(path=path)


def geojson_to_osm(path: Path, feature_collection: geojson.feature.FeatureCollection):
    """Convert Squadrats' geojson to OSM"""
    visited_squadrats = VisitedSquadrats()

    if isinstance(feature_collection, geojson.feature.FeatureCollection):
        for feature in feature_collection.features:
            if isinstance(feature, geojson.feature.Feature):
                feature_name = feature.properties['name']
                if feature_name in ['squadrats', 'squadratinhos', 'ubersquadrat', 'ubersquadratinho']:
                    with timeit(msg=f"Processing {feature_name}"):
                        visited_squadrats.geojson_feature_to_osm(feature=feature, tags=[('name', feature_name)])

    with timeit(msg=f"Writing {path}"):
        visited_squadrats.write_document(path=path)


def parse_kml(path: pathlib.Path) -> KML:
    return KML.parse(path)


def parse_args():
    parser = argparse.ArgumentParser(description="Convert Squadrat's 'visited squadrats' KML to Garmin IMG map")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="verbose output")
    parser.add_argument('-k', '--keep', action='store_true',
                        help="keep output files after processing")
    parser.add_argument('-u', '--user-id', required=False,
                        help="Squadrat's user id")
    parser.add_argument('--kml', required=False,
                        help="Squadrat's 'visited squadrats' KML")
    parser.add_argument('-o', '--output', required=True,
                        help="Output file")

    return parser.parse_args()

def visited_squadrats():
    args = parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    with tempfile.TemporaryDirectory(prefix="mkgmap-", delete=(not args.keep)) as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        osm_path = tmp_dir / 'squadrats-visited.osm'

        if args.user_id:
            logger.info("Fetching squadrats data")
            squadrats_client = SquadratsClient()
            trophies = squadrats_client.get_trophies(user_id=args.user_id)
            geojson_to_osm(path=osm_path, feature_collection=trophies)
        elif args.kml_file:
            k: KML = parse_kml(Path(args.kml_file))
            kml_to_osm(path=osm_path, kml=k)

        config = VisitedSquadratsConfig(config={
            'output': Path(args.output),
            'output_dir': tmp_dir
        }, osm_path=osm_path)

        logger.info("Building Garmin IMG file %s", config.output)
        config.build_garmin_img()

        if args.keep:
            logger.info(f"Keeping output files in {tmp_dir_name}")

def main():
    with timeit(msg=f"{sys.argv}"):
        visited_squadrats()

if __name__ == "__main__":
    main()