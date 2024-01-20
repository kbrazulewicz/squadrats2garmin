from common.zoom import Zoom

class Job:
    """Representation of the job context
    """
    id: str
    zoom: Zoom
    
    def __init__(self, id: str, zoom: Zoom) -> None:
        self.id = id
        self.zoom = zoom