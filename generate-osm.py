#! /usr/bin/python3

import json
import math
import sys
import xml.etree.ElementTree as ET


def deg2num(coordinates_deg, zoom):
    """ Lon./lat. to tile numbers """
    lat_deg, lon_deg = coordinates_deg
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def num2deg(xtile, ytile, zoom):
    """ Tile numbers to lon./lat. """
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)


def dms2deg(deg, min, sec):
    return deg + (min / 60) + (sec / 60 / 60)


def tileId(x, y, zoom):
    n = 2 ** zoom
    return str(y * n + x)

def nodeId(x, y, zoom):
    n = 2 ** zoom
    return "-" + tileId(x, y, zoom)

def outerBoundaryId(x, y, zoom):
    n = 2 ** zoom
    return "-1" + tileId(x, y, zoom)

def gridLineId(x1, y1, x2, y2, zoom):
    horizontal = y1 == y2
    n = 2 ** zoom
    if horizontal:
        return "-2" + tileId(x1, y1, zoom)
    else:
        return "-3" + tileId(x1, y1, zoom)


def tile2NodeElement(x, y, zoom):
    lat, lon = num2deg(x, y, zoom)
    attrib = {
        "id": nodeId(x, y, zoom),
        "lat": str(lat),
        "lon": str(lon)
    }
    return ET.Element('node', attrib)

def tileOuterBoundary(x, y, zoom):
    attrib = {
        "id": outerBoundaryId(x, y, zoom),
    }

    way = ET.Element('way', attrib)
    way.append(ET.Element('nd', {"ref": nodeId(x, y, zoom)}))
    way.append(ET.Element('nd', {"ref": nodeId(x + 1, y, zoom)}))
    way.append(ET.Element('nd', {"ref": nodeId(x + 1, y + 1, zoom)}))
    way.append(ET.Element('nd', {"ref": nodeId(x, y + 1, zoom)}))
    way.append(ET.Element('nd', {"ref": nodeId(x, y, zoom)}))

    way.append(ET.Element('tag', {"k": "contour", "v": "elevation"}))

    return way

def gridLine(x1, y1, x2, y2, zoom):
    horizontal = y1 == y2
    attrib = {
        "id": gridLineId(x1, y1, x2, y2, zoom),
    }

    way = ET.Element('way', attrib)
    if horizontal:
        for x in range(x1, x2 + 1):
            way.append(ET.Element('nd', {"ref": nodeId(x, y1, zoom)}))
    else:
        for y in range(y1, y2 + 1):
            way.append(ET.Element('nd', {"ref": nodeId(x1, y, zoom)}))

    way.append(ET.Element('tag', {"k": "contour", "v": "elevation"}))

    return way

#
# Convert area to OSM structure:
# - node for every square corner
# - closed way for every square
#
def area2Elements(area, zoom):
    min_x, min_y = deg2num((area["n"], area["w"]), zoom)
    max_x, max_y = deg2num((area["s"], area["e"]), zoom)

    elements = []
    # nodes for the tile corners
    for y in range(min_y, max_y + 2):
        for x in range(min_x, max_x + 2):
            elements.append(tile2NodeElement(x, y, zoom))

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            elements.append(tileOuterBoundary(x, y, zoom))

    return elements


#
# Convert area to OSM structure:
# - node for every square corner on the boundary
# - ways forming a grid
#
def area2Grid(area, zoom):
    min_x, min_y = deg2num((area["n"], area["w"]), zoom)
    max_x, max_y = deg2num((area["s"], area["e"]), zoom)

    elements = []
    # nodes for the tile corners
    for y in range(min_y, max_y + 2):
        for x in range(min_x, max_x + 2):
            elements.append(tile2NodeElement(x, y, zoom))

    # ways N -> S
    for x in range(min_x, max_x + 2):
        elements.append(gridLine(x, min_y, x, max_y + 1, zoom))

    # ways W -> E
    for y in range(min_y, max_y + 2):
        elements.append(gridLine(min_x, y, max_x + 1, y, zoom))

    return elements


def area2osm(area, zoom):
    document = ET.Element('osm', {"version": '0.6'})
    document.extend(area2Grid(area, zoom))
    ET.indent(document)
    return document
    

ZOOM_SQUADRATS = 14
ZOOM_SQUADRATINHOS = 17

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

	ET.ElementTree(area2osm(options['area'], zoom)).write(sys.stdout.buffer, encoding='utf-8', xml_declaration=True)
			

match len(sys.argv):
	case 2:
		processOptionsFile(sys.argv[1])
