import sys
import unittest
import xml.etree.ElementTree as ET

from common.osm import Node

class TestNode(unittest.TestCase):
    def test_node_to_xml(self):
        """Test building an XML element"""
        node = Node(id = 123, lat = 12.34, lon = 56.78)
        elem = node.to_xml()

        self.assertDictEqual(elem.attrib, {'id' : '123', 'lat' : '12.34', 'lon' : '56.78'})

    def test_node_with_tags_to_xml(self):
        """Test building an XML element"""
        node = Node(id = 123, lat = 12.34, lon = 56.78, tags=[('k1', 'v1'), ('k2', 'v2'), ('k2', 'v2')])
        elem = node.to_xml()

        ET.ElementTree(elem).write(sys.stdout.buffer, encoding='utf-8', xml_declaration=True)

        self.assertDictEqual(elem.attrib, {'id' : '123', 'lat' : '12.34', 'lon' : '56.78'})

if __name__ == '__main__':
    unittest.main()