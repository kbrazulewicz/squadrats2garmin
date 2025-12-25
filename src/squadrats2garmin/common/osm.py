"""Classes and methods to work with OSM data
"""
import xml.etree.ElementTree as ET
from abc import ABC

from pygeoif.types import Point2D

# all squadratinhos
# 4^17 = 17 179 869 184
WAY_BASE_ID  = 100000000000

type Tag = tuple[str, str]

class OSMElement(ABC):
    """Abstract class representing an OSM element"""

    def __init__(self, name: str, element_id: int, tags: list[Tag] = None):
        self._name = name
        self._element_id = element_id
        self._tags = tags if tags else []

    def __hash__(self) -> int:
        return hash((self.name, self.element_id))

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, OSMElement):
            return self.name == __o.name and self.element_id == __o.element_id
        return NotImplemented


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
        node.extend(
            ET.Element('tag', {'k': tag[0], 'v': str(tag[1])})
            for tag in self.tags
        )
        return node

    @staticmethod
    def element_to_xml(name: str, attrs: dict, tags: list[Tag]) -> ET.Element:
        element = ET.Element(name, attrs)
        element.extend(
            ET.Element('tag', {'k': tag[0], 'v': str(tag[1])})
            for tag in tags
        )
        return element


class Node(OSMElement):
    """Representation of an OSM Node entity
       See https://wiki.openstreetmap.org/wiki/Node
    """

    _geom: Point2D
    """[0] is longitude, [1] is latitude"""

    def __init__(self, node_id: int, geom: Point2D, tags: list[Tag] = None) -> None:
        super().__init__(name='node', element_id=node_id, tags=tags)
        self._geom = geom

    def __repr__(self) -> str:
        """String representation of the Node object
        """
        return f'Node(node_id={self.element_id}, lat={self.lat}, lon {self.lon})'

    @property
    def lon(self):
        return self._geom[0]

    @property
    def lat(self):
        return self._geom[1]

    def get_element_attributes(self) -> dict:
        return super().get_element_attributes() | {
            'lat': str(self.lat),
            'lon': str(self.lon)
        }


class Way(OSMElement):
    """Representation of an OSM Way entity
       See https://wiki.openstreetmap.org/wiki/Way
    """

    nodes: list[Node] = None
    """Ways' nodes"""

    _refs: list[int] = None

    def __init__(self, way_id: int, refs: list[int] = None, nodes: list[Node] = None, tags: list[Tag] = None) -> None:
        super().__init__(name='way', element_id=way_id, tags=tags)
        if refs:
            self._refs = refs
        elif nodes:
            self.nodes = nodes
            self._refs = [node.element_id for node in nodes]
        else:
            raise

    def to_xml(self) -> ET.Element:
        """Generate XML representation of Way object
        """
        way = super().to_xml()
        for ref in self._refs:
            way.append(
                ET.Element('nd', {
                    'ref': str(ref)
                })
            )

        return way

    @staticmethod
    def way_to_xml(element_id: int, refs: list[int]) -> ET.Element:
        way = ET.Element('way', {'id': str(element_id)})
        for ref in refs:
            way.append(ET.Element('nd', {'ref': str(ref)}))

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
        tags = [('type', 'multipolygon')] + tags
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


    @staticmethod
    def element_to_xml(element_id: int, outer_rings: list[int], inner_rings: list[int] = None, tags: list[Tag] = None) -> ET.Element:
        if not tags:
            tags = []
        tags = [('type', 'multipolygon')] + tags

        relation = OSMElement.element_to_xml('relation', {'id': str(element_id)}, tags=tags)
        for way_id in outer_rings:
            relation.append(
                ET.Element('member', {
                    'type': 'way',
                    'ref': str(way_id),
                    'role': 'outer'
                })
            )

        for way_id in inner_rings:
            relation.append(
                ET.Element('member', {
                    'type': 'way',
                    'ref': str(way_id),
                    'role': 'inner'
                })
            )

        return relation

