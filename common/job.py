"""Classes and methods for creating a job context for a single region
"""
import pathlib

from common.id import Id
from common.region import Region
from common.zoom import Zoom

class Job:
    """Representation of the job context
    """
    region: Region
    zoom: Zoom
    osm_file: pathlib.Path

    _id: Id

    def __init__(self, region: Region, zoom: Zoom, osm_file: pathlib.Path) -> None:
        self.region = region
        self.zoom = zoom
        self.osm_file = osm_file
        self._id = Id()

    def __str__(self) -> str:
        return f'{self.region.iso_code}@{self.zoom.zoom}'

    def next_id(self) -> int:
        """Generate id for the next OSM element
        """
        return self._id.next_id()
