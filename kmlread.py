import argparse
import itertools
import logging
import pathlib
import xml.etree.ElementTree as ET
from pathlib import Path

from typing import Iterator

from fastkml import KML
from fastkml.utils import find
from fastkml import Placemark
from pygeoif import LinearRing, MultiPolygon, Polygon

import common.osm
from common.config import VisitedSquadratsConfig, IMG_FAMILY_ID_VISITED_SQUADRATS, OUTPUT_DIR
from common.mkgmap import run_mkgmap, write_mkgmap_config_headers
from common.timer import timeit

logger = logging.getLogger(__name__)

def linear_ring_to_way(geom: LinearRing, id_generator: Iterator[int]) -> common.osm.Way:
    """Parse pygeoif.LinearRing"""
    # first and last node are the same and this needs to be the same object in OSM file
    nodes = [
        common.osm.Node(node_id=next(id_generator), lon=point[0], lat=point[1])
        for point in itertools.islice(geom.coords, 0, len(geom.coords) - 1)
    ]
    nodes.append(nodes[0])
    return common.osm.Way(way_id=next(id_generator), nodes=nodes)

def parse_polygons(geoms: Iterator[Polygon], id_generator: Iterator[int], tags: list[common.osm.Tag]=None) -> common.osm.MultiPolygon:
    """Parse pygeoif.Polygon"""
    outer: list[common.osm.Way] = []
    inner: list[common.osm.Way] = []

    with timeit(msg='Building OSM data structure'):
        for geom in geoms:
            outer.append(linear_ring_to_way(geom=geom.exterior, id_generator=id_generator))
            for i in geom.interiors:
                inner.append(linear_ring_to_way(geom=i, id_generator=id_generator))

        return common.osm.MultiPolygon(relation_id=next(id_generator), outer_rings=outer, inner_rings=inner, tags=tags)

def placemark_to_osm(document: ET.Element, placemark: Placemark, id_generator: Iterator[int], tags: list[common.osm.Tag]):
    """Write fastkml.Placemark to OSM XML"""
    multipolygon: common.osm.MultiPolygon
    if isinstance(placemark.geometry, MultiPolygon):
        multipolygon = parse_polygons(geoms=placemark.geometry.geoms, id_generator=id_generator, tags=tags)
    elif isinstance(placemark.geometry, Polygon):
        multipolygon = parse_polygons(geoms=[placemark.geometry], id_generator=id_generator, tags=tags)
    else:
        return

    nodes: set[common.osm.Node] = set()
    ways: set[common.osm.Way] = set()
    for way in itertools.chain(multipolygon.outer_rings, multipolygon.inner_rings):
        nodes.update(way.nodes)
        ways.add(way)

    # nodes first
    document.extend(e.to_xml() for e in sorted(nodes, key=lambda e: e.element_id))
    # then ways
    document.extend(e.to_xml() for e in sorted(ways, key=lambda e: e.element_id))
    # then relation
    document.append(multipolygon.to_xml())


def to_osm(path: Path, kml):
    document = ET.Element("osm", {"version": '0.6'})
    id_generator: Iterator[int] = itertools.count(start=1)

    for name in ['squadrats', 'squadratinhos', 'ubersquadrat', 'ubersquadratinho']:
        with timeit(msg=f'Processing {name}'):
            placemark: Placemark = find(kml, name=name)
            placemark_to_osm(document=document, placemark=placemark, id_generator=id_generator, tags=[('name', name)])

    ET.indent(document)
    ET.ElementTree(document).write(path, encoding='utf-8', xml_declaration=True)


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

    k: KML
    with timeit(msg=f'Processing {args.input_file}'):
        k = KML.parse(Path(args.input_file))

    with timeit(msg=f'Writing {osm_file}'):
        to_osm(path=osm_file, kml=k)

    generate_mkgmap_config(config_path=mkgmap_config, config=config, input=osm_file)
    run_mkgmap(config=mkgmap_config)

if __name__ == "__main__":
    main()