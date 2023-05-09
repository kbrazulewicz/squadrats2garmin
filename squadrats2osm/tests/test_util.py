import unittest

from common.util import find_ranges
from common.util import merge_ranges

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

    def test_merge_ranges(self):
        """ Test util.merge_ranges method
        """

        # empty list
        self.assertEqual([], merge_ranges([]))

        self.assertEqual([(1, 3)], merge_ranges([(1, 3)]))
        self.assertEqual([(1, 2), (3, 4)], merge_ranges([(1, 2), (3, 4)]))
        self.assertEqual([(1, 4)], merge_ranges([(1, 3), (3, 4)]))
        self.assertEqual([(1, 4)], merge_ranges([(1, 3), (2, 4)]))
        self.assertEqual([(1, 4)], merge_ranges([(1, 4), (2, 3)]))

        self.assertEqual([(1, 4)], merge_ranges([(1, 2), (3, 4)]))

if __name__ == '__main__':
    unittest.main()