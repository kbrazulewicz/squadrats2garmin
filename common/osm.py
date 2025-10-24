"""Classes and methods to work with OSM data
"""
import xml.etree.ElementTree as ET

# all squadratinhos
# 4^17 = 17 179 869 184
WAY_BASE_ID  = 100000000000

class Tag:
    """Representation of an OSM tag
    """
    def __init__(self, k: str, v: str):
        self.k = k
        self.v = v

    def to_xml(self):
        """Generate XML representation of Tag object
        """
        return ET.Element('tag', {
            'k': self.k,
            'v': str(self.v)
        })

class Node:
    """Representation of an OSM Node entity
       See https://wiki.openstreetmap.org/wiki/Node
    """

    id : int = None
    """Node id"""

    lat : float = None
    """Node's latitude in degrees"""

    lon : float = None
    """Node's longitude in degrees"""

    tags : list[Tag] = None
    """Node's tags"""

    def __init__(self, id: int, lat: float, lon: float, tags:list[Tag]=None) -> None:
        if tags is None:
            tags = []
        self.id  = id
        self.lat = lat
        self.lon = lon
        self.tags = tags

    def __repr__(self) -> str:
        """String representation of the Node object
        """
        return f'Node(id={self.id}, lat={self.lat}, lon {self.lon})'

    def to_xml(self):
        """Generate XML representation of Node object
        """
        node = ET.Element('node', {
            'id': str(self.id),
            'lat': str(self.lat),
            'lon': str(self.lon)
        })
        for (k, v) in self.tags:
            node.append(Tag(k, v).to_xml())

        return node

class NodeRef:
    """Representation of an OSM NodeRef entity
    """
    ref : int = None

    def __init__(self, node: Node) -> None:
        self.ref = node.id

    def to_xml(self):
        """Generate XML representation of NodeRef object
        """
        return ET.Element('nd', {
            'ref': str(self.ref)
        })

class Way:
    """Representation of an OSM Way entity
       See https://wiki.openstreetmap.org/wiki/Way
    """

    id : int = None
    """Way id"""

    nodes : list[Node] = None
    """Ways' nodes"""

    tags : list[Tag] = None
    """Ways' tags"""

    def __init__(self, id: int, nodes: list[Node], tags: list[Tag]=None) -> None:
        if tags is None:
            tags = []
        self.id = id
        self.nodes = nodes
        self.tags = tags

    def to_xml(self):
        """Generate XML representation of Way object
        """
        way = ET.Element('way', {
            'id': str(self.id)
        })
        for node in self.nodes:
            way.append(NodeRef(node).to_xml())
        for (k, v) in self.tags:
            way.append(Tag(k, v).to_xml())

        return way
