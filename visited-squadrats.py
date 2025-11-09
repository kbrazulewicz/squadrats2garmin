import argparse
import itertools
import logging
import pathlib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator

import fastkml.geometry
from fastkml import KML
from fastkml import Placemark
from fastkml.utils import find

from common.config import VisitedSquadratsConfig, IMG_FAMILY_ID_VISITED_SQUADRATS, OUTPUT_DIR
from common.mkgmap import run_mkgmap, write_mkgmap_config_headers
from common.osm import Node, Tag, MultiPolygon, Way
from common.timer import timeit

logger = logging.getLogger(__name__)


class VisitedSquadrats:
    _document: ET.Element
    _id_generator: Iterator[int]

    def __init__(self):
        self._document = ET.Element("osm", {"version": '0.6'})
        self._id_generator = itertools.count(start=1)

    def parse_linear_ring(self, ring: fastkml.geometry.LinearRing) -> int:
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

    def parse_multipolygon(self, polygons: Iterator[fastkml.geometry.Polygon], tags: list[Tag]=None) -> None:
        """Parse fastkml.geometry.Polygon"""
        outer: list[int] = []
        inner: list[int] = []

        for poly in polygons:
            outer.append(self.parse_linear_ring(ring=poly.outer_boundary.kml_geometry))
            inner.extend([self.parse_linear_ring(ring=boundary.kml_geometry) for boundary in poly.inner_boundaries])

        self._document.append(MultiPolygon.element_to_xml(
            element_id=next(self._id_generator), outer_rings=outer, inner_rings=inner, tags=tags))

    def placemark_to_osm(self, placemark: Placemark, tags: list[Tag]):
        """Write fastkml.Placemark to OSM XML"""
        # use kml_geometry as it doesn't require recalculation
        if isinstance(placemark.kml_geometry, fastkml.geometry.MultiGeometry):
            self.parse_multipolygon(polygons=placemark.kml_geometry.kml_geometries, tags=tags)
            pass
        elif isinstance(placemark.kml_geometry, fastkml.geometry.Polygon):
            self.parse_multipolygon(polygons=[placemark.kml_geometry], tags=tags)
            pass
        else:
            return

    def write_document(self, path: Path):
        ET.indent(self._document)
        ET.ElementTree(self._document).write(path, encoding='utf-8', xml_declaration=True)


def to_osm(path: Path, kml):
    visited_squadrats = VisitedSquadrats()

    for name in ['squadrats', 'squadratinhos', 'ubersquadrat', 'ubersquadratinho']:
        with timeit(msg=f'Processing {name}'):
            placemark: Placemark = find(kml, name=name)
            visited_squadrats.placemark_to_osm(placemark=placemark, tags=[('name', name)])

    with timeit(msg=f'Writing {path}'):
        visited_squadrats.write_document(path=path)


def generate_mkgmap_config(config_path: pathlib.Path, config: VisitedSquadratsConfig, input: pathlib.Path):
    """Generate mkgmap config file
    """
    with config_path.open('w', encoding='UTF-8') as config_file:
        write_mkgmap_config_headers(file=config_file, config=config)

        config_file.write(f'mapname={config.img_family_id}0001\n')
        config_file.write(f'description={config.description}\n')
        config_file.write(f'input-file={input.relative_to(config.output_dir)}\n')

        config_file.write(f'input-file={config.typ_file}\n')
        config_file.write(f'description={config.description}\n')
        config_file.write("gmapsupp\n")

def parse_kml(path: pathlib.Path) -> KML:
    return KML.parse(path)

def main():
    parser = argparse.ArgumentParser(description="Convert Squadrat's 'visited squadrats' KML to Garmin IMG map")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='verbose output')
    parser.add_argument('-k', '--keep-output', action='store_true',
                        help='keep output files after processing')
    parser.add_argument('-i', '--input-file', required=True,
                        help="Squadrat's 'visited squadrats' KML")
    parser.add_argument('-o', '--output-file', required=True,
                        help='Output file')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    osm_file = OUTPUT_DIR / 'squadrats-visited.osm'
    mkgmap_config = OUTPUT_DIR / 'mkgmap.cfg'
    img_file = OUTPUT_DIR / 'squadrats-visited.img'

    config = VisitedSquadratsConfig({
        'img_family_id': IMG_FAMILY_ID_VISITED_SQUADRATS,
        'description': 'Visited Squadrats',
        'output': img_file.name
    })

    k: KML = parse_kml(Path(args.input_file))
    to_osm(path=osm_file, kml=k)

    generate_mkgmap_config(config_path=mkgmap_config, config=config, input=osm_file)
    run_mkgmap(config=mkgmap_config)

if __name__ == "__main__":
    main()