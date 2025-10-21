import unittest

from common.tile import Tile
from common.zoom import ZOOM_SQUADRATS

class TestTile(unittest.TestCase):
    def test_tile_at(self):
        """Test Tile.tile_at method
        """

        self.assertEqual(Tile(8192, 8192, ZOOM_SQUADRATS), Tile.tile_at(  0,   0, ZOOM_SQUADRATS))

        self.assertEqual(Tile(8647, 8649, ZOOM_SQUADRATS), Tile.tile_at(-10,  10, ZOOM_SQUADRATS))
        self.assertEqual(Tile(8647, 8192, ZOOM_SQUADRATS), Tile.tile_at(  0,  10, ZOOM_SQUADRATS))
        self.assertEqual(Tile(8647, 7734, ZOOM_SQUADRATS), Tile.tile_at( 10,  10, ZOOM_SQUADRATS))
        self.assertEqual(Tile(8192, 7734, ZOOM_SQUADRATS), Tile.tile_at( 10,   0, ZOOM_SQUADRATS))
        self.assertEqual(Tile(7736, 7734, ZOOM_SQUADRATS), Tile.tile_at( 10, -10, ZOOM_SQUADRATS))
        self.assertEqual(Tile(7736, 8192, ZOOM_SQUADRATS), Tile.tile_at(  0, -10, ZOOM_SQUADRATS))
        self.assertEqual(Tile(7736, 8649, ZOOM_SQUADRATS), Tile.tile_at(-10, -10, ZOOM_SQUADRATS))
        self.assertEqual(Tile(8192, 8649, ZOOM_SQUADRATS), Tile.tile_at(-10,   0, ZOOM_SQUADRATS))

if __name__ == '__main__':
    unittest.main()