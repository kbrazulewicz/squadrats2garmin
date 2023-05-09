#! /usr/bin/python3
import json
import sys
import xml.etree.ElementTree as ET

from common import poly, tile
from common.poly import Poly
from common.tile import ZOOM_SQUADRATS
from common.tile import ZOOM_SQUADRATINHOS
from common.timer import timeit


def generateOsmFile(input: str, output: str, zoom: int):
    poly = Poly(input)

    with timeit('generate_tiles'):
        tiles = poly.generate_tiles(zoom)

    print(f'{len(tiles)} tiles')

    with timeit('generate_grid'):
        ways = tile.generate_grid(tiles)
        
    print(f'{len(ways)} ways')

    uniqueNodes = set()
    with timeit('collect unique nodes'):
        for w in ways:
            uniqueNodes.update(w.nodes)

    print(f'{len(uniqueNodes)} unique nodes')

    with timeit('build OSM document'):
        document = ET.Element('osm', {"version": '0.6'})
        document.extend(n.to_xml() for n in sorted(uniqueNodes, key=lambda node: node.id))
        document.extend(w.to_xml() for w in sorted(ways, key=lambda way: way.id))
        ET.indent(document)

    with timeit('write OSM document'):
        ET.ElementTree(document).write(output, encoding='utf-8', xml_declaration=True)
        # ET.ElementTree(document).write(sys.stdout.buffer, encoding='utf-8', xml_declaration=True)


def processOptionsFile(filename):
	with open(filename) as optionsFile:
		options = json.load(optionsFile)
		zoom = 1
		match options['zoom']:
			case 'squadrats':
				zoom = ZOOM_SQUADRATS
			case 'squadratinhos':
				zoom = ZOOM_SQUADRATINHOS
			case _:
				print('Allowed zoom values are: [squadrats, squadratinhos]', file=sys.stderr)
				return 0

if __name__ == "__main__":
    match len(sys.argv):
        case 2:
            processOptionsFile(sys.argv[1])
        case _:
            generateOsmFile(input='tests/test_poly/pomorskie.poly', output='pomorskie.osm', zoom=ZOOM_SQUADRATINHOS)