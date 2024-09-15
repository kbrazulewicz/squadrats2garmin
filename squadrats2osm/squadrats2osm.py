#! /usr/bin/python3
import json
import pathlib
import subprocess
import sys
import xml.etree.ElementTree as ET

from common import poly, tile
from common.job import Job
from common.poly import Poly
from common.squadrats import generate_grid
from common.squadrats import generate_tiles
from common.zoom import Zoom
from common.zoom import ZOOM_SQUADRATS
from common.zoom import ZOOM_SQUADRATINHOS
from common.timer import timeit


def generateOsmFile(input: pathlib.Path, output: pathlib.Path, zoom: Zoom):
    print(f'Generating tiles for {str(input)}, zoom level {zoom.zoom}')

    job: Job = Job(name=input.name, zoom=zoom)
    poly = Poly(str(input))

    with timeit(f'{job.name}: generate_tiles'):
        tiles = generate_tiles(poly=poly, job=job)

    print(f'{job.name}: {sum(map(len, tiles.values()))} tiles')

    with timeit(f'{job.name}: generate_grid'):
        ways = generate_grid(tiles=tiles, job=job)
        
    print(f'{job.name}: {len(ways)} ways')

    uniqueNodes = set()
    with timeit(f'{job.name}: collect unique nodes'):
        for w in ways:
            uniqueNodes.update(w.nodes)

    print(f'{job.name}: {len(uniqueNodes)} unique nodes')

    with timeit(f'{job.name}: build OSM document'):
        document = ET.Element('osm', {"version": '0.6'})
        document.extend(n.to_xml() for n in sorted(uniqueNodes, key=lambda node: node.id))
        document.extend(w.to_xml() for w in sorted(ways, key=lambda way: way.id))
        ET.indent(document)

    with timeit(f'{job.name}: write OSM document'):
        output.parent.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(document).write(str(output), encoding='utf-8', xml_declaration=True)
        # ET.ElementTree(document).write(sys.stdout.buffer, encoding='utf-8', xml_declaration=True)

def processJob(job: dict):
    input = pathlib.Path(job['poly'])
    zoom = None
    match job['zoom']:
        case 'squadrats':
            zoom = ZOOM_SQUADRATS
        case 'squadratinhos':
            zoom = ZOOM_SQUADRATINHOS
        case _:
            print(f'job {id}: allowed zoom values are: [squadrats, squadratinhos]', file=sys.stderr)
            return 0

    if input.is_file():
        osmFilePath = pathlib.Path(job['osm'].replace('{name}', input.stem))
        generateOsmFile(input, osmFilePath, zoom)

    elif input.is_dir():
        for poly in input.glob('*.poly'):
            output = pathlib.Path(job['osm'].replace('{name}', poly.stem))
            generateOsmFile(poly, output, zoom)


def processOptionsFile(filename):
    with open(filename) as optionsFile:
        options = json.load(optionsFile)
        for job in options['jobs']:
            processJob(job)


if __name__ == "__main__":
    match len(sys.argv):
        case 2:
            processOptionsFile(sys.argv[1])
        case _:
            generateOsmFile(input=pathlib.Path('tests/test_poly/pomorskie.poly'), output=pathlib.Path('pomorskie.osm'), zoom=ZOOM_SQUADRATINHOS)