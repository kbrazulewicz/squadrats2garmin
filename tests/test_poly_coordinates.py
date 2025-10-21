import unittest

from common.poly import Coordinates

class TestPolyCoordinates(unittest.TestCase):
    """Test functionality provided by the Coordinates"""

    def test_constructor_with_ordered_arguments(self):
        """Test constructor with ordered arguments"""
        (lat, lon) = (1.23, 3.45)

        coordinates = Coordinates(lat, lon)
        self.assertEqual(coordinates.lat, lat)
        self.assertEqual(coordinates.lon, lon)

    def test_constructor_from_tuple(self):
        """Test constructor from tuple"""
        (lat, lon) = (1.23, 3.45)
        coordinatesTuple = (lat, lon)

        coordinates = Coordinates(*coordinatesTuple)
        self.assertEqual(coordinates.lat, lat)
        self.assertEqual(coordinates.lon, lon)

    def test_equals(self):
        """Test constructor from tuple"""
        (lat, lon) = (1.23, 3.45)
        coordinatesTuple = (lat, lon)

        coordinates1 = Coordinates(lat, lon)
        coordinates2 = Coordinates(lat, lon)
        coordinates3 = Coordinates(lat + 1, lon + 1)
        self.assertEqual(coordinates1, coordinates2)
        self.assertNotEqual(coordinates1, coordinates3)

if __name__ == '__main__':
    unittest.main()