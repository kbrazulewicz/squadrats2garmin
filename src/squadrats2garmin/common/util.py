from collections.abc import Iterable


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

def merge_ranges(ranges: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    merged = []
    for r in sorted(ranges, key=lambda x: x[0]):
        if not merged or merged[-1][1] < r[0]:
            merged.append(r)
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], r[1]))

    return merged

def merge_ranges_end_inclusive(ranges: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    merged = []
    for r in sorted(ranges, key=lambda x: x[0]):
        if not merged or merged[-1][1] + 1 < r[0]:
            merged.append(r)
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], r[1]))

    return merged

def make_ranges_end_inclusive(ranges: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    """Convert ranges representing tile's top-left corner to reach next tile's top-left corner"""
    return [(l, r + 1) for (l, r) in ranges]
