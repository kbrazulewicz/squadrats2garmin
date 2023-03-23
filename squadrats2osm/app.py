#! /usr/bin/python3

import sys
from collections import defaultdict

from common.poly import Poly
from common.tile import ZOOM_SQUADRATINHOS

poly = Poly('tests/test_poly/pomorskie.poly')
tiles = poly.generate_tiles(ZOOM_SQUADRATINHOS)

tilesByY = defaultdict(list)
for tile in tiles:
    tilesByY[tile.y].append(tile)

for x in tilesByY.values():
    x.sort(key=lambda tile: tile.x)
    print(x)


# sort tiles by y, x
# generate horizontal lines
# merge horizontal lines

# sort tiles by x, y
# generate vertical lines
# merge vertical lines

print(len(tiles))