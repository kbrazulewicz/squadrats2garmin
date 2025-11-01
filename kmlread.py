import itertools
import pathlib
import xml.etree.ElementTree as ET
from pathlib import Path

from typing import Iterator

from fastkml import KML
from fastkml.utils import find, find_all
from fastkml import Placemark
from pygeoif import LinearRing, MultiPolygon, Polygon

import common.osm
from common.config import OUTPUT_PATH, IMG_FAMILY_ID, IMG_FAMILY_NAME, IMG_SERIES_NAME
from common.mkgmap import run_mkgmap


def linear_ring_to_way(geom: LinearRing, node_id: Iterator[int], way_id: Iterator[int]) -> common.osm.Way:
    # first and last node are the same and this needs to be the same object in OSM file
    nodes = [
        common.osm.Node(node_id=next(node_id), lon=point[0], lat=point[1])
        for point in itertools.islice(geom.coords, 0, len(geom.coords) - 1)
    ]
    nodes.append(nodes[0])
    return common.osm.Way(way_id=next(way_id), nodes=nodes)

def multipolygon_to_relation(geom: MultiPolygon, tags: list[common.osm.Tag]=None) -> common.osm.MultiPolygon:
    node_id: Iterator[int] = itertools.count(start=1)
    way_id: Iterator[int] = itertools.count(start=1)
    relation_id: Iterator[int] = itertools.count(start=1)

    outer: list[common.osm.Way] = []
    inner: list[common.osm.Way] = []

    for geom in geom.geoms:
        outer.append(linear_ring_to_way(geom=geom.exterior, node_id=node_id, way_id=way_id))
        for i in geom.interiors:
            inner.append(linear_ring_to_way(geom=i, node_id=node_id, way_id=way_id))

    return common.osm.MultiPolygon(relation_id=next(relation_id), outer_rings=outer, inner_rings=inner, tags=tags)

def to_osm(path: Path, kml):
    squadrats: Placemark = find(kml, name='squadrats')

    if isinstance(squadrats.geometry, MultiPolygon):
        osm_relation = multipolygon_to_relation(geom=squadrats.geometry, tags=[common.osm.Tag('name', 'squadrats')])
        nodes: set[common.osm.Node] = set()
        ways: set[common.osm.Way] = set()
        for way in itertools.chain(osm_relation.outer_rings, osm_relation.inner_rings):
            nodes.update(way.nodes)
            ways.add(way)

        document = ET.Element("osm", {"version": '0.6'})
        # nodes first
        document.extend(e.to_xml() for e in sorted(nodes, key=lambda e: e.element_id))
        # then ways
        document.extend(e.to_xml() for e in sorted(ways, key=lambda e: e.element_id))
        # then relation
        document.append(osm_relation.to_xml())
        ET.indent(document)
        ET.ElementTree(document).write(path, encoding='utf-8', xml_declaration=True)


def generate_mkgmap_config(output: pathlib.Path, input: pathlib.Path):
    """Generate mkgmap config file
    """
    with output.open('w', encoding='UTF-8') as config_file:
        # images with 'unicode' encoding are not displayed on Garmin
        config_file.write('latin1\n')
        config_file.write('transparent\n')
        config_file.write(f'output-dir={OUTPUT_PATH.name}\n')

        config_file.write(f'family-id={IMG_FAMILY_ID}\n')
        config_file.write(f'family-name={IMG_FAMILY_NAME}\n')
        config_file.write('product-id=1\n')
        config_file.write(f'series-name={IMG_SERIES_NAME}\n')

        config_file.write('style-file=etc/squadrats-default.style\n')

        config_file.write(f'mapname={IMG_FAMILY_ID}0001\n')
        config_file.write('description=Visited squadrats\n')
        config_file.write(f'input-file={input.relative_to(OUTPUT_PATH)}\n')

        config_file.write('input-file=../etc/squadrats.typ.txt\n')
        config_file.write(f'description=Visited squadrats\n')
        config_file.write("gmapsupp\n")


kml_file=Path('squadrats-2025-10-24.kml')
osm_file=Path('output/squadrats-2025-10-24.osm')
mkgmap_config=Path('output/mkgmap.cfg')
img_file=Path('output/squadrats-2025-10-24.img')

k = KML.parse(kml_file)
to_osm(path=osm_file, kml=k)
generate_mkgmap_config(output=mkgmap_config, input=osm_file)
run_mkgmap(config=mkgmap_config)

# https://wiki.openstreetmap.org/wiki/Relation:multipolygon#Examples_in_XML