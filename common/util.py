def find_ranges(nums: list[int]) -> list[tuple[int, int]]:
    if not nums: return []

    result: list[tuple[int, int]] = []
    nL: int = nums[0]
    nR: int = None

    for n in sorted(nums):
        if nR and nR + 1 != n:
            result.append((nL, nR))
            nL = n
        nR = n

    result.append((nL, nR))

    return result

def merge_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not ranges: return []

    result: list[tuple[int, int]] = []
    currentRange: tuple[int, int] = None

    for range in sorted(ranges, key = lambda r: r[0]):
        if not currentRange: 
            currentRange = range
        elif currentRange[1] >= range[0]:
            # overlap
            currentRange = (currentRange[0], max(currentRange[1], range[1]))
        else:
            # no overlap
            result.append(currentRange)
            currentRange = range

    result.append(currentRange)
    return result

def make_ranges_end_inclusive(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Convert ranges representing tile's top-left corner to reach next tile's top-left corner"""
    return [(l, r + 1) for (l, r) in ranges]



def _generate_tiles_along_the_line(pointA: tuple[int], pointB: tuple[int], zoom: int):
    """Generate tiles along the line
    """
    tiles: list[Tile] = []
    # tileA is the northernmost tile of the range, tileB is the southernmost tile of the range (but not necessarily the nothern/southern end of the line)
    (tileA, tileB) = sorted([Tile.tile_at(lon = point[0], lat = point[1], zoom = zoom) for point in (pointA, pointB)], key=lambda tile:tile.y)

    # x1 is the Tile.x of the northern end of line
    x1: int = tileA.x
    x2: int = None
    # starting from the second row
    for y in range(tileA.y + 1, tileB.y + 1):
        # TODO calculate longitude where tile latitude intersects with the line
        tile1 = Tile(x = x1, y = y, zoom = zoom)
        (lonA, latA) = pointA
        (lonB, latB) = pointB
        lat = tile1.lat
        lon = (lonA * (latB - lat) - lonB * (latA - lat)) / (latB - latA)
        tile2 = Tile.tile_at(lon = lon, lat = lat, zoom = zoom)
        x2 = tile2.x
        # list of tiles overlapping in the y - 1 row
        tiles.extend(Tile(x, y - 1, zoom) for x in range(min(x1, x2), max(x1, x2) + 1))
        x1 = x2

    # add last row
    tiles.extend(Tile(x, tileB.y, zoom) for x in range(min(x1, tileB.x), max(x1, tileB.x) + 1))
    
    return tiles