"""Classes and methods to work with OSM data
"""
import xml.etree.ElementTree as ET
from abc import ABC

# all squadratinhos
# 4^17 = 17 179 869 184
WAY_BASE_ID  = 100000000000

class OSMElement(ABC):
    """Abstract class representing an OSM element"""

    def __init__(self, name: str, element_id: int, tags: list[Tag] = None):
        self._name = name
        self._element_id = element_id
        self._tags = tags if tags else []

    @property
    def name(self) -> str:
        """Element name"""
        return self._name

    @property
    def element_id(self) -> int:
        """Element ID"""
        return self._element_id

    @property
    def tags(self) -> list[Tag]:
        """Element tags"""
        return self._tags

    def get_element_attributes(self):
        return {
            'id': str(self.element_id),
        }

    def to_xml(self) -> ET.Element:
        """Generate XML representation of Element
        """
        node = ET.Element(self.name, self.get_element_attributes())
        for (k, v) in self.tags:
            node.append(Tag(k, v).to_xml())

        return node


class Tag:
    """Representation of an OSM tag
    """
    def __init__(self, k: str, v: str):
        self.k = k
        self.v = v

    def to_xml(self) -> ET.Element:
        """Generate XML representation of Tag object
        """
        return ET.Element('tag', {
            'k': self.k,
            'v': str(self.v)
        })



class Node(OSMElement):
    """Representation of an OSM Node entity
       See https://wiki.openstreetmap.org/wiki/Node
    """

    lat : float = None
    """Node's latitude in degrees"""

    lon : float = None
    """Node's longitude in degrees"""

    def __init__(self, node_id: int, lat: float, lon: float, tags: list[Tag] = None) -> None:
        super().__init__(name='node', element_id=node_id, tags=tags)
        self.lat = lat
        self.lon = lon

    def __repr__(self) -> str:
        """String representation of the Node object
        """
        return f'Node(node_id={self.element_id}, lat={self.lat}, lon {self.lon})'

    def get_element_attributes(self) -> dict:
        return super().get_element_attributes() | {
            'lat': str(self.lat),
            'lon': str(self.lon)
        }


class NodeRef:
    """Representation of an OSM NodeRef entity
    """
    ref : int = None

    def __init__(self, node: Node) -> None:
        self.ref = node.element_id

    def to_xml(self) -> ET.Element:
        """Generate XML representation of NodeRef object
        """
        return ET.Element('nd', {
            'ref': str(self.ref)
        })

class Way(OSMElement):
    """Representation of an OSM Way entity
       See https://wiki.openstreetmap.org/wiki/Way
    """

    nodes: list[Node] = None
    """Ways' nodes"""

    def __init__(self, way_id: int, nodes: list[Node], tags: list[Tag] = None) -> None:
        super().__init__(name='way', element_id=way_id, tags=tags)
        self.nodes = nodes

    def to_xml(self) -> ET.Element:
        """Generate XML representation of Way object
        """
        way = super().to_xml()
        for node in self.nodes:
            way.append(NodeRef(node).to_xml())

        return way


class MultiPolygon(OSMElement):
    """Representation of an OSM MultiPolygon Relation entity
    See https://wiki.openstreetmap.org/wiki/Relation:multipolygon
    """

    outer_rings: list[Way]
    """List of outer rings"""

    inner_rings: list[Way]
    """List of inner rings"""

    def __init__(self, relation_id: int, outer_rings: list[Way], inner_rings: list[Way] = None, tags: list[Tag] = None) -> None:
        if not tags:
            tags = []
        tags = [Tag('type', 'multipolygon')] + tags
        super().__init__(name='relation', element_id=relation_id, tags=tags)
        self.outer_rings = outer_rings
        self.inner_rings = inner_rings if inner_rings else []

    def add_outer(self, way: Way) -> None:
        self.outer_rings.append(way)

    def add_inner(self, way: Way) -> None:
        self.inner_rings.append(way)

    def to_xml(self):
        """Generate XML representation of MultiPolygon object
        """
        relation = super().to_xml()
        # add members

        for way in self.outer_rings:
            relation.append(
                ET.Element('member', {
                    'type': 'way',
                    'ref': str(way.element_id),
                    'role': 'outer'
                })
            )

        for way in self.inner_rings:
            relation.append(
                ET.Element('member', {
                    'type': 'way',
                    'ref': str(way.element_id),
                    'role': 'inner'
                })
            )

        return relation

