import unittest

from common.tile import ZOOM_SQUADRATS
from common.tile import ZOOM_SQUADRATINHOS

class TestZoom(unittest.TestCase):
    """Test functionality provided by the Zoom module"""

    def test_lat(self):
        # squadrats
        for (y, lat) in [(4096, 66.513260), (8192, 0.0), (12288, -66.513260)]:
            with self.subTest(y = y, lat = lat):
                self.assertAlmostEqual(ZOOM_SQUADRATS.lat(y), lat, places = 6)

        # squadratinhos
        for (y, lat) in [(32768, 66.513260), (65536, 0.0), (98304, -66.513260)]:
            with self.subTest(y = y, lat = lat):
                self.assertAlmostEqual(ZOOM_SQUADRATINHOS.lat(y), lat, places = 6)
    
if __name__ == '__main__':
    unittest.main()