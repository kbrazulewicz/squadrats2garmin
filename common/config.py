import json
import logging
import pathlib

from common.region import Region, RegionIndex
from common.zoom import Zoom, ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS

OUTPUT_PATH = pathlib.Path("output")

IMG_FAMILY_ID = 9724
IMG_MAPNAME_PREFIX_LENGTH = 5
IMG_FAMILY_NAME = "Squadrats2Garmin 2025"
IMG_SERIES_NAME = "Squadrats grid"

logger = logging.getLogger(__name__)

class Config:
    output: str
    description: str
    mapname_prefix: str
    regions: dict[Zoom, list[Region]]

    def __init__(self, config:dict, regions_14: list[Region], regions_17: list[Region]) -> None:
        self.output = config['output']
        self.description = config['description']
        if 'mapname_prefix' in config:
            self.mapname_prefix = config['mapname_prefix']
        else:
            self.mapname_prefix = str(IMG_FAMILY_ID).ljust(IMG_MAPNAME_PREFIX_LENGTH, '0')
        if len(self.mapname_prefix) > IMG_MAPNAME_PREFIX_LENGTH:
            raise ValueError(f'Mapname prefix "{self.mapname_prefix}" is too long')

        self.regions = {
            ZOOM_SQUADRATS: regions_14,
            ZOOM_SQUADRATINHOS: regions_17
        }

    @staticmethod
    def parse(filename: str, poly_index: RegionIndex) -> Config:
        logger.debug(f'Processing input job from "{filename}"')
        with open(filename) as configFile:
            config = json.load(configFile)

            regions_14: list[Region] = poly_index.select_regions(regions=config['zoom_14'])
            regions_17: list[Region] = poly_index.select_regions(regions=config['zoom_17'])

            return Config(config=config, regions_14=regions_14, regions_17=regions_17)