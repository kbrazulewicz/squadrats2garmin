import xml.etree.ElementTree as ET

# all squadratinhos
# 4^17 = 17 179 869 184
WAY_BASE_ID  = 100000000000

class Tag:
    def __init__(self, k: str, v: str):
        self.k = k
        self.v = v

    def to_xml(self):
        return ET.Element('tag', {
            'k': self.k,
            'v': str(self.v)
        })

class Node:
    """Representation of a OSM Node entity
       See https://wiki.openstreetmap.org/wiki/Node
    """

    id : int = None
    """Node id"""

    lat : float = None
    """Node's latitude in degrees"""

    lon : float = None
    """Node's longitude in degrees"""

    tags : list = None
    """Node's tags"""

    def __init__(self, id: int, lat: float, lon: float, tags: list = []) -> None:
        self.id  = id
        self.lat = lat
        self.lon = lon
        self.tags = tags

    def __repr__(self) -> str:
        """String representation of the Node object
        """
        return 'Node(id {}; lat {}; lon {})'.format(self.id, self.lat, self.lon)

    def to_xml(self):
        node = ET.Element('node', {
            'id': str(self.id),
            'lat': str(self.lat),
            'lon': str(self.lon)
        })
        for (k, v) in self.tags:
            node.append(Tag(k, v).to_xml())

        return node
    
class NodeRef:
    ref : int = None

    def __init__(self, node: Node) -> None:
        self.ref = node.id

    def to_xml(self):
        return ET.Element('nd', {
            'ref': str(self.ref)
        })

class Way:
    """Representation of a OSM Way entity
       See https://wiki.openstreetmap.org/wiki/Way
    """

    id : int = None
    """Way id"""

    nodes : list[Node] = None
    """Ways' nodes"""

    tags : list[Tag] = None
    """Ways' tags"""

    def __init__(self, id: int, nodes: list[Node], tags: list[Tag] = []) -> None:
        self.id = id
        self.nodes = nodes
        self.tags = tags

    def to_xml(self):
        way = ET.Element('way', {
            'id': str(self.id)
        })
        for (node) in self.nodes:
            way.append(NodeRef(node).to_xml())
        for (k, v) in self.tags:
            way.append(Tag(k, v).to_xml())

        return way
