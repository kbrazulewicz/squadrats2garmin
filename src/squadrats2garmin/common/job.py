"""Classes and methods for creating a job context for a single region
"""
import itertools
from pathlib import Path
from typing import Iterator

from squadrats2garmin.common.region import Region
from squadrats2garmin.common.tile import Zoom

class Job:
    """Representation of the job context
    """

    def __init__(self, region: Region, zoom: Zoom, osm_file: Path) -> None:
        self.region: Region = region
        self.zoom: Zoom = zoom
        self.osm_file: Path = osm_file
        self._id: Iterator[int] = itertools.count(start=-1, step=-1)

    def __str__(self) -> str:
        return f"{self.region.code}@{self.zoom.zoom}"

    def next_id(self) -> int:
        """Generate id for the next OSM element
        """
        return next(self._id)
