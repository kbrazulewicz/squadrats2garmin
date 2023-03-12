import xml.etree.ElementTree as ET

# all squadratinhos
# 4^17 = 17 179 869 184
NODE_BASE_ID = 100000000000

WAY_BASE_ID  = 200000000000

class Tag:
    def __init__(self, k: str, v: str):
        self.k = k
        self.v = v

    def to_xml(self):
        return ET.Element('tag', {
            'k': self.k,
            'v': self.v
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