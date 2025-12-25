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