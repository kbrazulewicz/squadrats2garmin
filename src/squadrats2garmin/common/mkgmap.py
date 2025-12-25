"""Classes and functions to provide interface to mkgmap tool

See https://www.mkgmap.org.uk/
"""
import importlib.resources
import json
import logging
import os
import pathlib
import subprocess
from abc import ABC
from importlib import resources

from squadrats2garmin.common.job import Job
from squadrats2garmin.common.region import Region, RegionIndex, Subdivision
from squadrats2garmin.common.tile import Zoom, ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS
from squadrats2garmin.common.timer import timeit

logger = logging.getLogger(__name__)

OUTPUT_DIR = pathlib.Path("output")

# different family_id's to ensure no styles overlap
IMG_FAMILY_ID_SQUADRATS_GRID = '9724'
IMG_FAMILY_ID_VISITED_SQUADRATS = '9725'

_IMG_FAMILY_NAME = 'Squadrats2Garmin'
_IMG_PRODUCT_ID = '1'
_IMG_MAPNAME_PREFIX_LENGTH = 5

class Config(ABC):

    def __init__(self, config:dict) -> None:
        self._img_family_id = config['img_family_id']
        self._img_family_name = config['img_family_name'] if 'img_family_name' in config else _IMG_FAMILY_NAME
        self._img_product_id = _IMG_PRODUCT_ID
        self._img_series_name = config['series_name']
        self._description = config['description']
        self._output_dir = config['output_dir'] if 'output_dir' in config else OUTPUT_DIR
        self._output = config['output']
        # relative to current working directory

        mkgmap_resources = resources.files("squadrats2garmin.config.mkgmap")
        with resources.as_file(mkgmap_resources.joinpath("squadrats-default.style")) as style_file:
            self._style_file = style_file.copy_into(self.output_dir)

        with resources.as_file(mkgmap_resources.joinpath("squadrats.typ.txt")) as typ_file:
            self._typ_file = typ_file.copy_into(self.output_dir)

    @property
    def output_dir(self) -> pathlib.Path:
        """mkgmap's output directory"""
        return self._output_dir

    @property
    def output(self) -> pathlib.Path:
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
    def style_file(self) -> pathlib.Path:
        return self._style_file

    @property
    def typ_file(self) -> pathlib.Path:
        return self._typ_file

    def write_mkgmap_config_headers(self, config_file) -> None:
        # images with 'unicode' encoding are not displayed on Garmin
        config_file.write('latin1\n')
        config_file.write('transparent\n')
        config_file.write(f'output-dir={self.output_dir}\n')

        config_file.write(f'family-id={self.img_family_id}\n')
        config_file.write(f'family-name={self.img_family_name}\n')
        config_file.write(f'product-id={self.img_product_id}\n')
        config_file.write(f'series-name={self.img_series_name}\n')

        # style contains instructions for filtering elements, so it needs to go before any map file
        config_file.write(f'style-file={str(self.style_file)}\n')

    def move_output_file_to_final_location(self) -> pathlib.Path:
        gmapsupp_img = self.output_dir / 'gmapsupp.img'

        logger.debug(f'Moving {gmapsupp_img} to {self.output}')

        if not gmapsupp_img.exists():
            raise RuntimeError(f'{gmapsupp_img} not found')

        self.output.parent.mkdir(parents=True, exist_ok=True)
        gmapsupp_img.move(self.output)

        return self.output


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
    def __init__(self, config: dict, osm_path: pathlib.Path) -> None:
        """
        Create VisitedSquadratsConfig object
        :param config:
        :param osm_path: path to the input OSM file
        """
        config = {
            'description': 'Visited Squadrats',
            'series_name': 'Visited Squadrats'
        } | config
        super().__init__(config=config)
        self._osm_path = osm_path

    @property
    def osm_path(self) -> pathlib.Path:
        return self._osm_path

    def write_mkgmap_config(self, config_path: pathlib.Path) -> None:
        """Generate mkgmap config file
        """
        with config_path.open('w', encoding='UTF-8') as config_file:
            self.write_mkgmap_config_headers(config_file)

            config_file.write(f'mapname={self.img_family_id}0001\n')
            config_file.write(f'description={self.description}\n')
            config_file.write(f'input-file={self.osm_path.relative_to(self.output_dir)}\n')

            config_file.write(f'input-file={self.typ_file.relative_to(self.output_dir)}\n')
            config_file.write(f'description={self.description}\n')
            config_file.write("gmapsupp\n")


def generate_mkgmap_config(output: pathlib.Path, config: RegionConfig, jobs: list[Job]):
    """Generate mkgmap config file
    """
    with output.open('w', encoding='UTF-8') as config_file:
        config.write_mkgmap_config_headers(config_file)

        sequence_number = 1
        for job in jobs:
            # mapname_prefix is 5 characters long, and we're adding 3 digits of a sequence number
            if sequence_number > 999:
                raise ValueError("Too many mapfiles to merge")
            config_file.write(f'mapname={config.mapname_prefix}{sequence_number:03d}\n')
            config_file.write(f'country-name={job.region.get_country_name()}\n')
            config_file.write(f'country-abbr={job.region.get_country_code()}\n')
            if isinstance(job.region, Subdivision):
                config_file.write(f'region-name={job.region.name}\n')
                config_file.write(f'region-abbr={job.region.code}\n')

            description = (f'{job.region.name} @{job.zoom.zoom}'
                           # country name replacements
                           .replace(", Republic of", "")
                           .replace("Bosnia and Herzegovina", "BiH")
                           # region name replacements
                           .replace(", Unitatea teritorială autonomă (UTAG)", "")
                           .replace(", unitatea teritorială din", "")
                           )
            config_file.write(f'description={description}\n')
            config_file.write(f'input-file={job.osm_file.relative_to(config.output_dir)}\n')

            sequence_number += 1

        config_file.write(f'input-file={config.typ_file.relative_to(config.output_dir)}\n')

        config_file.write(f'description={config.description}\n')
        config_file.write("gmapsupp\n")

def run_mkgmap(config_path: pathlib.Path):
    with timeit(msg=f'Running mkgmap --read-config={config_path}'):
        result = subprocess.run(
            ['mkgmap', f'--read-config={str(config_path)}'],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise RuntimeError(f'mkgmap failed: {result.stderr}')


def generate_garmin_img(config: RegionConfig, jobs: list[Job]):
    """Generate a single Garmin IMG file from multiple jobs"""
    # generate mkgmap config file
    config_path = config.output_dir / 'mkgmap.conf'
    generate_mkgmap_config(output=config_path, config=config, jobs=jobs)

    # generate Garmin IMG file
    logger.info('Creating Garmin IMG file %s', config.output)
    run_mkgmap(config_path=config_path)

    config.move_output_file_to_final_location()