import unittest
from common.poly import Poly

class TestPoly(unittest.TestCase):
    def test_wrong_format(self):
        """
        Test that it can recognize a proper filetype
        """
        with self.assertRaises(Exception) as cm:
            poly = Poly('tests/test_poly/wrong_format.poly')

        self.assertEqual(str(cm.exception), 'Expecting polygon filetype, got "not-polygon" instead')

    def test_pomorskie(self):
        """
        Test that it can load properly formatted POLY file
        """
        poly = Poly('tests/test_poly/pomorskie.poly')
        self.assertEqual(len(poly.coords), 215)
        self.assertEqual(poly.coords[0], [16.68, 54.58])
        self.assertEqual(poly.coords[100], [18.465, 53.665])
        self.assertEqual(poly.coords[200], [16.79, 54.35])
        self.assertEqual(poly.coords[214], [16.68, 54.58])
        

if __name__ == '__main__':
    unittest.main()