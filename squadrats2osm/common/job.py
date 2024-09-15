from common.id import Id
from common.zoom import Zoom

class Job:
    """Representation of the job context
    """
    name: str
    zoom: Zoom

    _id: Id
    
    def __init__(self, name: str, zoom: Zoom) -> None:
        self.name = name
        self.zoom = zoom
        self._id = Id()

    def nextId(self) -> int:
        return self._id.next_id()