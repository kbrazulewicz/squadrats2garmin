"""Functions to provide interface to mkgmap tool

See https://www.mkgmap.org.uk/
"""
import logging
import os
import pathlib
import subprocess

from common.config import Config, OUTPUT_PATH, IMG_FAMILY_ID, IMG_FAMILY_NAME, IMG_SERIES_NAME
from common.job import Job
from common.region import Subdivision

logger = logging.getLogger(__name__)


def generate_mkgmap_config(output: pathlib.Path, config: Config, jobs: list[Job]):
    """Generate mkgmap config file
    """
    with output.open('w', encoding='UTF-8') as config_file:
        # images with 'unicode' encoding are not displayed on Garmin
        config_file.write('latin1\n')
        config_file.write('transparent\n')
        config_file.write(f'output-dir={OUTPUT_PATH.name}\n')

        config_file.write(f'family-id={IMG_FAMILY_ID}\n')
        config_file.write(f'family-name={IMG_FAMILY_NAME}\n')
        config_file.write('product-id=1\n')
        config_file.write(f'series-name={IMG_SERIES_NAME}\n')

        config_file.write('style-file=etc/squadrats-default.style\n')

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
            config_file.write(f'input-file={job.osm_file.relative_to(OUTPUT_PATH)}\n')

            sequence_number += 1

        config_file.write("input-file=../etc/squadrats.typ.txt\n")

        config_file.write(f'description={config.description}\n')
        config_file.write("gmapsupp\n")

def run_mkgmap(config: pathlib.Path):
    result = subprocess.run(
        ['mkgmap', f'--read-config={str(config)}'],
        cwd=os.getcwd(),
        capture_output=True,
        text=True,
        check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f'mkgmap failed: {result.stderr}')


def generate_garmin_img(config: Config, jobs: list[Job]):
    """Generate a single Garmin IMG file from multiple jobs"""
    # generate mkgmap config file
    mkgmap_config = OUTPUT_PATH / 'mkgmap.conf'
    generate_mkgmap_config(output=mkgmap_config, config=config, jobs=jobs)

    # generate Garmin IMG file
    logger.info('Creating Garmin IMG file %s', config.output)
    run_mkgmap(config=mkgmap_config)

    gmapsupp_img = OUTPUT_PATH / 'gmapsupp.img'
    if not gmapsupp_img.exists():
        raise RuntimeError('gmapsupp.img not found')

    gmapsupp_img.move(config.output)
