import unittest

from parameterized import parameterized

from squadrats2garmin.common.tile import ZOOM_SQUADRATS
from squadrats2garmin.common.tile import ZOOM_SQUADRATINHOS


class TestZoom(unittest.TestCase):
    """Test functionality provided by the Zoom module"""

    @parameterized.expand([(4096, 66.513260), (8192, 0.0), (12288, -66.513260)])
    def test_lat_zoom_squadrats(self, y: int, lat: float):
        self.assertAlmostEqual(lat, ZOOM_SQUADRATS.lat(y), places=6)

    @parameterized.expand([(32768, 66.513260), (65536, 0.0), (98304, -66.513260)])
    def test_lat_zoom_squadratinhos(self, y: int, lat: float):
        self.assertAlmostEqual(lat, ZOOM_SQUADRATINHOS.lat(y), places=6)

    @parameterized.expand([
        (7736, -10),
        (8192, 0),
        (8647, 10),
    ])
    def test_x(self, expected: int, lon: float):
        self.assertEqual(expected, ZOOM_SQUADRATS.x(lon))

    @parameterized.expand([
        (8649, -10),
        (8192, 0),
        (7734, 10),
    ])
    def test_y(self, expected: int, lat: float):
        self.assertEqual(expected, ZOOM_SQUADRATS.y(lat))


if __name__ == '__main__':
    unittest.main()
