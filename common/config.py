"""Classes and methods to process input jobs
"""
import json
import logging
import pathlib
from abc import ABC

from common.region import Region, RegionIndex
from common.zoom import Zoom, ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS

OUTPUT_DIR = pathlib.Path("output")

# different family_id's to ensure no styles overlap
IMG_FAMILY_ID_SQUADRATS_GRID = '9724'
IMG_FAMILY_ID_VISITED_SQUADRATS = '9725'

_IMG_FAMILY_NAME = 'Squadrats2Garmin'
_IMG_PRODUCT_ID = '1'
_IMG_MAPNAME_PREFIX_LENGTH = 5

logger = logging.getLogger(__name__)

class Config(ABC):

    def __init__(self, config:dict) -> None:
        self._img_family_id = config['img_family_id']
        self._img_family_name = config['img_family_name'] if 'img_family_name' in config else _IMG_FAMILY_NAME
        self._img_product_id = _IMG_PRODUCT_ID
        self._img_series_name = config['series_name']
        self._description = config['description']
        self._output_dir = OUTPUT_DIR
        self._output = config['output']
        # relative to current working directory
        self._style_file = 'etc/squadrats-default.style'
        # relative to the self.output_dir
        self._typ_file = '../etc/squadrats.typ.txt'
        pass

    @property
    def output_dir(self) -> pathlib.Path:
        """mkgmap's output directory"""
        return self._output_dir

    @property
    def output(self) -> str:
        return self._output

    @property
    def description(self) -> str:
        return self._description

    @property
    def img_family_id(self) -> str:
        return self._img_family_id

    @property
    def img_family_name(self) -> str:
        return self._img_family_name

    @property
    def img_product_id(self) -> str:
        return self._img_product_id

    @property
    def img_series_name(self) -> str:
        return self._img_series_name

    @property
    def style_file(self) -> str:
        return self._style_file

    @property
    def typ_file(self) -> str:
        return self._typ_file


class RegionConfig(Config):
    """Representation of a single input job
    """
    mapname_prefix: str
    regions: dict[Zoom, list[Region]]

    def __init__(self, config:dict, regions_14: list[Region], regions_17: list[Region]) -> None:
        super().__init__(config=config)

        if 'mapname_prefix' in config:
            self.mapname_prefix = config['mapname_prefix']
        else:
            self.mapname_prefix = self.img_family_id.ljust(_IMG_MAPNAME_PREFIX_LENGTH, '0')
        if len(self.mapname_prefix) > _IMG_MAPNAME_PREFIX_LENGTH:
            raise ValueError(f'Mapname prefix "{self.mapname_prefix}" is too long')

        self.regions = {
            ZOOM_SQUADRATS: regions_14,
            ZOOM_SQUADRATINHOS: regions_17
        }

    @staticmethod
    def parse(filename: str, poly_index: RegionIndex) -> RegionConfig:
        """Parse input file and return a Config object
        """
        logger.debug('Processing input job from %s', filename)
        with open(filename, encoding='UTF-8') as config_file:
            config = json.load(config_file) | {
                'img_family_id': IMG_FAMILY_ID_SQUADRATS_GRID,
                'series_name': 'Squadrats grid'
            }

            regions_14: list[Region] = poly_index.select_regions(regions=config['zoom_14'])
            regions_17: list[Region] = poly_index.select_regions(regions=config['zoom_17'])

            return RegionConfig(config=config, regions_14=regions_14, regions_17=regions_17)


class VisitedSquadratsConfig(Config):
    def __init__(self, config:dict) -> None:
        config = {
            'description': 'Visited Squadrats',
            'series_name': 'Visited Squadrats'
        } | config
        super().__init__(config=config)
