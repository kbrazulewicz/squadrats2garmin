"""Functions to provide interface to mkgmap tool

See https://www.mkgmap.org.uk/
"""
import logging
import os
import pathlib
import subprocess

from common.config import RegionConfig, Config
from common.job import Job
from common.region import Subdivision
from common.timer import timeit

logger = logging.getLogger(__name__)


def write_mkgmap_config_headers(file, config: Config) -> None:
    # images with 'unicode' encoding are not displayed on Garmin
    file.write('latin1\n')
    file.write('transparent\n')
    file.write(f'output-dir={config.output_dir.name}\n')

    file.write(f'family-id={config.img_family_id}\n')
    file.write(f'family-name={config.img_family_name}\n')
    file.write(f'product-id={config.img_product_id}\n')
    file.write(f'series-name={config.img_series_name}\n')

    # style contains instructions for filtering elements, so it needs to go before any map file
    file.write(f'style-file={config.style_file}\n')


def generate_mkgmap_config(output: pathlib.Path, config: RegionConfig, jobs: list[Job]):
    """Generate mkgmap config file
    """
    with output.open('w', encoding='UTF-8') as config_file:
        write_mkgmap_config_headers(file=config_file, config=config)

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

        config_file.write(f'input-file={config.typ_file}\n')

        config_file.write(f'description={config.description}\n')
        config_file.write("gmapsupp\n")

def run_mkgmap(config: pathlib.Path):
    with timeit(msg=f'Running mkgmap --read-config={config}'):
        result = subprocess.run(
            ['mkgmap', f'--read-config={str(config)}'],
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
    mkgmap_config = config.output_dir / 'mkgmap.conf'
    generate_mkgmap_config(output=mkgmap_config, config=config, jobs=jobs)

    # generate Garmin IMG file
    logger.info('Creating Garmin IMG file %s', config.output)
    run_mkgmap(config=mkgmap_config)

    gmapsupp_img = config.output_dir / 'gmapsupp.img'
    if not gmapsupp_img.exists():
        raise RuntimeError('gmapsupp.img not found')

    pathlib.Path(config.output).parent.mkdir(parents=True, exist_ok=True)
    gmapsupp_img.move(config.output)
