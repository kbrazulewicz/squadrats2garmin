import unittest

from parameterized import parameterized

from squadrats2garmin.common.tile import ZOOM_SQUADRATS
from squadrats2garmin.common.tile import ZOOM_SQUADRATINHOS


class TestZoom(unittest.TestCase):
    """Test functionality provided by the Zoom module"""

    @parameterized.expand([(4096, 66.513260), (8192, 0.0), (12288, -66.513260)])
    def test_lat_zoom_squadrats(self, y: int, lat: float):
        self.assertAlmostEqual(ZOOM_SQUADRATS.lat(y), lat, places=6)

    @parameterized.expand([(32768, 66.513260), (65536, 0.0), (98304, -66.513260)])
    def test_lat_zoom_squadratinhos(self, y: int, lat: float):
        self.assertAlmostEqual(ZOOM_SQUADRATINHOS.lat(y), lat, places=6)

    def test_to_tile(self):
        """Test Zoom.to_tile method"""
        for (lon, lat, x, y) in [
            (  0,   0, 8192, 8192),
            ( 10, -10, 8647, 8649),
            ( 10,   0, 8647, 8192),
            ( 10,  10, 8647, 7734),
            (  0,  10, 8192, 7734),
            (-10,  10, 7736, 7734),
            (-10,   0, 7736, 8192),
            (-10, -10, 7736, 8649),
            (  0, -10, 8192, 8649),
        ]:
            with self.subTest(lon=lon, lat=lat, x=x, y=y):
                tile = ZOOM_SQUADRATS.to_tile((lon, lat))
                self.assertEqual(tile.x, x)
                self.assertEqual(tile.y, y)
        pass

if __name__ == '__main__':
    unittest.main()