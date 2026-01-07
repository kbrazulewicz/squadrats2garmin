import unittest

from parameterized import parameterized

from squadrats2garmin.common.util import find_ranges, merge_ranges, merge_ranges_end_inclusive


class TestUtil(unittest.TestCase):
    def test_find_ranges(self):
        """ Test util.find_ranges method
        """

        # empty list
        self.assertEqual([], find_ranges([]))

        # one element list with a value
        self.assertEqual([(0, 0)], find_ranges([0]))
        self.assertEqual([(1, 1)], find_ranges([1]))
        self.assertEqual([(1, 3), (5, 5), (7, 8)], find_ranges([1, 2, 3, 5, 7, 8]))

    @parameterized.expand([
        ([], []),
        ([(1, 2), (3, 4)], [(1, 2), (3, 4)]),
        ([(1, 4)], [(1, 3), (3, 4)]),
        ([(1, 4)], [(1, 3), (2, 4)]),
        ([(1, 4)], [(1, 4), (2, 3)]),
    ])
    def test_merge_ranges(self, expected: list[tuple[int, int]], ranges: list[tuple[int, int]]) -> None:
        """
        Test util.merge_ranges method
        """
        self.assertEqual(expected, merge_ranges(ranges))

    @parameterized.expand([
        ([], []),
        ([(1, 4)], [(1, 2), (3, 4)]),
        ([(1, 4)], [(1, 3), (3, 4)]),
        ([(1, 4)], [(1, 3), (2, 4)]),
        ([(1, 4)], [(1, 4), (2, 3)]),
    ])
    def test_merge_ranges_end_inclusive(self, expected: list[tuple[int, int]], ranges: list[tuple[int, int]]) -> None:
        """
        Test util.merge_ranges method
        """
        self.assertEqual(expected, merge_ranges_end_inclusive(ranges))

if __name__ == '__main__':
    unittest.main()