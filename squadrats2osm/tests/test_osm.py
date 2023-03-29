import sys
import unittest
import xml.etree.ElementTree as ET

from common.osm import Node

class TestNode(unittest.TestCase):
    def test_node_to_xml(self):
        """Test building an XML element for simple Node"""
        node = Node(id = 123, lat = 12.34, lon = 56.78)
        elem = node.to_xml()

        self.assertDictEqual(elem.attrib, {'id' : '123', 'lat' : '12.34', 'lon' : '56.78'})

    def test_node_with_tags_to_xml(self):
        """Test building an XML element for Node with tags"""
        node = Node(id = 123, lat = 12.34, lon = 56.78, tags=[('k1', 'v1'), ('k2', 'v2'), ('k2', 'v2')])
        elem = node.to_xml()

        self.assertDictEqual(elem.attrib, {'id' : '123', 'lat' : '12.34', 'lon' : '56.78'})
        self.assertEqual(len(elem), 3)
        self.assertEqual(elem[0].tag, 'tag')
        self.assertDictEqual(elem[0].attrib, {'k' : 'k1', 'v' : 'v1'})
        self.assertEqual(elem[1].tag, 'tag')
        self.assertDictEqual(elem[1].attrib, {'k' : 'k2', 'v' : 'v2'})
        self.assertEqual(elem[2].tag, 'tag')
        self.assertDictEqual(elem[2].attrib, {'k' : 'k2', 'v' : 'v2'})

if __name__ == '__main__':
    unittest.main()