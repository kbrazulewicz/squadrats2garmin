#! /usr/bin/python3

from collections import defaultdict

from common import poly, tile
from common.poly import Poly
from common.tile import ZOOM_SQUADRATINHOS
from common.timer import timeit

poly = Poly('tests/test_poly/pomorskie.poly')

with timeit('generate_tiles'):
    tiles = poly.generate_tiles(ZOOM_SQUADRATINHOS)

print(len(tiles))

with timeit('generate_grid'):
    ways = tile.generate_grid(tiles)
    
print(len(ways))